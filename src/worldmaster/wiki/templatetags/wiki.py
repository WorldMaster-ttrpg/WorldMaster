from json import dumps

from django import template

register = template.Library()

json = register.simple_tag(name="json")(dumps)

