"""Datos compartidos por todas las plantillas."""


def site_context(request):
    """Entrega menú e información comercial desde un solo lugar."""
    return {
        "site_menu": [
            {"label": "Inicio", "url_name": "home"},
            {"label": "Servicios", "url_name": "services"},
            {"label": "Detalle", "url_name": "service_detail", "service_id": 1},
            {"label": "Planes", "url_name": "plans"},
            {"label": "Galería", "url_name": "gallery"},
            {"label": "Contacto", "url_name": "contact"},
        ],
        "business": {
            "name": "Apex Motors Premium Service",
            "tagline": "Precisión, confianza y excelencia automotriz.",
            "phone": "+56 2 2345 6789",
            "email": "contacto@apexmotors.cl",
            "address": "Av. Concha y Toro 2505, Puente Alto, Santiago",
            "hours": {
                "Lun-Vie": "08:30–18:30",
                "Sábado": "08:30–13:00",
                "Domingo y Festivos": "Cerrado"
            }
        },
    }
