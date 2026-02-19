from django import template

register = template.Library()


@register.filter
def calc_percentage(value, total):
    """
    Calculate percentage of value out of total.
    Usage: {{ value|calc_percentage:total }}
    """
    try:
        value = float(value)
        total = float(total)
        if total > 0:
            return round((value / total) * 100, 1)
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
