from django.urls import path

from tools import views

from .loaders import load_tool_classes

app_name = 'tools'

urlpatterns = [
  path('', views.nothing, name='tool-parent-path'),

  # not described yet
  path('fhost/<str:file_name>/', views.get_fhost, name='fhost'),
  path('yt/audio/', views.convert_youtube_video_to_stream_audio, name='youtube-audio-stream'),

]

for tool_class in load_tool_classes():
  endpoints = tool_class().get_endpoints_paths()
  urlpatterns.extend(endpoints)
