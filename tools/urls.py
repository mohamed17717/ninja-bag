from django.contrib import admin
from django.urls import path, include

from .views import (
  index,
  get_my_ip,
  get_my_proxy_anonimity,
  get_my_request_headers,
  get_image_placeholder,
  convert_username_to_profile_pic,
  convert_image_to_thumbnail,
  get_fb_user_id,
  remove_image_meta_data
)

app_name = 'tools'


urlpatterns = [
  path('', index, name='tools-home'),

  path('get-my-ip/', get_my_ip, name='get-my-ip'),

  path('get-my-proxy-anonimity/', get_my_proxy_anonimity, name='get-my-proxy-anonimity'),

  path('get-my-request-headers/', get_my_request_headers, name='get-my-request-headers'),

  path('get-image-placeholder/<int:width>x<int:height>/', get_image_placeholder, name='get-image-placeholder1'),
  path('get-image-placeholder/<int:width>/<int:height>/', get_image_placeholder, name='get-image-placeholder2'),
  path('get-image-placeholder/<int:width>x<int:height>/<str:color>/', get_image_placeholder, name='get-image-placeholder3'),
  path('get-image-placeholder/<int:width>/<int:height>/<str:color>/', get_image_placeholder, name='get-image-placeholder4'),

  path('username-to-profile-pic/<int:size>/<str:username>/', convert_username_to_profile_pic, name='username-to-profile-pic1'),
  path('username-to-profile-pic/<int:size>/<str:username>/<str:color>/', convert_username_to_profile_pic, name='username-to-profile-pic2'),
  
  path('image-to-thumbnail/', convert_image_to_thumbnail, name='image-to-thumbnail'),

  path('fb-user-id/', get_fb_user_id, name='fb-user-id'),

  path('remove-image-meta-data/', remove_image_meta_data, name='remove-image-meta-data'),

]
