from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.core.cache import cache

from toolsframe.models import Tool

from handlers import LimitsHandler, ToolHandler

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


def tool_handler(limitation=[]):
  def decorator(func):
    th = ToolHandler()

    tool_id = th.reverse_view_func_to_tool_id(func)
    tool = Tool.get_tool_by_tool_id(tool_id)

    def wrapper(request, *args, **kwargs):
      api_key = request.GET.get('token', None)

      acc = th.get_acc(api_key, limitation)
      limits_handler = LimitsHandler(acc)

      args_of_limit_before_hook = (request,)
      access_states = th.run_limits_before(limits_handler, limitation, args_of_limit_before_hook)

      response = HttpResponseBadRequest('You have no access to use this tool')

      if all(access_states):
        response = th.run_func(func, request, *args, **kwargs)

        args_of_limit_after_hook = (request, response)
        th.run_limits_after(limits_handler, limitation, args_of_limit_after_hook)
        tool.increase_uses_count()

      return response
    return wrapper

  return decorator


def required_post_fields(required_fields=[]):
  def decorator(func):

    def wrapper(request, data, *args, **kwargs):
      posted_fields = request.POST.dict().keys()

      error_response = lambda field: HttpResponseBadRequest(f'field "{field}" is required.')
      for required_field in required_fields:
        if required_field not in posted_fields:
          return error_response(required_field)

      return func(request, *args, **kwargs)

    return wrapper
  return decorator

