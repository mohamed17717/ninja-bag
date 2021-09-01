from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View

from .models import Tool, UpcomingTool, SuggestedTool, ToolIssueReport

from utils.decorators import require_http_methods, required_post_fields
from utils.handlers import ToolHandler
from utils.mixins import ExtractPostRequestData, GenerateDefaultContext, FormSaveMixin
from utils.helpers import Redirector

from .forms import ToolIssueReportForm, SuggestToolForm


@require_http_methods(['GET'])
def toggle_color_mode(request):
  response = Redirector.go_previous_page(request)
  cookie_name = 'light-mode'
  if request.COOKIES.get(cookie_name):
    response.delete_cookie(cookie_name)
  else:
    response.set_cookie(cookie_name, 'true')

  return response



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
  Tool.objects.increase_views_count(pk=tool.pk)

  context = {
    **GenerateDefaultContext(request),
    'tool': tool,
    'db_records': tool.get_db_records(request.user),
    'issue_form': ToolIssueReportForm()
  }

  return render(request, 'd_tool-doc.html', context)


class SuggestTool(FormSaveMixin, View):
  form_class = SuggestToolForm

  def update_saved_object(self, request, obj, *args, **kwargs):
    if request.user.is_authenticated:
      obj.user = request.user
    return obj
class ReportToolIssue(FormSaveMixin, View):
  form_class = ToolIssueReportForm

  def update_saved_object(self, request, obj, *args, **kwargs):
    tool_id = kwargs.get('tool_id')
    tool = Tool.objects.force_get(tool_id=tool_id)
    obj.tool = tool

    if request.user.is_authenticated:
      obj.user = request.user
    return obj

