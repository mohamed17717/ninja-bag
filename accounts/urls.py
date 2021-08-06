from django.contrib import admin
from django.urls import path

from .views import (
  index,
  logout_account
)

app_name = 'accounts'


urlpatterns = [
  path('', index, name='login-page'),
  path('logout/', logout_account, name='logout'),
]