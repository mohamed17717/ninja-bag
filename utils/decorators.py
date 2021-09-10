from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.core.cache import cache

from toolsframe.models import Tool, ToolViewsFunctions
from accounts.models import Account

from utils.handlers import LimitsHandler, ToolHandler
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

def tool_handler(limitation=[]):
  def decorator(func):
    th = ToolHandler()
    tool = ToolViewsFunctions.objects.reverse_view_func_to_tool(func)

    def wrapper(request, *args, **kwargs):
      # make sure tool is active
      if not tool or not tool.active:
        raise PermissionDenied('You can\'t access this tool.' )

      # make sure tool accessable by this user (limits and token)
      token = request.GET.get('token', None)
      is_acc_required = bool(th.is_limits_active and len(limitation))
      acc = token and Account.objects.get_user_acc_by_token(token, required=is_acc_required)

      limits_handler = LimitsHandler(acc)

      args_for_limit_before_hook = (request,)
      access_states = th.run_limits_before(limits_handler, limitation, args_for_limit_before_hook)

      response = HttpResponseBadRequest('You have no access to use this tool')
      if all(access_states):
        response = th.run_func(func, request, *args, **kwargs)

        args_of_limit_after_hook = (request, response)
        th.run_limits_after(limits_handler, limitation, args_of_limit_after_hook)

        Tool.objects.increase_uses_count(tool.pk)

      return response
    return wrapper

  return decorator

def required_post_fields(required_fields=[]):
  def decorator(func):

    def wrapper(request, *args, **kwargs):
      fields = {}
      fields.update(request.POST.dict())
      fields.update(request.FILES.dict())

      try: 
        request_body = json.loads(request.body.decode('utf8'))
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

