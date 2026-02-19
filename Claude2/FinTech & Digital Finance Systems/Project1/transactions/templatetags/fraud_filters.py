"""
Custom template filters for the fraud detection system.
"""
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def add(value, arg):
    """Add the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def negate(value):
    """Return the negative of the value"""
    try:
        return -float(value)
    except (ValueError, TypeError):
        return 0
