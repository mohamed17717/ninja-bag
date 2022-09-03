from django.urls import path

from .views import index, get_tool_page, SuggestTool, ReportToolIssue, toggle_color_mode, PrivacyPolicyView

app_name = 'toolsframe'

urlpatterns = [
  path('', index, name='homepage'),
  path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),

  path('toggle-color-mode/', toggle_color_mode, name='toggle-color'),
  path('tool/<str:tool_id>/', get_tool_page, name='tool'),
  path('suggest-tool/', SuggestTool.as_view(), name='suggest-tool'),
  path('report-tool/<str:tool_id>/', ReportToolIssue.as_view(), name='report-tool')
]
