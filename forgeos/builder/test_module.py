from forgeos.module import ForgeModule

class TestModule(ForgeModule):
    name = "auto_test"

    def register_services(self):
        def hello(**kwargs):
            return "hello world"
        return {"hello": hello}