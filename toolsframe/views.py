from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Tool, UpcomingTool, SuggestedTool
from decorators import require_http_methods, required_post_fields

import json
from classes.Redirector import Redirector

def get_default_context(request):
  return {
    'user': request.user,
    'account': request.user.user_account.get(),
    'upcoming_tools': UpcomingTool.list_all_active(),
  }

@require_http_methods(['GET'])
def index(request):
  if not request.user.is_authenticated:
    return Redirector.go_login()

  context = {
    **get_default_context(request),
    'tools': Tool.list_for_homepage()
  }

  return render(request, 'd_homepage.html', context)


@require_http_methods(['GET'])
def get_tool_page(request, tool_id):
  tool = get_object_or_404(Tool, tool_id=tool_id)
  tool.increase_views_count()

  context = {
    **get_default_context(request),
    'tool': tool
  }

  return render(request, 'd_tool-doc.html', context)


@require_http_methods(['POST'])
@required_post_fields(['description'])
def suggest_tool(request):
  user = request.user

  data = request.POST or json.loads(request.body.decode('utf8'))
  description = data.get('description', '').strip()

  SuggestedTool.objects.create(user=user, description=description)
  return HttpResponse(status=201)

