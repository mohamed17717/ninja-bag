from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from .models import Tool, UpcomingTool, SuggestedTool, ToolIssueReport

from utils.decorators import require_http_methods, required_post_fields
from utils.handlers import ToolHandler
from utils.mixins import ExtractPostRequestData, GenerateDefaultContext, FormSaveMixin

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


class SuggestTool(FormSaveMixin, View):
  form_class = SuggestToolForm

  def after_save_hook(self, obj, request, *args, **kwargs):
    obj.user = request.user

class ReportToolIssue(FormSaveMixin, View):
  form_class = ToolIssueReportForm

  def after_save_hook(self, obj, request, *args, **kwargs):
    tool_id = kwargs.get('tool_id')

    obj.user = request.user
    obj.tool = Tool.objects.force_get(tool_id=tool_id)

