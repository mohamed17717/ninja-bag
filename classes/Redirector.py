from django.shortcuts import redirect


class Redirector:
  HOMEPAGE_URL_REVERSER = 'toolsframe:homepage'
  LOGIN_URL_REVERSER = 'accounts:login-page'

  @classmethod
  def go_home(cls):
    return redirect(cls.HOMEPAGE_URL_REVERSER)

  @classmethod
  def go_login(cls):
    return redirect(cls.LOGIN_URL_REVERSER)

