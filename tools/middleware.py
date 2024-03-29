import re

from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import get_object_or_404
from django.conf import settings

from toolsframe.models import Tool


class ToolMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)

    if response.status_code >= 500 and settings.DEBUG is False:
      raise BadRequest('unexpected error happened.')

    return response

  def process_view(self, request, view_func, view_args, view_kwargs):
    path = request.path
    tool_path_pattern = r'/t/[\w-]+'
    if re.match(tool_path_pattern, path):
      try:
        tool_id = view_func.__self__.tool_id
        tool = get_object_or_404(Tool, tool_id=tool_id)

        # check tool activity
        if tool.active is False:
          raise PermissionDenied('You can\'t access this tool.' )

        tool.increase_uses_count()
      except AttributeError as e:
        pass
