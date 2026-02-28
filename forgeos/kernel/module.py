from .lifecycle import ModuleLifecycle, ModuleState
from .schema import ForgeModuleSchema
import time
from functools import wraps
from forgeos.governance.cost_tracker import record_event
from forgeos.ai.llm_provider import get_llm_provider
import ast


class ForgeModule:

    def __init__(self, schema: ForgeModuleSchema):
        self.schema = schema
        self.lifecycle = ModuleLifecycle()

        # 🔥 Retry 控制
        self.retry_count = 0
        self.max_retries = 2
        self.repair_log = []

        # 🔥 Generation Loop 控制
        self.generation_attempts = 0
        self.total_tokens_used = 0
        self.max_generation_iterations = 3
        self.generation_log = []

    # =====================================================
    # 🔐 安全安裝服務
    # =====================================================
    def install_services(self, code: str):

        safe_globals = {
            "__builtins__": {
                "len": len,
                "range": range,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "isinstance": isinstance,
            }
        }

        namespace = {}

        exec(code, safe_globals, namespace)

        if "run" not in namespace:
            raise Exception("Generated code must define function 'run'")

        self.services = {
            "run": namespace["run"]
        }

    # =====================================================
    # 🔁 Generation Loop（自動驗證 + 修復）
    # =====================================================
    def generate(self):

        # 每次 generate 重置狀態
        self.generation_attempts = 0
        self.total_tokens_used = 0
        self.generation_log = []

        llm = get_llm_provider()

        last_error = None
        code = None

        while self.generation_attempts < self.max_generation_iterations:

            self.generation_attempts += 1

            # --- 產生或修復 ---
            if last_error:
                result = llm.repair_code(
                    previous_code=code,
                    error=last_error
                )
            else:
                result = llm.generate_code(self.schema.name)

            # --- 支援回傳 1 或 2 個值 ---
            if isinstance(result, tuple):
                raw_code, tokens = result
            else:
                raw_code = result
                tokens = 0

            self.total_tokens_used += tokens

            # 🔥 清理 markdown code block
            code = self.clean_code(raw_code)

            try:
                self.validate_code_structure(code)
                self.install_services(code)

                self.generation_log.append({
                    "attempt": self.generation_attempts,
                    "status": "success",
                    "tokens": tokens,
                    "raw_output": raw_code,
                    "clean_code": code
                })

                return

            except Exception as e:

                last_error = str(e)

                self.generation_log.append({
                    "attempt": self.generation_attempts,
                    "status": "failed",
                    "error": last_error,
                    "tokens": tokens,
                    "raw_output": raw_code,
                    "clean_code": code
                })

        raise Exception(
            f"Module generation failed after {self.max_generation_iterations} attempts"
        )

    # =====================================================
    # 🔍 AST 靜態驗證
    # =====================================================
    def validate_code_structure(self, code: str):

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise Exception(f"Syntax error in generated code: {e}")

        function_defs = []

        for node in ast.walk(tree):

            # ❌ 禁止 import
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise Exception("Import statements are not allowed")

            # ❌ 禁止 class
            if isinstance(node, ast.ClassDef):
                raise Exception("Class definitions are not allowed")

            # ❌ 禁止 lambda
            if isinstance(node, ast.Lambda):
                raise Exception("Lambda expressions are not allowed")

            # ❌ 禁止 global
            if isinstance(node, ast.Global):
                raise Exception("Global statements are not allowed")

            # ❌ 禁止 exec / eval / __import__
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["exec", "eval", "__import__"]:
                        raise Exception(f"{node.func.id} is not allowed")

            if isinstance(node, ast.FunctionDef):
                function_defs.append(node)

        if len(function_defs) != 1:
            raise Exception("Generated code must define exactly one function")

        if function_defs[0].name != "run":
            raise Exception("Function name must be 'run'")

    # =====================================================
    # 🧹 清理 Markdown Code Block
    # =====================================================
    def clean_code(self, code: str) -> str:

        code = code.strip()

        # 如果包含 markdown block
        if code.startswith("```"):
            lines = code.splitlines()

            # 移除第一行 ```python 或 ```
            first_line = lines[0].strip()
            if first_line.startswith("```"):
                lines = lines[1:]

            # 移除最後一行 ```
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]

            code = "\n".join(lines)

        return code.strip()

    # =====================================================
    # Lifecycle
    # =====================================================
    def validate(self):
        self.lifecycle.transition(ModuleState.VALIDATED)

    def deploy(self):
        self.lifecycle.transition(ModuleState.DEPLOYED)

    # =====================================================
    # Retry
    # =====================================================
    def log_repair(self, error_type, context):
        self.repair_log.append({
            "attempt": self.retry_count,
            "error_type": error_type,
            "context": context
        })

    def can_retry(self):
        return self.retry_count < self.max_retries

    name = "base_module"

    # =====================================================
    # Service Wrapper
    # =====================================================
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
        return {}

    def get_wrapped_services(self):
        services = getattr(self, "services", {})
        wrapped = {}

        for name, func in services.items():
            wrapped[name] = self.wrap_service(func)

        return wrapped