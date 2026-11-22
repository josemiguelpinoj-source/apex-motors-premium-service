"""Direcciones de las páginas de la aplicación."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("servicios/", views.services, name="services"),
    path("servicios/<int:service_id>/", views.service_detail, name="service_detail"),
    path("planes/", views.plans, name="plans"),
    path("galeria/", views.gallery, name="gallery"),
    path("contacto/", views.contact, name="contact"),
]
