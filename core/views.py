"""Vistas públicas del taller."""
import re

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .services import get_services


def home(request):
    """Portada con una selección del catálogo."""
    services = get_services()
    featured = services[:4]
    return render(request, "core/home.html", {"services": services, "featured": featured})


def services(request):
    """Muestra el catálogo y aplica un filtro por categoría."""
    all_services = get_services()
    categories = sorted({item["category"] for item in all_services})
    selected_category = request.GET.get("categoria", "").strip()
    if selected_category not in categories:
        selected_category = ""

    visible_services = []
    total_from = 0
    for item in all_services:
        if not selected_category or item["category"] == selected_category:
            visible_services.append(item)
            total_from += item["price"]

    average_price = total_from // len(visible_services) if visible_services else 0
    return render(
        request,
        "core/services.html",
        {
            "services": visible_services,
            "categories": categories,
            "selected_category": selected_category,
            "average_price": average_price,
        },
    )


def service_detail(request, service_id):
    """Busca un servicio por su identificador de catálogo."""
    service = next((item for item in get_services() if item["id"] == service_id), None)
    if service is None:
        raise Http404("Servicio no encontrado.")
    return render(request, "core/service_detail.html", {"service": service})


def plans(request):
    """Presenta los tres planes de mantención."""
    return render(request, "core/plans.html")


def gallery(request):
    """Galería referencial del taller y sus especialidades."""
    return render(request, "core/gallery.html")


def contact(request):
    """Valida el formulario y usa Post/Redirect/Get sin guardar datos."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        errors = []

        if not 2 <= len(name) <= 80:
            errors.append("El nombre debe tener entre 2 y 80 caracteres.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Ingresa un correo electrónico válido.")
        if phone and not re.fullmatch(r"[\d+\s().-]{8,20}", phone):
            errors.append("Revisa el formato del teléfono.")
        if not 10 <= len(message) <= 1000:
            errors.append("El mensaje debe tener entre 10 y 1.000 caracteres.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "core/contact.html",
                {"form_data": {"name": name, "email": email, "phone": phone, "message": message}},
                status=400,
            )

        messages.success(
            request,
            f"Gracias, {name}. Recibimos tu solicitud; te contactaremos pronto.",
        )
        return redirect("contact")

    return render(request, "core/contact.html")
