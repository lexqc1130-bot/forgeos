from django.http import JsonResponse
from forgeos.kernel.engine import ForgeEngine


def test_forgeos(request):
    engine = ForgeEngine(org_id="default_org")

    schema_data = {
        "name": "dashboard",
        "type": "web_component",
        "inputs": [],
        "outputs": [],
        "dependencies": [],
        "permissions": [],
        "config_schema": {}
    }

    module = engine.build_module(schema_data)

    modules = engine.list_modules()

    # 🔥 把 QuerySet 轉成 list
    module_list = [
        {
            "name": m.name,
            "state": m.state
        }
        for m in modules
    ]

    return JsonResponse({
        "built_module": module.schema.name,
        "all_modules": module_list
    })