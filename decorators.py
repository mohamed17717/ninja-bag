from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.http import (
  HttpResponseBadRequest, HttpResponseNotAllowed )

from accounts.models import Account
from toolsframe.models import Tool

import json


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


def required_post_fields(required_fields=[]):
  def decorator(func):

    def wrapper(request, data, *args, **kwargs):
      posted_fields = request.POST.dict().keys()

      error_response = lambda field: HttpResponseBadRequest(f'field "{field}" is required.')
      for required_field in required_fields:
        if required_field not in posted_fields:
          return error_response(required_field)

      return func(request, *args, **kwargs)

    return wrapper
  return decorator

