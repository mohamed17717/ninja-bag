from django.shortcuts import render
from django.views import View

from .models import Tool

from utils.decorators import require_http_methods
from utils.views_mixins import GenerateDefaultContext
from utils.mixins import FormSaveMixin
from utils.helpers import Redirector

from .forms import ToolIssueReportForm, SuggestToolForm

from tools.loaders import WhatsMyIp, ProxyAnonymeter, RequestHeaders
from django.http import HttpResponse


def refresh_tools(request):
  WhatsMyIp().store_in_db()
  ProxyAnonymeter().store_in_db()
  RequestHeaders().store_in_db()
  return HttpResponse('<h1>Tools refreshed</h1>')



@require_http_methods(['GET'])
def toggle_color_mode(request):
  response = Redirector.go_previous_page(request)
  cookie_name = 'light-mode'
  cookie_exist = request.COOKIES.get(cookie_name, False)

  if cookie_exist: response.delete_cookie(cookie_name)
  else: response.set_cookie(cookie_name, 'true')

  return response

@require_http_methods(['GET'])
def index(request):
  tools = Tool.objects.list_for_homepage()
  context = GenerateDefaultContext(request)

  context.update({ 'tools': tools })

  return render(request, 'd_homepage.html', context)


@require_http_methods(['GET'])
def get_tool_page(request, tool_id):
  tool = Tool.objects.force_get(tool_id=tool_id)
  db_records = tool.get_db_records(request.user)

  context = GenerateDefaultContext(request)
  context.update({
    'tool': tool, 'db_records': db_records, 'issue_form': ToolIssueReportForm()
  })

  Tool.objects.increase_views_count(pk=tool.pk)

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

