from django import template

register = template.Library()


@register.filter
def percentage(value):
    """
    Convert a decimal to a percentage string.
    Usage: {{ 0.85|percentage }} -> 85%
    """
    try:
        value = float(value)
        return f"{int(value * 100)}%"
    except (ValueError, TypeError):
        return "N/A"
