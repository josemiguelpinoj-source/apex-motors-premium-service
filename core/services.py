"""Acceso centralizado al catálogo JSON del sitio."""
import json
from functools import lru_cache
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "data" / "services.json"


@lru_cache(maxsize=1)
def get_services():
    """Carga el catálogo una vez y reutiliza los datos en futuras solicitudes."""
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def clear_services_cache():
    """Permite recargar el archivo cuando se actualiza durante el desarrollo."""
    get_services.cache_clear()
