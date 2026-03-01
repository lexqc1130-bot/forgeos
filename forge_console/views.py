from django.shortcuts import render
from django.http import JsonResponse
from forgeos.kernel.engine import ForgeEngine
from django.views.decorators.csrf import csrf_exempt
from forgeos.runtime.execution_context import ExecutionContext
import json
import inspect

def console_home(request):
    return render(request, "forge_console/console_home.html")

def api_modules(request):
    engine = ForgeEngine(org_id="default_org")

    modules = engine.list_modules()
    active_modules = engine.get_active_modules()

    active_names = {m.name for m in active_modules}

    module_list = []

    for m in modules:
        runtime_state = "ACTIVE" if m.name in active_names else m.state

        module_list.append({
            "name": m.name,
            "state": runtime_state
        })

    return JsonResponse({"modules": module_list})

@csrf_exempt
def api_create_module(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    engine = ForgeEngine(org_id="default_org")

    module = engine.build_module(data)

    return JsonResponse({
        "message": "Module created",
        "module": module.schema.name
    })

@csrf_exempt
def api_activate_module(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    module_name = data.get("name")

    engine = ForgeEngine(org_id="default_org")
    engine.activate_module(module_name)

    return JsonResponse({"message": "Module activated"})


@csrf_exempt
def api_deactivate_module(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    module_name = data.get("name")

    engine = ForgeEngine(org_id="default_org")
    engine.deactivate_module(module_name)

    return JsonResponse({"message": "Module deactivated"})

def api_token_usage(request):
    engine = ForgeEngine(org_id="default_org")
    org = engine.organization

    return JsonResponse({
        "org_id": org.org_id,
        "current_tokens": org.current_month_tokens,
        "quota": org.monthly_token_quota,
        "remaining": org.monthly_token_quota - org.current_month_tokens
    })

@csrf_exempt
def api_execute_module(request):

    try:
        org_id = request.GET.get("org")

        if not org_id:
            return JsonResponse({
                "status": "error",
                "message": "org is required"
            })

        data = json.loads(request.body)

        module_name = data.get("name")
        payload = data.get("payload", {})

        engine = ForgeEngine(org_id)

        # 🔥 確保 module 被 activate
        engine.activate_module(module_name)

        context = ExecutionContext(
            org_id=org_id,
            payload=payload,
            retry_count=0,
            retry_delay=0,
            backoff_multiplier=1
        )

        result = engine.execute("run", context)

        return JsonResponse({
            "status": "success",
            "result": result
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })
    
def api_module_signature(request, name):

    org_id = request.GET.get("org", "default_org")
    engine = ForgeEngine(org_id)

    module = engine._runtime_modules.get(name)

    if not module:
        return JsonResponse({"error": "Module not found"}, status=404)

    services = module.get_wrapped_services()

    if "run" not in services:
        return JsonResponse({"error": "No run service"}, status=400)

    raw_service = module.services["run"]
    sig = inspect.signature(raw_service)

    parameters = []

    for param in sig.parameters.values():
        if param.name in ["org_id", "kwargs"]:
            continue

        parameters.append({
            "name": param.name,
            "annotation": str(param.annotation)
        })

    return JsonResponse({
        "service": "run",
        "parameters": parameters
    })