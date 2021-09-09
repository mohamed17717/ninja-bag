from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages

from utils.helpers import Redirector
from utils.views_mixins import GenerateRequestContext

def index(request):
  response = render(request, 'd_login.html', GenerateRequestContext(request))
  if request.user.is_authenticated:
    response = Redirector.go_home()

  return response

def logout_account(request):
  logout(request)
  messages.info(request, "You have successfully logged out.") 
  return Redirector.go_login()

