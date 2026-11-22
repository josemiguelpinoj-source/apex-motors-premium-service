"""Filtros para presentar valores en pesos chilenos."""
import humanize
from django import template

register = template.Library()


@register.filter
def clp(value):
    """Formatea un número entero con separadores de miles y símbolo CLP."""
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return "$0"
    return f"${humanize.intcomma(amount).replace(',', '.')}"
