from django import template
from decimal import Decimal
from django.core.exceptions import ValidationError

register = template.Library()

# Filter to multiply values
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

# Filter to get item from dictionary
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
