from django.contrib import admin
from django.urls import path, include

from .views import index, get_my_ip

app_name = 'tools'


urlpatterns = [
  path('', index, name='tools-home'),

  path('get-my-ip/', get_my_ip, name='get-my-ip'),
]
