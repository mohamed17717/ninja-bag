
from django.core.exceptions import PermissionDenied
from toolsframe.models import Tool, ToolViewsFunctions
from accounts.models import Account
from utils.handlers import LimitsHandler, ToolHandler
from django.http import HttpResponseBadRequest


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
