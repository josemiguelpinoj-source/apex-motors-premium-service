"""Rutas principales del proyecto."""
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
]
