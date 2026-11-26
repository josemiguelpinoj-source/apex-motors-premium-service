"""Vistas públicas del taller."""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from django.contrib import messages
from django.http import Http404, JsonResponse
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


def _time_to_minutes(value):
    hour, minute = (int(part) for part in value.split(":"))
    return hour * 60 + minute


def _minutes_to_time(value):
    return f"{value // 60:02d}:{value % 60:02d}"


def _reservations_path():
    return Path(__file__).resolve().parent / "data" / "reservations.json"


def _occupied_intervals(config, selected_date, reservations):
    weekday = selected_date.weekday()
    day_config = "saturday" if weekday == 5 else "weekday"
    occupied_times = list(config["occupied"].get(day_config, {}).get(str(weekday), []))
    offset = (selected_date - date.today()).days
    occupied_times.extend(config["specific_offsets"].get(str(offset), []))
    slot_minutes = int(config["slot_minutes"])
    intervals = [
        (_time_to_minutes(time), _time_to_minutes(time) + slot_minutes)
        for time in occupied_times
    ]

    date_value = selected_date.isoformat()
    for reservation in reservations:
        if reservation.get("date") == date_value and reservation.get("status") == "confirmada":
            reservation_start = _time_to_minutes(reservation["time"])
            reservation_end = reservation_start + int(reservation["duration_minutes"])
            intervals.append((reservation_start, reservation_end))
    return intervals


def _duration_minutes(duration):
    normalized = duration.lower().replace(",", ".")
    match = re.search(r"([\d.]+)", normalized)
    if not match:
        return 60
    return max(30, int(float(match.group(1)) * 60))


def booking_availability(request):
    """Devuelve en JSON los horarios disponibles para una fecha y servicio."""
    date_value = request.GET.get("date", "").strip()
    service_id = request.GET.get("service", "").strip()
    try:
        selected_date = date.fromisoformat(date_value)
        service = next(
            (item for item in get_services() if str(item["id"]) == service_id),
            None,
        )
    except ValueError:
        return JsonResponse({"error": "Fecha no válida."}, status=400)

    if service is None:
        return JsonResponse({"error": "Servicio no válido."}, status=400)

    config_path = Path(__file__).resolve().parent / "data" / "booking.json"
    with config_path.open(encoding="utf-8") as file:
        config = json.load(file)

    today = date.today()
    booking_end = date.fromisoformat(config["booking_end_date"])
    if selected_date < today or selected_date > booking_end:
        return JsonResponse({"error": "La fecha está fuera del calendario disponible."}, status=400)

    weekday = selected_date.weekday()
    if weekday == 6:
        return JsonResponse({
            "date": date_value,
            "service": service["name"],
            "duration_minutes": _duration_minutes(service["duration"]),
            "hours": config["hours"]["sunday"],
            "slots": [],
        })

    day_config = "saturday" if weekday == 5 else "weekday"
    hours = config["hours"][day_config]

    duration = _duration_minutes(service["duration"])
    slot_minutes = int(config["slot_minutes"])
    open_minutes = _time_to_minutes(hours["open"])
    close_minutes = _time_to_minutes(hours["close"])
    reservations = json.loads(_reservations_path().read_text(encoding="utf-8"))
    occupied_intervals = _occupied_intervals(config, selected_date, reservations)
    slots = []

    for start in range(open_minutes, close_minutes, slot_minutes):
        end = start + duration
        if end > close_minutes:
            break

        is_occupied = any(start < busy_end and end > busy_start for busy_start, busy_end in occupied_intervals)
        slots.append({
            "time": _minutes_to_time(start),
            "available": not is_occupied,
        })

    return JsonResponse({
        "date": date_value,
        "service": service["name"],
        "duration_minutes": duration,
        "hours": hours,
        "slots": slots,
    })


def booking_confirm(request):
    """Confirma y registra una reserva, bloqueando el horario seleccionado."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    date_value = request.POST.get("date", "").strip()
    time_value = request.POST.get("time", "").strip()
    service_id = request.POST.get("service", "").strip()
    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()

    try:
        selected_date = date.fromisoformat(date_value)
    except ValueError:
        return JsonResponse({"error": "Fecha no válida."}, status=400)

    service = next((item for item in get_services() if str(item["id"]) == service_id), None)
    if service is None:
        return JsonResponse({"error": "Servicio no válido."}, status=400)
    if not re.fullmatch(r"\d{2}:\d{2}", time_value):
        return JsonResponse({"error": "Hora no válida."}, status=400)
    if not 2 <= len(name) <= 80:
        return JsonResponse({"error": "Ingresa tu nombre."}, status=400)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return JsonResponse({"error": "Ingresa un correo válido."}, status=400)

    config_path = Path(__file__).resolve().parent / "data" / "booking.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    today = date.today()
    booking_end = date.fromisoformat(config["booking_end_date"])
    if selected_date < today or selected_date > booking_end:
        return JsonResponse({"error": "La reserva está fuera del calendario disponible."}, status=400)

    reservations_path = _reservations_path()
    reservations = json.loads(reservations_path.read_text(encoding="utf-8"))

    start = _time_to_minutes(time_value)
    duration = _duration_minutes(service["duration"])
    weekday = selected_date.weekday()
    if weekday == 6:
        return JsonResponse({"error": "El taller está cerrado los domingos."}, status=409)
    day_config = "saturday" if weekday == 5 else "weekday"
    hours = config["hours"][day_config]
    open_minutes = _time_to_minutes(hours["open"])
    slot_minutes = int(config["slot_minutes"])
    if (
        start < open_minutes
        or start + duration > _time_to_minutes(hours["close"])
        or (start - open_minutes) % slot_minutes
    ):
        return JsonResponse({"error": "El horario excede el funcionamiento del taller."}, status=409)

    occupied_intervals = _occupied_intervals(config, selected_date, reservations)
    if any(start < busy_end and start + duration > busy_start for busy_start, busy_end in occupied_intervals):
        return JsonResponse({"error": "El horario ya está ocupado."}, status=409)

    reservations.append({
        "date": date_value,
        "time": time_value,
        "service_id": int(service_id),
        "service": service["name"],
        "duration_minutes": duration,
        "code": f"APX-{uuid4().hex[:8].upper()}",
        "name": name,
        "email": email,
        "status": "confirmada",
    })
    reservations_path.write_text(json.dumps(reservations, ensure_ascii=False, indent=2), encoding="utf-8")

    return JsonResponse({
        "confirmed": True,
        "date": date_value,
        "time": time_value,
        "service": service["name"],
        "code": reservations[-1]["code"],
    })


def contact(request):
    """Valida el formulario y usa Post/Redirect/Get sin guardar datos."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        service_id = request.POST.get("service", "").strip()
        booking_date = request.POST.get("booking_date", "").strip()
        booking_time = request.POST.get("booking_time", "").strip()
        errors = []

        if not 2 <= len(name) <= 80:
            errors.append("El nombre debe tener entre 2 y 80 caracteres.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Ingresa un correo electrónico válido.")
        if phone and not re.fullmatch(r"[\d+\s().-]{8,20}", phone):
            errors.append("Revisa el formato del teléfono.")
        if not 10 <= len(message) <= 1000:
            errors.append("El mensaje debe tener entre 10 y 1.000 caracteres.")
        if not service_id:
            errors.append("Selecciona el servicio que deseas reservar.")
        elif not any(str(item["id"]) == service_id for item in get_services()):
            errors.append("Selecciona un servicio válido.")
        if not booking_date or not booking_time:
            errors.append("Selecciona una fecha y horario disponible.")
        elif booking_date:
            try:
                requested_date = date.fromisoformat(booking_date)
                end_date = date(2026, 12, 20)
                if requested_date < date.today() or requested_date > end_date:
                    errors.append("La reserva debe realizarse entre hoy y el 20 de diciembre.")
            except ValueError:
                errors.append("Selecciona una fecha válida.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "core/contact.html",
                {
                    "form_data": {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "message": message,
                        "service": service_id,
                        "booking_date": booking_date,
                        "booking_time": booking_time,
                    },
                    "services": get_services(),
                },
                status=400,
            )

        messages.success(
            request,
            f"Gracias, {name}. Recibimos tu solicitud para el {booking_date} a las {booking_time}; te confirmaremos la reserva pronto.",
        )
        return redirect("contact")

    return render(request, "core/contact.html", {"services": get_services()})
