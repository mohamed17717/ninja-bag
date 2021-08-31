from django import template
from django.shortcuts import render_to_response
from django.template import RequestContext


def error_page(number):
  template_name = 'error-page.html'
  def view_function(request, *args, **kwargs):
    response = render_to_response(template_name, {'number': number})
    response.status_code = number
    return response
  return view_function
