"""Pruebas de páginas, catálogo y formulario."""
from django.test import SimpleTestCase
from django.urls import reverse

from .services import clear_services_cache, get_services


class SitePagesTests(SimpleTestCase):
    def setUp(self):
        clear_services_cache()

    def test_all_main_pages_render(self):
        for route in ("home", "services", "plans", "gallery", "contact"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
        home_page = self.client.get(reverse("home"))
        self.assertContains(home_page, reverse("service_detail", args=(1,)))
        self.assertContains(home_page, "/static/core/images/promesa-estandar.jpg")

    def test_home_shows_multibrand_section(self):
        response = self.client.get(reverse("home"))
        brands = (
            ("citroen-logo.svg", "Citroën"),
            ("audi-logo.svg", "Audi"),
            ("subaru-logo.png", "Subaru"),
            ("peugeot-logo.svg", "Peugeot"),
            ("mercedes-benz-logo.svg", "Mercedes-Benz"),
            ("jaguar-logo.svg", "Jaguar"),
            ("porsche-logo.svg", "Porsche"),
            ("alfa-romeo-logo.svg", "Alfa Romeo"),
            ("volvo-logo.svg", "Volvo"),
            ("dodge-logo.png", "Dodge"),
            ("chrysler-logo.svg", "Chrysler"),
            ("toyota-logo.svg", "Toyota"),
        )
        for logo, brand in brands:
            with self.subTest(brand=brand):
                self.assertContains(response, brand)
                self.assertContains(
                    response,
                    f"/static/core/images/brands/{logo}",
                )

    def test_services_are_read_from_json_and_can_be_filtered(self):
        self.assertGreaterEqual(len(get_services()), 6)
        self.assertTrue(all(item["image"].startswith("/static/core/images/") for item in get_services()))
        response = self.client.get(reverse("services"), {"categoria": "Diagnóstico"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Diagnóstico computarizado")
        self.assertContains(response, "$25.000")
        self.assertContains(response, "$42.500")
        self.assertContains(response, "Económico")
        self.assertNotContains(response, "· Premium")
        self.assertNotContains(response, "Detalle y protección")

    def test_service_price_labels_reflect_catalog_data(self):
        response = self.client.get(reverse("services"))
        self.assertContains(response, "Económico")
        self.assertContains(response, "Premium")

    def test_home_and_services_carousels_include_motion_control(self):
        for route in ("home", "services"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertContains(response, "data-carousel-toggle")

    def test_gallery_loads_related_image_and_two_high_resolution_photos(self):
        response = self.client.get(reverse("gallery"))
        self.assertContains(response, "suspension-direccion-reparacion.png")
        self.assertContains(response, "photos/4756886/")
        self.assertContains(response, "photos/37163499/")

    def test_business_hours_are_rendered_as_readable_entries(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Lun-Vie: 08:30–18:30")
        self.assertContains(response, "Sábado: 08:30–13:00")
        self.assertNotContains(response, "{&#x27;Lun-Vie&#x27;")

    def test_service_detail_exists(self):
        response = self.client.get(reverse("service_detail", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Diagnóstico computarizado")
        self.assertContains(response, "/static/core/images/diagnostico-computarizado.jpg")

        alignment = self.client.get(reverse("service_detail", args=(4,)))
        self.assertContains(alignment, "Alineación 3D")
        self.assertContains(alignment, "/static/core/images/alineacion-3d.jpg")

        suspension = self.client.get(reverse("service_detail", args=(7,)))
        self.assertContains(suspension, "Suspensión y dirección")
        self.assertContains(suspension, "/static/core/images/suspension-direccion-reparacion.png")

    def test_contact_validates_and_redirects_after_post(self):
        invalid = self.client.post(
            reverse("contact"),
            {"name": "A", "email": "incorrecto", "message": "corto"},
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertContains(invalid, "correo electrónico válido", status_code=400)

        valid = self.client.post(
            reverse("contact"),
            {
                "name": "Cliente de prueba",
                "email": "cliente@example.com",
                "phone": "+56 9 1234 5678",
                "message": "Quisiera agendar una evaluación para mi vehículo.",
            },
        )
        self.assertEqual(valid.status_code, 302)
        self.assertEqual(valid["Location"], reverse("contact"))
        confirmation = self.client.get(reverse("contact"))
        self.assertContains(confirmation, "Recibimos tu solicitud")
