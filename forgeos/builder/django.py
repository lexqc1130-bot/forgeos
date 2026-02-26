from .base import BaseBuilder


class DjangoBuilder(BaseBuilder):

    def build(self, module):
        # 未來寫實際產生 Django app
        print(f"Building Django module: {module.schema.name}")