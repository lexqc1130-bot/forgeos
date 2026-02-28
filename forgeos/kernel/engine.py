from typing import Any

from .module import ForgeModule
from .schema import ForgeModuleSchema
from .lifecycle import ModuleState
from forgeos.registry.service import ModuleRegistry
from .dependency import DependencyGraph
from forgeos.governance.repair import RepairEngine
from forgeos.runtime.execution_context import ExecutionContext
from core.models import ForgeModuleRecord
import time
from forgeos.governance.cost_tracker import record_event
import signal

class ServiceTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise ServiceTimeout("Service execution timed out")

class ForgeEngine:

    def __init__(self, org_id: str = "default_org"):
        self.org_id = org_id
        self.registry = ModuleRegistry(org_id=self.org_id)
        self.dependency_graph = DependencyGraph()
        self.repair_engine = RepairEngine()

        # Runtime in-memory module cache
        self._runtime_modules = {}

    # ----------------------------
    # Build Phase
    # ----------------------------

    def build_module(self, schema_data: dict) -> ForgeModule:
        schema = ForgeModuleSchema(**schema_data)
        module = ForgeModule(schema)

        try:
            module.generate()
        except Exception as e:
            module.lifecycle.transition(ModuleState.FAILED)
            try:
                module = self.repair_engine.repair(module, e)
            except Exception:
                raise Exception("Module generation failed after repair limit")

        if module.lifecycle.get_state() == ModuleState.FAILED:
            raise Exception("Module generation failed after repair")

        module.validate()

        self.dependency_graph.add_module(
            module.schema.name,
            module.schema.dependencies
        )
        self.dependency_graph.validate()

        module.deploy()

        # Persist
        self.registry.register(module)

        ForgeModuleRecord.objects.update_or_create(
            name=module.schema.name,
            defaults={"state": module.lifecycle.get_state().value}
        )

        # Cache for runtime execution
        self._runtime_modules[module.schema.name] = module

        return module

    # ----------------------------
    # Activation Layer
    # ----------------------------

    def activate_module(self, module_name: str):
        self.registry.activate(module_name)

    def deactivate_module(self, module_name: str):
        self.registry.deactivate(module_name)

    def get_active_modules(self):
        return self.registry.get_active_modules()

    def list_modules(self):
        return self.registry.list_modules()

    def get_dependency_graph(self):
        return self.dependency_graph.get_graph()

    # ----------------------------
    # Execution Kernel
    # ----------------------------

    def execute(self, service_name: str, context: ExecutionContext) -> Any:
        active_records = self.registry.get_active_modules()
        candidate_modules = []

        for record in active_records:
            module = self._runtime_modules.get(record.name)
            if not module:
                continue

            services = module.get_wrapped_services()

            if service_name in services:
                candidate_modules.append((module, services[service_name]))

        if not candidate_modules:
            raise Exception(f"No active module provides service '{service_name}'")

        selected_module, selected_service = candidate_modules[0]

        start_time = time.time()

        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(5)

        try:
            result = selected_service(
                org_id=context.org_id,
                **context.payload
            )

            execution_time = time.time() - start_time

            record_event(
                org_id=context.org_id,
                module_name=selected_module.schema.name,
                event_type="execution_success",
                execution_time=execution_time,
            )

            return result

        except ServiceTimeout:
            execution_time = time.time() - start_time

            record_event(
                org_id=context.org_id,
                module_name=selected_module.schema.name,
                event_type="execution_timeout",
                execution_time=execution_time,
            )

            raise

        except Exception as e:
            execution_time = time.time() - start_time

            record_event(
                org_id=context.org_id,
                module_name=selected_module.schema.name,
                event_type="execution_failure",
                execution_time=execution_time,
                metadata={"error": str(e)}
            )

            raise

        finally:
            signal.alarm(0)