from django.urls import path

from tools import views

app_name = 'tools'

from . import WhatsMyIp, ProxyAnonymeter, RequestHeaders



urlpatterns = [
  # path('get-my-ip/', views.get_my_ip, name='get-my-ip'),
  *WhatsMyIp().get_endpoints_paths(),

  # path('get-my-proxy-anonymity/', views.get_my_proxy_anonymity, name='get-my-proxy-anonymity'),
  *ProxyAnonymeter().get_endpoints_paths(),

  # path('get-my-request-headers/', views.get_my_request_headers, name='get-my-request-headers'),
  *RequestHeaders().get_endpoints_paths(),

  path('analyze-my-machine/', views.analyze_my_machine_user_agent, name='analyze-my-machine'),
  path('analyze-user-agent/', views.analyze_user_agent, name='analyze-user-agent'),

  path('get-image-placeholder/<int:width>/', views.get_image_placeholder, name='get-image-placeholder5'),
  path('get-image-placeholder/<int:width>/<str:color>/', views.get_image_placeholder, name='get-image-placeholder5'),
  path('get-image-placeholder/<int:width>x<int:height>/', views.get_image_placeholder, name='get-image-placeholder1'),
  path('get-image-placeholder/<int:width>x<int:height>/<str:color>/', views.get_image_placeholder, name='get-image-placeholder3'),

  path('username-to-profile-pic/<int:size>/<str:username>/', views.convert_username_to_profile_pic, name='username-to-profile-pic1'),
  path('username-to-profile-pic/<int:size>/<str:username>/<str:color>/', views.convert_username_to_profile_pic, name='username-to-profile-pic2'),
  
  path('image-to-thumbnail/', views.convert_image_to_thumbnail, name='image-to-thumbnail'),

  path('remove-image-meta-data/', views.remove_image_meta_data, name='remove-image-meta-data'),

  path('image-to-b64/', views.convert_image_to_b64, name='image-to-b64'),
  path('b64-to-image/', views.convert_b64_to_image, name='b64-to-image'),

  path('gen-qrcode/', views.generate_qrcode, name='gen-qrcode'),

  path('fb-user-id/', views.get_fb_user_id, name='fb-user-id'),

  path('cors-proxy/', views.cors_proxy, name='cors-proxy'),

  path('unshorten-url/', views.unshorten_url_wrapper(full_track=False), name='unshorten-url'),
  path('unshorten-url/full-track/', views.unshorten_url_wrapper(full_track=True), name='unshorten-url'),

  path('save-text/<str:file_name>/', views.TextSaverView.as_view, name='textsaver'),
  path('save-text/', views.TextSaverView.add, name='textsaver-create'),
  path('save-text/delete/<str:file_name>/', views.TextSaverView.delete, name='textsaver-delete'),
  path('save-text/read/<str:file_name>/', views.TextSaverView.read, name='textsaver-read'),
  path('save-text/read-text/<str:file_name>/', views.TextSaverView.read_text, name='textsaver-read-text'),
  path('save-text/check-line-exist/<str:file_name>/', views.TextSaverView.check_line_exist, name='textsaver-check-line-exist'),

  # not described yet
  path('fhost/<str:file_name>/', views.get_fhost, name='fhost'),
  path('yt/audio/', views.convert_youtube_video_to_stream_audio, name='youtube-audio-stream'),

]
