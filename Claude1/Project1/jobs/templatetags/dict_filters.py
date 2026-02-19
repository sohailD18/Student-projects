from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return 0
    return dictionary.get(key, 0)


@register.filter
def multiply(value, arg):
    """Template filter to multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Template filter to divide value by arg"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def floatformat_custom(value, arg=2):
    """Template filter to format float with custom decimal places"""
    try:
        return round(float(value), int(arg))
    except (ValueError, TypeError):
        return value


@register.filter
def to_json(value):
    """Template filter to convert Python object to JSON string for use in JavaScript"""
    try:
        return json.dumps(value)
    except (TypeError, ValueError):
        return '[]'
