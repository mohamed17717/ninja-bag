from django.shortcuts import redirect


class Redirector:
  HOMEPAGE_URL_REVERSER = 'toolsframe:homepage'
  LOGIN_URL_REVERSER = 'accounts:auth'

  @staticmethod
  def go_home():
    return redirect(Redirector.HOMEPAGE_URL_REVERSER)

  @staticmethod
  def go_login():
    return redirect(Redirector.LOGIN_URL_REVERSER)
