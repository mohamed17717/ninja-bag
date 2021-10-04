from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.conf import settings

import json


def cache_request(name_format, timeout=60*60*24, identifier=None):
  def decorator(func):
    def wrapper(*args, **kwargs):
      name = name_format
      if identifier: 
        name = name_format.format(**{identifier: kwargs[identifier]})

      output = cache.get(name)
      if not output:
        output = func(*args, **kwargs)
        cache.set(name, output, timeout=timeout)

      return output
    return wrapper
  return decorator

def required_post_fields(required_fields=[]):
  def decorator(func):

    def wrapper(request, *args, **kwargs):
      fields = {}
      fields.update(request.POST.dict())
      fields.update(request.FILES.dict())

      try:
        request_body = json.loads(request.data)
        fields.update(request_body)
      except: pass

      posted_fields = fields.keys()

      error_response = lambda field: HttpResponseBadRequest(f'field "{field}" is required.')
      for required_field in required_fields:
        if required_field not in posted_fields:
          return error_response(required_field)

      return func(request, *args, **kwargs)

    return wrapper
  return decorator

def function_nickname(nickname):
  def decorator(func):
    def wrapper(*args, **kwargs): 
      return func(*args, **kwargs)
    wrapper.__name__ = nickname
    return wrapper
  return decorator

def cache_counter(name_format):
  def decorator(func):
    def wrapper(*args, **kwargs):
      key = name_format.format(args[1])

      count = int(cache.get(key, 1)) + 1
      cache.set(key, count)
      if count % 100 == 0:
        func(*args, **kwargs)

    return wrapper
  return decorator







def tool_handler(func_reverser):
  def run_tool_view_safely(func, request, *args, **kwargs):
    if settings.DEBUG:
      response = func(request, *args, **kwargs)
    else:
      try:
        response = func(request, *args, **kwargs)
      except Exception as e:
        response = HttpResponseBadRequest('unexpected error happened.')
    
    return response

  def decorator(func):
    def wrapper(request, *args, **kwargs):
      tool = func_reverser(func)

      is_tool_accessable = tool and tool.active
      if is_tool_accessable == False:
        raise PermissionDenied('You can\'t access this tool.' )

      response = run_tool_view_safely(func, request, *args, **kwargs)
      tool.increase_uses_count()

      return response

    return wrapper
  return decorator

