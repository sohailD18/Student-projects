from django import template

register = template.Library()


@register.filter
def dict_key(d, key):
    """Access dictionary key in template."""
    try:
        return d.get(key, [])
    except (TypeError, AttributeError):
        return []
