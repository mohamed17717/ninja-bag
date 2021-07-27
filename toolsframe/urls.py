from django.contrib import admin
from django.urls import path, include

from .views import index, get_tool_page, suggest_tool, report_tool_issue

app_name = 'toolsframe'


urlpatterns = [
  path('', index, name='homepage'),
  path('tool/<str:tool_id>/', get_tool_page, name='tool'),
  path('suggest-tool/', suggest_tool, name='suggest-tool'),
  path('report-tool/<str:tool_id>/', report_tool_issue, name='report-tool')
]
