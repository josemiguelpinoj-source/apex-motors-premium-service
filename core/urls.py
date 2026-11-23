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
    path("api/reservas-disponibilidad/", views.booking_availability, name="booking_availability"),
    path("api/reservas-confirmar/", views.booking_confirm, name="booking_confirm"),
]
