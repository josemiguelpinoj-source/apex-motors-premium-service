Apex Motors Premium Service

## El sitio

Sitio de demostración en Django para clientes y propietarios de vehículos de mediana y alta gama que buscan diagnóstico, mantención o reparación especializada. Incluye Inicio, Servicios con filtro y detalle, Planes, Galería y Contacto. El catálogo vive en `core/data/services.json`; las reservas confirmadas se guardan en `core/data/reservations.json` y bloquean los horarios ocupados. Los mensajes de contacto se validan en el servidor y no se almacenan. Los datos comerciales y los valores son de ejemplo.

## Cómo ejecutarlo

Requiere Python 3.12 o superior. En Windows, desde la carpeta que contiene `manage.py`:

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py check
python manage.py test
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. Este proyecto no configura ni utiliza una base de datos. Para personalizar la configuración, define las variables `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS` en el entorno antes de iniciar el servidor.

## Uso de IA

Se utilizó GitHub Copilot como agente de IA para apoyar la estructura, el código, el diseño y las pruebas. Estos fueron los prompts principales, resumidos:

- «Crea un sitio Django sin base de datos, con datos JSON, seis páginas, menú, Bootstrap, diseño responsive y formulario validado».
- «Implementa una capa de servicios con caché, filtros de plantilla con humanize, carrusel reutilizable y pruebas automáticas».

**Acepté:** la separación entre vistas, rutas, lectura JSON, contexto compartido, plantillas, estáticos y pruebas.

**Corregí:** la búsqueda del detalle para recorrer una lista JSON; las pruebas para no depender de una base de datos; el formato CLP para usar puntos como separadores de miles; y el contador del carrusel para reflejar las tarjetas visibles.

**Descarté:** la configuración inicial del proyecto que incluía SQLite, autenticación y administración, porque esta entrega debe funcionar sin base de datos. Las decisiones finales y el contenido deben ser revisados y explicados por el estudiante.

### Archivos principales

- `manage.py`: punto de entrada para ejecutar comandos Django.
- `config/settings.py`: aplicaciones, plantillas, zona horaria, estáticos y variables de entorno.
- `config/urls.py` y `core/urls.py`: conectan las direcciones del proyecto con sus vistas.
- `core/views.py`: prepara las páginas, filtra servicios y valida el contacto.
- `core/services.py`: lectura del JSON con caché.
- `core/context_processors.py`: menú e información comercial compartidos.
- `core/data/services.json`: servicios de ejemplo, precios en CLP y rutas locales de sus imágenes.
- `core/templates/core/`: estructura HTML reutilizable y las seis páginas.
- `core/static/core/`: hoja de estilos responsive, JavaScript del carrusel, imágenes locales y el video de fondo del vehículo en movimiento.
- `core/templatetags/clp.py`: filtro de precios que utiliza `humanize`.
- `core/tests.py`: pruebas de páginas, filtro y formulario.
- `requirements.txt`: Django y la dependencia externa `humanize`.

### Datos que debes reemplazar

Actualiza el catálogo y sus precios en `core/data/services.json`; cambia nombre, teléfono, correo, dirección, horario y redes en `core/context_processors.py` y `core/templates/core/base.html`; revisa los precios de planes en `core/templates/core/plans.html`. Las fotografías locales están guardadas en `core/static/core/images/`. La imagen de “Nuestra promesa” y las fotos nuevas de la galería se cargan desde Pexels bajo su licencia gratuita: [taller](https://www.pexels.com/photo/black-sports-car-in-an-auto-repair-shop-15085608/) y [deportivos](https://www.pexels.com/photo/sports-cars-in-workshop-4756886/) de Jae Park, y [auto rojo en reparación](https://www.pexels.com/photo/red-sports-car-on-lift-in-auto-repair-garage-37163499/) de Ivan Chumak. Requieren conexión a internet. Antes de publicar, define una clave secreta real y `DEBUG=False` mediante variables de entorno.
