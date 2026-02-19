"""
Custom template filters for the Finance Platform.
"""
from django import template
from django.template.defaultfilters import register

register = template.Library()


@register.filter
def get_alert_type(insight):
    """
    Return alert type based on insight type and severity.
    """
    type_mapping = {
        'alert': 'danger',
        'warning': 'warning',
        'pattern': 'info',
        'recommendation': 'primary',
        'forecast': 'info'
    }

    if isinstance(insight, dict):
        insight_type = insight.get('type', 'info')
        severity = insight.get('severity', '')

        if severity == 'critical':
            return 'danger'
        elif severity == 'warning':
            return 'warning'
        elif severity == 'caution':
            return 'info'

        return type_mapping.get(insight_type, 'info')

    return 'info'


@register.filter
def get_budget_status_color(budget):
    """
    Return color class based on budget status.
    """
    status = budget.status if hasattr(budget, 'status') else budget

    color_mapping = {
        'Over Budget': 'danger',
        'Near Limit': 'warning',
        'Moderate': 'info',
        'On Track': 'success'
    }

    return color_mapping.get(status, 'secondary')


@register.filter
def get_progress_color(budget):
    """
    Return progress bar color based on utilization.
    """
    utilization = budget.utilization_percentage if hasattr(budget, 'utilization_percentage') else 0

    if utilization >= 100:
        return 'danger'
    elif utilization >= 80:
        return 'warning'
    elif utilization >= 50:
        return 'info'
    else:
        return 'success'


@register.filter
def get_status_color(status):
    """
    Return color based on status string.
    """
    color_mapping = {
        'Over Budget': 'danger',
        'Near Limit': 'warning',
        'Moderate': 'info',
        'On Track': 'success'
    }

    return color_mapping.get(status, 'secondary')


@register.filter
def sub(value, arg):
    """
    Subtraction filter.
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def define(value=None):
    """
    Define a variable in template.
    """
    return value


@register.filter
def percentage(value):
    """
    Convert decimal to percentage string.
    """
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "0%"


@register.filter
def multiply(value, arg):
    """
    Multiply value by arg.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Divide value by arg.
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def abs_filter(value):
    """
    Return absolute value.
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def truncatewords_custom(value, arg):
    """
    Truncate text after a certain number of words.
    """
    try:
        from django.utils.text import truncate_words
        return truncate_words(value, int(arg))
    except:
        # For newer Django versions
        from django.utils.text import Truncator
        return Truncator(value).words(int(arg), truncate=' ...')
