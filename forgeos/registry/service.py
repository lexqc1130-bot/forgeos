from forgeos.registry.models import ModuleRecord


class ModuleRegistry:

    def __init__(self, org_id: str):
        self.org_id = org_id

    def register(self, module):
        ModuleRecord.objects.update_or_create(
            org_id=self.org_id,
            name=module.schema.name,
            version="v1",
            defaults={
                "state": module.lifecycle.get_state().value,
                "schema_json": module.schema.__dict__,
            }
        )

    def activate(self, module_name: str):
        ModuleRecord.objects.filter(
            org_id=self.org_id,
            name=module_name
        ).update(is_active=True)

    def deactivate(self, module_name: str):
        ModuleRecord.objects.filter(
            org_id=self.org_id,
            name=module_name
        ).update(is_active=False)

    def get_active_modules(self):
        return ModuleRecord.objects.filter(
            org_id=self.org_id,
            is_active=True
        )

    def list_modules(self):
        return ModuleRecord.objects.filter(
            org_id=self.org_id
        )