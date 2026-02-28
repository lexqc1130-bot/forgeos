from django.http import JsonResponse
from forgeos.kernerl.engine import ForgeEngine

engine = ForgeEngine()


def test_forgeos(request):

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

    return JsonResponse({
        "built_module": module.schema.name,
        "all_modules": engine.list_modules()
    })