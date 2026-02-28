class ContextEnhancer:

    def enhance(self, module, error_type):
        context = {
            "module_name": module.schema.name,
            "module_type": module.schema.type,
            "dependencies": module.schema.dependencies,
            "error_type": error_type,
        }

        # 未來可以加入：
        # - 之前生成的程式碼
        # - 錯誤 traceback
        # - LLM prompt injection

        return context