from typing import Any
import time
import signal

from django.db.models import F

from .module import ForgeModule
from .schema import ForgeModuleSchema
from .lifecycle import ModuleState
from forgeos.registry.service import ModuleRegistry
from .dependency import DependencyGraph
from forgeos.governance.repair import RepairEngine
from forgeos.runtime.execution_context import ExecutionContext
from core.models import ForgeModuleRecord
from forgeos.governance.cost_tracker import record_event
from forgeos.runtime.sandbox import SandboxExecutor
from forgeos.governance.models import Organization, TokenUsage  # 🔥 只新增 TokenUsage


class ServiceTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise ServiceTimeout("Service execution timed out")


class ForgeEngine:

    def __init__(self, org_id: str):

        if not org_id:
            raise ValueError("org_id is required")

        self.organization = Organization.objects.get(org_id=org_id)
        self.org_id = self.organization.org_id

        self.registry = ModuleRegistry(org_id=self.org_id)
        self.dependency_graph = DependencyGraph()
        self.repair_engine = RepairEngine()

        self._runtime_modules = {}
        self.sandbox = SandboxExecutor(timeout=2)

    # ----------------------------
    # Build Phase
    # ----------------------------

    def build_module(self, schema_data: dict) -> ForgeModule:

        schema = ForgeModuleSchema(**schema_data)
        module = ForgeModule(schema)

        module.organization = self.organization

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

        self.registry.register(module)

        ForgeModuleRecord.objects.update_or_create(
            name=module.schema.name,
            defaults={"state": module.lifecycle.get_state().value}
        )

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
    # Execution Kernel (Quota Enabled)
    # ----------------------------

    def execute(self, service_name: str, context: ExecutionContext) -> Any:

        if self.organization.current_month_tokens >= self.organization.monthly_token_quota:
            raise Exception("Monthly token quota exceeded")

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

        RATE_PER_SECOND = 0.01

        max_attempts = context.retry_count + 1
        attempt = 0
        last_exception = None

        while attempt < max_attempts:

            attempt += 1
            start_time = time.time()

            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(5)

            try:

                payload = {"org_id": self.org_id, **context.payload}

                result = self.sandbox.run(
                    selected_service,
                    payload
                )

                execution_time = time.time() - start_time
                cost_amount = execution_time * RATE_PER_SECOND

                tokens_used = max(1, int(cost_amount * 100))

                # 🔥 原子更新（保持你原本邏輯）
                Organization.objects.filter(
                    pk=self.organization.pk
                ).update(
                    current_month_tokens=F("current_month_tokens") + tokens_used
                )

                self.organization.refresh_from_db()

                # 🔥 新增：Execution TokenUsage（不動既有功能）
                TokenUsage.objects.create(
                    organization=self.organization,
                    source="execution",
                    tokens_used=tokens_used
                )

                record_event(
                    org_id=self.org_id,
                    module_name=selected_module.schema.name,
                    event_type="execution_success",
                    execution_time=execution_time,
                    metadata={
                        "attempt": attempt,
                        "tokens_used": tokens_used
                    },
                    cost_amount=cost_amount
                )

                return result

            except ServiceTimeout as e:

                last_exception = e
                execution_time = time.time() - start_time
                cost_amount = execution_time * RATE_PER_SECOND

                event_type = (
                    "execution_retry"
                    if attempt < max_attempts
                    else "execution_failure"
                )

                record_event(
                    org_id=self.org_id,
                    module_name=selected_module.schema.name,
                    event_type=event_type,
                    execution_time=execution_time,
                    metadata={
                        "attempt": attempt,
                        "reason": "timeout"
                    },
                    cost_amount=cost_amount
                )

            except Exception as e:

                last_exception = e
                execution_time = time.time() - start_time
                cost_amount = execution_time * RATE_PER_SECOND

                event_type = (
                    "execution_retry"
                    if attempt < max_attempts
                    else "execution_failure"
                )

                record_event(
                    org_id=self.org_id,
                    module_name=selected_module.schema.name,
                    event_type=event_type,
                    execution_time=execution_time,
                    metadata={
                        "attempt": attempt,
                        "error": str(e)
                    },
                    cost_amount=cost_amount
                )

            finally:
                signal.alarm(0)

            if attempt < max_attempts and context.retry_delay > 0:
                delay = context.retry_delay * (
                    context.backoff_multiplier ** (attempt - 1)
                )
                time.sleep(delay)

        raise last_exception