from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator

import json
import re
import requests
from random import randint
import secrets

from PIL import Image, ImageDraw, ImageFont
from io import StringIO, BytesIO
import base64

import qrcode

from .classes.MyImageHandler import MyImageHandler
from .classes.Social import Facebook
from .classes.helpers import ua_details
from .classes.FileManager import FileManager

from decorators import require_http_methods, tool_handler

from accounts.models import Account

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


class TextSaver:
  @staticmethod
  def get_account(request):
    token = request.GET.get('token')
    acc = Account.get_user_by_api_key(token)
    return acc

  @staticmethod
  def get_folder(acc):
    return acc.get_user_folder_location() + 'text-saver/'

  @staticmethod
  def get_file_url(request, file_name):
    path = reverse('tools:textsaver-read', kwargs={'file_name': file_name})
    url = request.build_absolute_uri(path)
    return url

  @staticmethod
  @require_http_methods(['POST'])
  @tool_handler(limitation=['requests', 'bandwidth', 'storage'])
  def add(request, file_name=None):
    acc = TextSaver.get_account(request)
    fm = FileManager()

    text = request.POST.get('text')
    if not text:
      return HttpResponseBadRequest('missing field "text"')

    file_name = file_name or f'{secrets.token_hex(nbytes=8)}.txt'

    location = TextSaver.get_folder(acc) + file_name
    fm.write(location, text+'\n', mode='a', force_location=True)

    file_url = TextSaver.get_file_url(request, file_name)
    return HttpResponse(file_url)

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  def read(request, file_name):
    acc = TextSaver.get_account(request)
    location = TextSaver.get_folder(acc) + file_name

    response = HttpResponse(open(location), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests'])
  def delete(request, file_name):
    acc = TextSaver.get_account(request)
    location = TextSaver.get_folder(acc) + file_name

    fm = FileManager()
    delete_status = fm.delete(location)

    if delete_status: reponse = HttpResponse(status=200)
    else: reponse = HttpResponseBadRequest('filename is not exist')

    return reponse

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests'])
  def list_all(request):
    acc = TextSaver.get_account(request)
    location = TextSaver.get_folder(acc)

    fm = FileManager()
    files_names = fm.listdir(location)

    files_urls = list(map(lambda fn: TextSaver.get_file_url(request, fn), files_names))
    return JsonResponse(files_urls, safe=False)

  @staticmethod
  def action_handler(request, file_name):
    if request.method == 'GET':
      response = TextSaver.read(request, file_name)
    elif request.method == 'POST':
      response = TextSaver.add(request, file_name)
    return response


class CorsProxy:
  def __init__(self, request):
    self.request = request

  def __get_body(self):
    body = self.request.body.decode('utf8')
  
    try: body = json.loads(body)
    except: pass

    return body

  def __get_headers(self):
    headers = self.request.headers
    not_allowed_headers = [
      'Host','Origin','Sec-Fetch-Sit',
      'Sec-Fetch-Mode','Sec-Fetch-Dest','Referer',
      'Sec-Fetch-Site','Content-Length', # 'Content-Type'
    ]

    new_headers = {}
    for h, v in headers.items():
      if h in not_allowed_headers: continue
      new_headers[h] = v

    return new_headers

  def __get_request_params(self, url, method, headers, cookies, body):
    request_params = { 'url': url, 'headers': headers }
    if body:
      key = 'data'
      if headers['Content-Type'].lower() == 'application/json':
        key = 'json'
      
      request_params.update({ key: body })

    return request_params

  def __get_method_function(self, method):
    return eval(f'requests.{method.lower()}')

  def simulate_request(self):
    url = self.request.GET.get('url')
    method = self.request.method
    headers = self.__get_headers()
    cookies = self.request.COOKIES
    body = self.__get_body()

    request_params = self.__get_request_params(url, method, headers, cookies, body)

    method_func = self.__get_method_function(method)
    response = method_func(**request_params)

    return response

  def simulate_response(self, res):
    response = HttpResponse(
      content=res.text, 
      status=res.status_code, 
      content_type=res.headers['Content-Type']
    )
    return response

  @staticmethod
  @tool_handler(limitation=['requests', 'bandwidth'])
  def proxy(request):
    cors = CorsProxy(request)

    res = cors.simulate_request()
    reponse = cors.simulate_response(res)

    return reponse

