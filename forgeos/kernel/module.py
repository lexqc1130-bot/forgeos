from .lifecycle import ModuleLifecycle, ModuleState
from .schema import ForgeModuleSchema
import time
from functools import wraps
from forgeos.governance.cost_tracker import record_event
from forgeos.ai.llm_provider import get_llm_provider

class ForgeModule:

    def __init__(self, schema: ForgeModuleSchema):
        self.schema = schema
        self.lifecycle = ModuleLifecycle()

        # 🔥 新增控制欄位
        self.retry_count = 0
        self.max_retries = 2
        self.repair_log = []

    def generate(self):

        llm = get_llm_provider()
        raw_code = llm.generate_code(self.schema.name)

        code = raw_code.strip()

        # 🔥 移除 markdown code block
        if code.startswith("```"):
            code = code.replace("```python", "")
            code = code.replace("```", "")
            code = code.strip()

        namespace = {}

        try:
            exec(code, {}, namespace)
        except Exception as e:
            raise Exception(f"Code execution failed: {str(e)}")

        if "run" not in namespace:
            raise Exception("Generated code must define function 'run'")

        self.services = {
            "run": namespace["run"]
        }

    def validate(self):
        self.lifecycle.transition(ModuleState.VALIDATED)

    def deploy(self):
        self.lifecycle.transition(ModuleState.DEPLOYED)

    def log_repair(self, error_type, context):
        self.repair_log.append({
            "attempt": self.retry_count,
            "error_type": error_type,
            "context": context
        })

    def can_retry(self):
        return self.retry_count < self.max_retries
    
    name = "base_module"

    def wrap_service(self, service_func):

        @wraps(service_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            result = None

            try:
                result = service_func(*args, **kwargs)
                return result

            except Exception as e:
                error = str(e)
                raise e

            finally:
                execution_time = time.time() - start_time

                record_event(
                    org_id=kwargs.get("org_id", "unknown_org"),
                    module_name=self.name,
                    event_type=service_func.__name__,
                    token_used=kwargs.get("token_used", 0),
                    execution_time=execution_time,
                    metadata={
                        "error": error,
                        "lifecycle_state": self.lifecycle.state.name
                    }
                )

        return wrapper

    def register_services(self):
        """
        Child modules should override this.
        Must return dict of services.
        """
        return {}

    def get_wrapped_services(self):
        """
        Return auto-wrapped services.
        """
        services = getattr(self, "services", {})
        wrapped = {}

        for name, func in services.items():
            wrapped[name] = self.wrap_service(func)

        return wrapped