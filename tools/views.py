from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseBadRequest

import json
import re
from random import randint

from PIL import Image
from io import StringIO, BytesIO
import base64



def index(request):
  return HttpResponse('Hiiii')


def get_my_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return HttpResponse(ip)


def get_my_proxy_anonimity(request):
  rename_header = lambda h: f'http-{h}'.upper().replace('-', '_')
  proxy_headers = map(rename_header, [
    # elite
    # Anonymous
    'Authorization', 
    'From', 
    'Proxy-Authorization',
    'Proxy-Connection',
    'Via',
    # transparent
    'X-Forwarded-For'
  ])

  headers = request.META
  found_headers = [h for h in proxy_headers if headers.get(h)]

  anonimity = 'anonymous'
  if len(found_headers) == 0:
    anonimity = 'elite'
  elif rename_header('X-Forwarded-For') in found_headers:
    anonimity = 'transparent'

  return HttpResponse(anonimity)


def get_my_request_headers(request):
  headers = {}

  for key, value in request.META.items():
    if key.startswith('HTTP_'):
      key = key.replace('HTTP_', '')
      headers[key] = value

  return JsonResponse(headers)


def get_image_placeholder(request, width, height, color=None):
  if color == None:
    color = 'rgb({}, {}, {})'.format(*[randint(0, 255) for _ in range(3)])
  elif not (re.fullmatch(r'[a-z]+', color) or color.startswith('rgb')):
    color = f'#{color}'

  try:
    red = Image.new('RGB', (width, height), color)
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "jpeg")
  except Exception as e:
    response = HttpResponseBadRequest(e)
  return response