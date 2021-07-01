from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.http import (
  HttpResponseBadRequest,
  HttpResponseNotAllowed,
  HttpResponseForbidden,
  HttpResponseRedirect,
  HttpResponsePermanentRedirect,
)

import json
from datetime import datetime

from classes.JWT import JWTAuth


# may cause error in get params byt i hope not
def extract_request_data(func):
  def wrapper(request, *args, **kwargs):
    method = request.POST if request.method == 'POST' else request.GET
    data = method.dict()
    if not bool(data):
      data = json.loads(request.body.decode('utf8'))
    return func(request, data, *args, **kwargs)
  return wrapper


def is_from_myApp(func):
  @extract_request_data
  def wrapper(request, data, *args, **kwargs):
    appKey = data.get('itsme', '')

    todayDate = datetime.now()
    def sumNumDigits(num): return sum([int(i) for i in str(num)])
    dynamicLength = int(
      f'{sumNumDigits(todayDate.year)}{sumNumDigits(todayDate.month)}{sumNumDigits(todayDate.day)}')

    if dynamicLength != len(appKey):
      return HttpResponseForbidden()

    return func(request, *args, **kwargs)
  return wrapper


def is_account_active(func):
  @is_authorized
  def wrapper(request, *args, **kwargs):
    token = JWTAuth.extractRequestToken(request)

    if not JWTAuth.checkUserTokenIsActiveAccount(token):
      return HttpResponseRedirect('/auth/activate/')

    return func(request, *args, **kwargs)
  return wrapper

def is_authorized(func):
  def wrapper(request, *args, **kwargs):
    token = JWTAuth.extractRequestToken(request)
    if not JWTAuth.checkUserTokenValid(token):
      return HttpResponseForbidden()

    return func(request, *args, **kwargs)
  return wrapper



def extract_post_request_data(func):
  def wrapper(request, *args, **kwargs):

    data = request.POST.dict()
    if not bool(data):
      data = json.loads(request.body.decode('utf8'))

    return func(request, data, *args, **kwargs)
  return wrapper


def check_unique_fields(kls, uniqueFields=[]):
  def decorator(func):
    @extract_post_request_data
    def wrapper(request, data, *args, **kwargs):

      for field in uniqueFields:
        value = data.get(field)
        if kls.objects.filter(**{field: value}).first():
          return HttpResponseBadRequest(f'{field}: "{value}" is already in use')

      return func(request, *args, **kwargs)
    return wrapper
  return decorator


def require_fields(requiredFields=[]):
  def decorator(func):
    @extract_post_request_data
    def wrapper(request, data, *args, **kwargs):

      for field in requiredFields:
        if not data.get(field, None):
          return HttpResponseBadRequest(f'field "{field}" is required')

      return func(request, *args, **kwargs)
    return wrapper
  return decorator


def allow_fields(allowed_fields=[]):
  def decorator(func):
    @extract_post_request_data
    def wrapper(request, data, *args, **kwargs):
      for field in data.keys():
        if field not in allowed_fields:
          return HttpResponseBadRequest(f'field "{field}" is not allowed')

      return func(request, *args, **kwargs)
    return wrapper
  return decorator


def validateToken():
  pass



# cace decorator
def cache_request(name_format, timeout=60*60*24, identifier=None):
  def decorator(func):
    def wrapper(*args, **kwargs):
      name = name_format
      if identifier: 
        name = name_format.format(**{identifier: kwargs[identifier]})

      output = cache.get(name)
      if not output:
        output = func(*args, **kwargs)
        cache.set(name, output, timeout=timeout)

      return output
    return wrapper
  return decorator

from accounts.models import Account
from toolsframe.models import Tool

def tool_handler(limitation=[], pk=None):
  def decorator(func):
    def wrapper(request, *args, **kwargs):
      # need api key or not
      api_key = request.GET.get('token')
      if len(limitation) and not api_key:
        return HttpResponseNotAllowed('token required!!')

      # check if api_key exist
      acc = Account.get_user_by_api_key(api_key)
      if not acc:
        return HttpResponseNotAllowed('not valid token')

      # check if user limits can access the tool or not
      limits = {
        'storage': {
          'before': acc.check_storage_limit_hookbefore,
          'after': lambda x,y: True
        },
        'bandwidth': {
          'before': acc.check_bandwidth_limit_hookbefore,
          'after': acc.check_bandwidth_limit_hookafter,
        },
        'requests': {
          'before': acc.check_requests_limit_hookbefore,
          'after': acc.check_requests_limit_hookafter,
        }
      }

      access_state = [ 
        limits[limit_name]['before'](request)
        for limit_name in limitation
      ]

      # before function # validate limits
      if all(access_state):
        response = func(request, *args, **kwargs)
        # after function # update the limits if success
        for limit_name in limitation:
          limits[limit_name]['after'](request, response)

        if pk != None:
          Tool.increase_uses_count_by_pk(pk)

      else:
        response = HttpResponseBadRequest('there is something wrong')

      return response
    return wrapper
  return decorator

