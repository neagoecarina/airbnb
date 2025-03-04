from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the given argument."""
    try:
        return value * float(arg)
    except (ValueError, TypeError):
        return value
