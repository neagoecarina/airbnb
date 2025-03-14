from django import template

register = template.Library()


from decimal import Decimal

@register.filter
def multiply(value, arg):
    """Multiplies the value by the given argument, handling both float and decimal."""
    try:
        # Convert the value and arg to Decimal, ensuring precision is maintained
        value = Decimal(value)
        arg = Decimal(arg)
        return value * arg
    except (ValueError, TypeError, InvalidOperation):
        # Return the original value if there's an error
        return value
