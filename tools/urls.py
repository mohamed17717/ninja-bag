from django.contrib import admin
from django.urls import path, include

from .views import (
  get_my_ip,
  get_my_proxy_anonymity,
  get_my_request_headers,
  get_image_placeholder,
  convert_username_to_profile_pic,
  convert_image_to_thumbnail,
  get_fb_user_id,
  remove_image_meta_data,
  convert_image_to_b64,
  convert_b64_to_image,
  unshorten_url_wrapper,
  analyze_user_agent,
  analyze_my_machine_user_agent,
  generate_qrcode,
  cors_proxy,
  TextSaverView,
)

app_name = 'tools'


urlpatterns = [
  path('get-my-ip/', get_my_ip, name='get-my-ip'),

  path('get-my-proxy-anonymity/', get_my_proxy_anonymity, name='get-my-proxy-anonymity'),

  path('get-my-request-headers/', get_my_request_headers, name='get-my-request-headers'),

  path('analyze-my-machine/', analyze_my_machine_user_agent, name='analyze-my-machine'),
  path('analyze-user-agent/', analyze_user_agent, name='analyze-user-agent'),

  path('get-image-placeholder/<int:width>/', get_image_placeholder, name='get-image-placeholder5'),
  path('get-image-placeholder/<int:width>/<str:color>/', get_image_placeholder, name='get-image-placeholder5'),
  path('get-image-placeholder/<int:width>x<int:height>/', get_image_placeholder, name='get-image-placeholder1'),
  path('get-image-placeholder/<int:width>x<int:height>/<str:color>/', get_image_placeholder, name='get-image-placeholder3'),

  path('username-to-profile-pic/<int:size>/<str:username>/', convert_username_to_profile_pic, name='username-to-profile-pic1'),
  path('username-to-profile-pic/<int:size>/<str:username>/<str:color>/', convert_username_to_profile_pic, name='username-to-profile-pic2'),
  
  path('image-to-thumbnail/', convert_image_to_thumbnail, name='image-to-thumbnail'),

  path('remove-image-meta-data/', remove_image_meta_data, name='remove-image-meta-data'),

  path('image-to-b64/', convert_image_to_b64, name='image-to-b64'),
  path('b64-to-image/', convert_b64_to_image, name='b64-to-image'),

  path('gen-qrcode/', generate_qrcode, name='gen-qrcode'),

  path('fb-user-id/', get_fb_user_id, name='fb-user-id'),

  path('cors-proxy/', cors_proxy, name='cors-proxy'),

  path('unshorten-url/', unshorten_url_wrapper(full_track=False), name='unshorten-url'),
  path('unshorten-url/full-track/', unshorten_url_wrapper(full_track=True), name='unshorten-url'),

  path('save-text/<str:file_name>/', TextSaverView.as_view, name='textsaver'),
  path('save-text/', TextSaverView.add, name='textsaver-create'),
  path('save-text/delete/<str:file_name>/', TextSaverView.delete, name='textsaver-delete'),
  path('save-text/read/<str:file_name>/', TextSaverView.read, name='textsaver-read'),
  path('save-text/read-text/<str:file_name>/', TextSaverView.read_text, name='textsaver-read-text'),
]
