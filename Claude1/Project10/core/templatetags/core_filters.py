from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """Split a string by a delimiter"""
    if value:
        return value.split(delimiter)
    return []


@register.filter
def strip(value):
    """Strip whitespace from a string"""
    if value:
        return value.strip()
    return ''


@register.filter
def range_filter(value):
    """Returns a range of numbers from 0 to value"""
    try:
        return range(value)
    except (ValueError, TypeError):
        return range(0)


@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
