from django.urls import path
from .views import test_forgeos

urlpatterns = [
    path("test-forgeos/", test_forgeos),
]