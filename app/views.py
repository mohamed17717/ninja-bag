from django import template
from django.shortcuts import render_to_response, HttpResponse
from tools.controller import RequestAnalyzerTools

from utils.views_mixins import GenerateRequestContext

def error_page(number):
  template_name = 'error-page.html'
  def view_function(request, *args, **kwargs):
    ua = request.META['HTTP_USER_AGENT']
    ua_details = RequestAnalyzerTools.get_user_agent_details(ua)

    is_from_api = not any(ua_details['flags'].values()) # all must be false
    if is_from_api:
      response = HttpResponse(status=number)
    else:
      context = { 'number': number, **GenerateRequestContext(request) }
      response = render_to_response(template_name, context)
      response.status_code = number

    return response
  return view_function
