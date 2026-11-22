Apex Motors Premium Service

## El sitio

Sitio de demostración en Django para clientes y propietarios de vehículos de mediana y alta gama que buscan diagnóstico, mantención o reparación especializada. Incluye Inicio, Servicios con filtro y detalle, Planes, Galería y Contacto. El catálogo vive en `core/data/services.json`; el formulario se valida en el servidor y no almacena información. Los datos comerciales y los valores son de ejemplo.

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
- «Compara el proyecto con la pauta de evaluación y corrige las brechas verificables».

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
- `core/static/core/`: hoja de estilos responsive, JavaScript del carrusel e imágenes locales de tecnología, atención personalizada y equipo técnico.
- `core/templatetags/clp.py`: filtro de precios que utiliza `humanize`.
- `core/tests.py`: pruebas de páginas, filtro y formulario.
- `requirements.txt`: Django y la dependencia externa `humanize`.

### Datos que debes reemplazar

Actualiza el catálogo y sus precios en `core/data/services.json`; cambia nombre, teléfono, correo, dirección, horario y redes en `core/context_processors.py` y `core/templates/core/base.html`; revisa los precios de planes en `core/templates/core/plans.html`. Todas las fotografías del sitio están guardadas en `core/static/core/images/`; puedes reemplazarlas conservando los nombres de archivo o actualizar sus rutas. Antes de publicar, define una clave secreta real y `DEBUG=False` mediante variables de entorno.
