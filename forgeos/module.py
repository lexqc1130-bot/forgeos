from .lifecycle import ModuleLifecycle, ModuleState
from .schema import ForgeModuleSchema


class ForgeModule:

    def __init__(self, schema: ForgeModuleSchema):
        self.schema = schema
        self.lifecycle = ModuleLifecycle()

        # 🔥 新增控制欄位
        self.retry_count = 0
        self.max_retries = 2
        self.repair_log = []

    def generate(self):
        # 🔥 故意製造錯誤來測試 Repair Pipeline
        raise Exception("SyntaxError: invalid syntax")
        try:
            self.schema.validate()

            # ⚠️ 這裡先保留正常版本
            self.lifecycle.transition(ModuleState.GENERATED)

        except Exception as e:
            self.lifecycle.transition(ModuleState.FAILED)
            raise e

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