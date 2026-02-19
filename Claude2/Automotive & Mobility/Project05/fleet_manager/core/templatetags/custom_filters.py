"""
Custom template filters for the fleet management system
"""
from django import template

register = template.Library()


@register.filter
def percentage(value, decimal_places=2):
    """
    Format a decimal value as a percentage
    Usage: {{ value|percentage:"2" }}
    """
    try:
        # Convert to float and multiply by 100
        value = float(value) * 100
        # Format with specified decimal places
        return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return value
