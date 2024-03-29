from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.conf import settings

from app import models
import json

from urllib.parse import urlparse
import json, sys

from django.contrib.auth import get_user_model


User = get_user_model()

def dumps(value):
  return json.dumps(value,default=lambda o:None)

class RequestBodyToDataMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    return self.get_response(request)

  def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'data'):
      request_body = request.body
      try: request_body = request_body.decode('utf8')
      except: pass

      setattr(request,'data', request_body)

class WebRequestMiddleware(object):
  def process_view(self, request, view_func, view_args, view_kwargs):
    setattr(request,'hide_post',view_kwargs.pop('hide_post',False))

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    response = self.get_response(request)
    return self.process_response(request, response)

  # def process_exception(self, request, exception): 
  #   return HttpResponse("in exception")

  def process_response(self, request, response):
    if request.path.endswith('/favicon.ico'):
      return response

    if type(response) == HttpResponsePermanentRedirect and settings.APPEND_SLASH:
      new_location = response.get('location',None)
      content_length = response.get('content-length',None)

      if new_location and content_length == '0':
        new_parsed = urlparse(new_location)

        old = (('http','https')[request.is_secure()], request.get_host(), '{0}/'.format(request.path), request.META['QUERY_STRING'])
        new = (new_parsed.scheme, new_parsed.netloc, new_parsed.path, new_parsed.query)

        if old == new:
          #don't log - it's just adding a /
          return response
    try:
      self.save(request, response)
    except Exception as e:
      print("Error saving request log", e, file=sys.stderr)

    return response

  def save(self, request, response):
    user = None
    if hasattr(request, 'user'):
      user = request.user if request.user.is_authenticated else None

    meta = request.META.copy()
    meta.pop('QUERY_STRING',None)
    meta.pop('HTTP_COOKIE',None)
    remote_addr_fwd = None

    if 'HTTP_X_FORWARDED_FOR' in meta:
      remote_addr_fwd = meta['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
      if remote_addr_fwd == meta['HTTP_X_FORWARDED_FOR']:
        meta.pop('HTTP_X_FORWARDED_FOR')
    remote_addr = meta.pop('REMOTE_ADDR', None) or meta.pop('HTTP_X_REAL_IP', None) or remote_addr_fwd

    post = None
    uri = request.build_absolute_uri()
    if request.POST and getattr(request,'hide_post') != True:
      post = dumps(request.POST)

    models.WebRequest(
      host = request.get_host(),
      path = request.path,
      method = request.method,
      uri = uri,
      status_code = response.status_code,
      user_agent = meta.pop('HTTP_USER_AGENT',None),
      remote_addr = remote_addr,
      remote_addr_fwd = remote_addr_fwd,
      meta = None if not meta else dumps(meta),
      cookies = None if not request.COOKIES else dumps(request.COOKIES),
      get = None if not request.GET else dumps(request.GET),
      post = post,
      raw_post = None,
      is_secure = request.is_secure(),
      user = user
    ).save()

