from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from .models import Category, Tool, UpcomingTool, SuggestedTool
from decorators import require_http_methods

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
  context = {
    **get_default_context(request),
    'tool': get_object_or_404(Tool, tool_id=tool_id)
  }
  return render(request, 'd_tool-doc.html', context)


@require_http_methods(['POST'])
def suggest_tool(request):
  user = request.user

  data = request.POST or json.loads(request.body.decode('utf8'))
  description = data.get('description', '').strip()

  if not user or not description:
    return HttpResponseBadRequest()

  SuggestedTool.objects.create(user=user, description=description)
  return HttpResponse(status=201)

