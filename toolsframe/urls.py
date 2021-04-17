from django.contrib import admin
from django.urls import path

from .views import index, get_tool_page

app_name = 'toolsframe'


urlpatterns = [
  path('', index, name='homepage'),
  # path('', index, name='get-tool'),
  path('tool/<str:tool_id>/', get_tool_page, name='tool'),

  path('facebook-profile-pic/', index, name='fbpp'),
  path('instagram-profile-pic/', index, name='igapp'),
  path('get-my-ip/', index, name='ip'),
  path('get-proxy-anonimity/', index, name='proxy'),
]