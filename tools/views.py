from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator

import json
import re
import requests
from random import randint

from PIL import Image, ImageDraw, ImageFont
from io import StringIO, BytesIO
import base64

import qrcode

from .classes.MyImageHandler import MyImageHandler
from .classes.Social import Facebook
from .classes.helpers import ua_details

from decorators import require_http_methods, tool_handler

def index(request):
  return HttpResponse('Hiiii')


@require_http_methods(['GET'])
@tool_handler(limitation=[])
def get_my_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return HttpResponse(ip)


@require_http_methods(['GET'])
@tool_handler(limitation=[])
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


@require_http_methods(['GET'])
@tool_handler(limitation=[])
def get_my_request_headers(request):
  headers = {}

  for key, value in request.META.items():
    if key.startswith('HTTP_'):
      key = key.replace('HTTP_', '')
      headers[key] = value

  return JsonResponse(headers)


@require_http_methods(['GET'])
@tool_handler(limitation=['requests', 'bandwidth'])
def get_image_placeholder(request, width, height, color=None):
  color = MyImageHandler.handle_user_color(color)

  try:
    image = Image.new('RGB', (width, height), color)
    response = MyImageHandler.image_response(image)
  except Exception as e:
    response = HttpResponseBadRequest(e)

  return response


@require_http_methods(['GET'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_username_to_profile_pic(request, size, username, color=None):
  color = MyImageHandler.handle_user_color(color)
  text_color = MyImageHandler.get_color_best_contrast_bw(color)
  width = height = size
  text = ''.join([name[0] for name in username.split(' ')[:2]]).upper()

  try:
    image = Image.new('RGB', (width, height), color)

    # setup text
    draw = ImageDraw.Draw(image)
    # font
    fontsize = int(size * 2/4)
    font = ImageFont.truetype('./static/fonts/Nonserif.ttf', fontsize)
    # position text
    textwidth, textheight = draw.textsize(text, font=font)
    x = (width - textwidth) / 2
    y = (height - textheight) / 2 - (size*20/400)
    # draw text
    draw.text((x, y), text, fill=text_color, font=font)

    response = MyImageHandler.image_response(image)
  except Exception as e:
    response = HttpResponseBadRequest(e)

  return response


@require_http_methods(['POST'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_image_to_thumbnail(request):
  image_file = request.FILES.get('image')
  new_width = int(request.POST.get('width') or 128)

  if not image_file:
    response = HttpResponse('make sure you name input "image"')
  else:
    image = Image.open(image_file)
    width, height = image.size
    new_height = new_width * height / width
    image.thumbnail((new_width, new_height), Image.ANTIALIAS)

    response = MyImageHandler.image_response(image)

  return response


@require_http_methods(['POST'])
@tool_handler(limitation=['requests'])
def get_fb_user_id(request):
  acc_url = request.POST.get('url')
  acc = Facebook(acc_url)
  user_id = acc.get_fb_user_id()

  return HttpResponse(user_id or 'Not Found')


@require_http_methods(['POST'])
@tool_handler(limitation=['requests', 'bandwidth'])
def remove_image_meta_data(request):
  image_file = request.FILES.get('image')

  if not image_file:
    response = HttpResponse('make sure you name input "image"')
  else:
    image = Image.open(image_file)

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    response = MyImageHandler.image_response(image_without_exif)

  return response


@require_http_methods(['POST'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_image_to_b64(request):
  image_file = request.FILES.get('image')
  image_name = image_file.name

  image_ext = 'jpeg'
  if '.' in image_name:
    image_ext = image_name.split('.')[-1]

  image_b64 = base64.b64encode(image_file.read())
  image_b64 = str(image_b64)[2:-1]

  prefix = f'data:image/{image_ext};base64,'
  return HttpResponse(prefix + image_b64)

@require_http_methods(['POST'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_b64_to_image(request):
  image_b64 = request.POST.get('image')
  if not image_b64:
    return HttpResponseBadRequest('missing field "image"')

  image_b64 = re.sub(r'^data:image/\w+?;base64,', '', image_b64)
  try: 
    image = Image.open(BytesIO(base64.b64decode(image_b64)))
    response = MyImageHandler.image_response(image)
  except:
    response = HttpResponseBadRequest('Not valid image')
  
  return response


def unshorten_url(full_track=False):

  @require_http_methods(['POST'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  def wrapper(request):
    shortened_url = request.POST.get('url')

    if shortened_url:
      try:
        res = requests.head(shortened_url, allow_redirects=True)
        if full_track:
          response = JsonResponse([r.url for r in res.history] + [res.url], safe=False)
        else:
          response = HttpResponse(res.url)

      except requests.exceptions.MissingSchema:
        response = HttpResponseBadRequest('you must provide protocol for the url')
    else:
      response = HttpResponseBadRequest('missing url in post body')

    return response
  return wrapper


@tool_handler(limitation=['requests'])
def get_user_agent_details(request):
  if request.method == 'GET':
    ua = request.META['HTTP_USER_AGENT']
  elif request.method == 'POST':
    ua = request.POST.get('user-agent')

  if ua:
    data = ua_details(ua)
    response = JsonResponse(data, safe=False)
  else:
    response = HttpResponseBadRequest('missed post key "user-agnet"')

  return response


@require_http_methods(['POST'])
@tool_handler(limitation=['requests', 'bandwidth'])
def generate_qrcode(request):
  string = request.POST.get('text')
  if not string:
    return HttpResponseBadRequest('missing field "text"')

  image = qrcode.make(string)
  response = MyImageHandler.image_response(image)

  return response
