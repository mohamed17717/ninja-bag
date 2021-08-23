from django.shortcuts import render
from django.http import HttpResponse

from .models import Tool, UpcomingTool, SuggestedTool, ToolIssueReport
from decorators import require_http_methods, required_post_fields

from handlers import ToolHandler

from mixins import ExtractPostRequestData

def get_default_context(request):
  is_authenticated = request.user.is_authenticated
  context = {
    'upcoming_tools': UpcomingTool.objects.get_active(),
    'is_limits_active': ToolHandler.is_limits_active,
    'is_authenticated': request.user.is_authenticated
  }

  if is_authenticated:
    user = request.user
    context.update({ 
      'account': user.user_account,
      'db_tools': Tool.objects.get_tools_that_has_db_for_aside_section(user)
    })

  return context

@require_http_methods(['GET'])
def index(request):
  context = {
    **get_default_context(request),
    'tools': Tool.objects.list_for_homepage()
  }

  return render(request, 'd_homepage.html', context)


@require_http_methods(['GET'])
def get_tool_page(request, tool_id):
  tool = Tool.objects.force_get(tool_id=tool_id)
  tool.increase_views_count()

  context = {
    **get_default_context(request),
    'tool': tool,
    'db_records': tool.get_db_records(request.user)
  }

  return render(request, 'd_tool-doc.html', context)


@require_http_methods(['POST'])
@required_post_fields(['description'])
def suggest_tool(request):
  user = request.user

  post_data = ExtractPostRequestData(request)
  description = post_data.get('description', '').strip()

  SuggestedTool.objects.create(user=user, description=description)
  return HttpResponse(status=201)

@require_http_methods(['POST'])
@required_post_fields(['description'])
def report_tool_issue(request, tool_id):
  user = request.user
  tool = Tool.objects.force_get(tool_id=tool_id)

  post_data = ExtractPostRequestData(request)
  description = post_data.get('description', '').strip()

  ToolIssueReport.objects.create(user=user, tool=tool, description=description)
  return HttpResponse(status=201)
