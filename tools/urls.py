from django.contrib import admin
from django.urls import path, include

from .views import index, get_my_ip, get_my_proxy_anonimity, get_my_request_headers

app_name = 'tools'


urlpatterns = [
  path('', index, name='tools-home'),

  path('get-my-ip/', get_my_ip, name='get-my-ip'),
  path('get-my-proxy-anonimity/', get_my_proxy_anonimity, name='get-my-proxy-anonimity'),
  path('get-my-request-headers/', get_my_request_headers, name='get-my-request-headers'),
]
