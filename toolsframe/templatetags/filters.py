from django import template
import json

register = template.Library()


@register.filter
def percent_of(value, arg):
  """Removes all values of arg from the given string"""
  return round(value/arg *100)

@register.filter
def to_int(value):
  return round(value)

@register.filter
def to_json(value):
  return json.dumps(value)
