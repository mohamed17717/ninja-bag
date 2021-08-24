from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages

from utils.helpers import Redirector

def index(request):
  response = render(request, 'd_login.html', {})
  if request.user.is_authenticated:
    response = Redirector.go_home()

  return response

def logout_account(request):
  logout(request)
  messages.info(request, "You have successfully logged out.") 
  return Redirector.go_login()

