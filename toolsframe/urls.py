from django.contrib import admin
from django.urls import path, include

from .views import index, get_tool_page

app_name = 'toolsframe'


urlpatterns = [
  path('', index, name='homepage'),
  path('tool/<str:tool_id>/', get_tool_page, name='tool'),
]
