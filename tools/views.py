from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseBadRequest

import json
import re
from random import randint

from PIL import Image, ImageDraw, ImageFont
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


def calc_random_color(color):
  # it must return tuple of 3 nums
  #  it must be another function convert tuple to rgb(x,y,z) format
  calculated_color = color
  if color == None:
    calculated_color = 'rgb({}, {}, {})'.format(*[randint(0, 255) for _ in range(3)])
  elif not (re.fullmatch(r'[a-z]+', color) or color.startswith('rgb')):
    calculated_color = f'#{color}'

  return calculated_color

def contrast_color(color):
  nums = list(map(int, color[4:-1].replace(' ', '').split(',')))
  avr = sum(nums) / len(nums)

  contrast_color = (0,0,0)
  if avr <= 127.5:
    contrast_color = (255,255,255)

  return contrast_color


def get_image_placeholder(request, width, height, color=None):
  color = calc_random_color(color)

  try:
    image = Image.new('RGB', (width, height), color)

    response = HttpResponse(content_type="image/jpeg")
    image.save(response, "jpeg")
  except Exception as e:
    response = HttpResponseBadRequest(e)
  return response


def convert_username_to_profile_pic(request, size, username, color=None):
  color = calc_random_color(color)
  text_color = (0, 0, 0)
  if color.startswith('rgb('):
    text_color = contrast_color(color)

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

    response = HttpResponse(content_type="image/jpeg")
    image.save(response, "jpeg")
  except Exception as e:
    response = HttpResponseBadRequest(e)

  return response


def convert_image_to_thumbnail(request):
  if request.method == 'GET':
    response = render(request, 'test.html')

  elif request.method == 'POST':
    image = request.FILES.get('image')
    new_width = int(request.POST.get('width') or 128)

    if not image:
      response = HttpResponse('make sure you name input "image"')
    else:
      im = Image.open(image)
      width, height = im.size
      new_height = new_width * height / width

      # convert to thumbnail image
      im.thumbnail((new_width, new_height), Image.ANTIALIAS)

      response = HttpResponse(content_type="image/jpeg")
      im.save(response, "jpeg")

  return response
