from .module import ForgeModule
from .schema import ForgeModuleSchema
from .lifecycle import ModuleState
from .registry import ModuleRegistry
from .dependency import DependencyGraph
from .builder.django import DjangoBuilder
from .repair import RepairEngine
from core.models import ForgeModuleRecord


class ForgeEngine:

    def __init__(self):
        self.registry = ModuleRegistry()
        self.dependency_graph = DependencyGraph()
        self.builder = DjangoBuilder()
        self.repair_engine = RepairEngine()   # ✅ 一定要在 __init__ 裡面

    def build_module(self, schema_data: dict) -> ForgeModule:
        schema = ForgeModuleSchema(**schema_data)
        module = ForgeModule(schema)

        # 🔥 Generate + Repair Hook
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

        # 🔥 Builder 執行
        self.builder.build(module)

        # 🔥 依賴圖
        self.dependency_graph.add_module(
            module.schema.name,
            module.schema.dependencies
        )

        self.dependency_graph.validate()

        module.deploy()
        self.registry.register(module)

        # 🔥 存進 DB
        ForgeModuleRecord.objects.update_or_create(
            name=module.schema.name,
            defaults={"state": module.lifecycle.get_state().value}
        )

        return module

    def list_modules(self):
        return self.registry.list_modules()

    def get_dependency_graph(self):
        return self.dependency_graph.get_graph()