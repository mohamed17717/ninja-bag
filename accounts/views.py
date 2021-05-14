from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterAccountForm


def index(request):
  return HttpResponse('Welcome accounts')

def go_homepage():
  return redirect('toolsframe:homepage')

def go_login():
  return redirect('accounts:login')


class register_account(View):
  def get(self, request, form=None):
    if request.user.is_authenticated:
      return go_homepage()

    context = { 'register_form': form or RegisterAccountForm }
    return render(request, 'register.html', context)


  def post(self, request):
    if request.user.is_authenticated:
      return go_homepage()

    form = RegisterAccountForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      messages.success(request, 'Registration successful.' )
      return go_homepage()

    messages.error(request, 'Unsuccessful registration. Invalid information.')
    return self.get(request, form)


class login_account(View):
  def get(self, request, form=None):
    if request.user.is_authenticated:
      return go_homepage()

    context = { 'login_form': form or AuthenticationForm() }
    return render(request, 'login.html', context)

  def post(self, request):
    if request.user.is_authenticated:
      return go_homepage()

    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(username=username, password=password)
      if user is not None:
        login(request, user)
        return go_homepage()

    messages.error(request,'Invalid username or password.')
    return self.get(request, form)


def logout_account(request):
  logout(request)
  messages.info(request, "You have successfully logged out.") 
  return go_login()

