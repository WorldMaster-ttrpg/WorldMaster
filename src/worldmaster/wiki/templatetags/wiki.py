from json import dumps

from django import template

register = template.Library()

@register.filter
def json(value):
    """Encode to json."""
    dumps(value, indent=2)

