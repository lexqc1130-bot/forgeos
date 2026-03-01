from django.urls import path
from . import views

urlpatterns = [
    path("", views.console_home, name="console_home"),
    path("api/modules/", views.api_modules, name="api_modules"),
    path("api/create-module/", views.api_create_module, name="api_create_module"),
    path("api/activate/", views.api_activate_module),
    path("api/deactivate/", views.api_deactivate_module),
    path("api/token-usage/", views.api_token_usage),
    path("api/execute/", views.api_execute_module),
    path("api/module/<str:name>/signature/", views.api_module_signature),
]