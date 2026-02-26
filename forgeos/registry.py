class ModuleRegistry:
    def __init__(self):
        self._modules = {}

    def register(self, module):
        self._modules[module.schema.name] = module

    def get(self, name):
        return self._modules.get(name)

    def list_modules(self):
        return {
            name: module.lifecycle.to_dict()
            for name, module in self._modules.items()
        }

    def exists(self, name):
        return name in self._modules