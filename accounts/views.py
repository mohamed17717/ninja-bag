from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterAccountForm

from classes.Redirector import Redirector

def index(request):
  response = render(request, 'd_login.html', {})
  if request.user.is_authenticated:
    response = Redirector.go_home()

  return response

def logout_account(request):
  logout(request)
  messages.info(request, "You have successfully logged out.") 
  return Redirector.go_login()


class register_account(View):
  def get(self, request, form=None):
    if request.user.is_authenticated:
      return Redirector.go_home()

    context = { 'register_form': form or RegisterAccountForm }
    return render(request, 'register.html', context)


  def post(self, request):
    if request.user.is_authenticated:
      return Redirector.go_home()

    form = RegisterAccountForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, 'Registration successful.' )
      return Redirector.go_home()

    messages.error(request, 'Unsuccessful registration. Invalid information.')
    return self.get(request, form)


class login_account(View):
  def get(self, request, form=None):
    if request.user.is_authenticated:
      return Redirector.go_home()

    context = { 'login_form': form or AuthenticationForm() }
    return render(request, 'login.html', context)

  def post(self, request):
    if request.user.is_authenticated:
      return Redirector.go_home()

    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(username=username, password=password)
      if user is not None:
        login(request, user)
        return Redirector.go_home()

    messages.error(request,'Invalid username or password.')
    return self.get(request, form)
