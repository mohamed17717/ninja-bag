from django.shortcuts import render
from django.http import HttpResponse

from .models import Tool, UpcomingTool, SuggestedTool, ToolIssueReport

from utils.decorators import require_http_methods, required_post_fields
from utils.handlers import ToolHandler
from utils.mixins import ExtractPostRequestData, GenerateDefaultContext

from .forms import ToolIssueReportForm, SuggestToolForm

@require_http_methods(['GET'])
def index(request):
  context = {
    **GenerateDefaultContext(request),
    'tools': Tool.objects.list_for_homepage()
  }

  return render(request, 'd_homepage.html', context)


@require_http_methods(['GET'])
def get_tool_page(request, tool_id):
  tool = Tool.objects.force_get(tool_id=tool_id)
  tool.increase_views_count()

  context = {
    **GenerateDefaultContext(request),
    'tool': tool,
    'db_records': tool.get_db_records(request.user),
    'issue_form': ToolIssueReportForm()
  }

  return render(request, 'd_tool-doc.html', context)


@require_http_methods(['POST'])
@required_post_fields(['description'])
def suggest_tool(request):
  post_data = ExtractPostRequestData(request)
  form = SuggestToolForm(post_data)

  if not form.is_valid():
    return HttpResponse(form.get_error_meesage(), status=400)

  obj = form.save(commit=False)
  obj.user = request.user
  obj.save()

  return HttpResponse(status=201)


@require_http_methods(['POST'])
@required_post_fields(['description'])
def report_tool_issue(request, tool_id):
  post_data = ExtractPostRequestData(request)
  form = ToolIssueReportForm(post_data)

  if not form.is_valid():
    return HttpResponse(form.get_error_meesage(), status=400)

  obj = form.save(commit=False)
  obj.user = request.user
  obj.tool = Tool.objects.force_get(tool_id=tool_id)
  obj.save()

  return HttpResponse(status=201)
