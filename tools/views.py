from django.shortcuts import render, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from accounts.models import Account

from decorators import require_http_methods, tool_handler, required_post_fields

from .classes.FileManager import FileManager
from .controller import RequestAnalyzerTools, ImageTools, ScrapingTools
from .controller.ImageTools import MyImageHandler

import json, secrets, os


def index(request):
  return render(request, 'test.html')


#--------------------- start RequestAnalyzer tools ---------------------#

@require_http_methods(['GET'])
@tool_handler(limitation=[])
def get_my_ip(request):
  ip = RequestAnalyzerTools.get_ip(request)
  return HttpResponse(ip)


@require_http_methods(['GET'])
@tool_handler(limitation=[])
def get_my_proxy_anonimity(request):
  anonimity = RequestAnalyzerTools.get_proxy_anonimity(request)
  return HttpResponse(anonimity)


@require_http_methods(['GET'])
@tool_handler(limitation=[])
def get_my_request_headers(request):
  headers = RequestAnalyzerTools.get_request_headers(request)
  return JsonResponse(headers, safe=False, json_dumps_params={'indent': 2})


@require_http_methods(['GET'])
@tool_handler(limitation=['requests'])
def analyze_my_machine_user_agent(request):
  ua = request.META['HTTP_USER_AGENT']
  ua_details = RequestAnalyzerTools.get_user_agent_details(ua)

  return JsonResponse(ua_details, safe=False, json_dumps_params={'indent': 2})


@require_http_methods(['POST'])
@required_post_fields(['user-agent'])
@tool_handler(limitation=['requests'])
def analyze_user_agent(request):
  request_data = json.loads(request.body.decode('utf8')) or request.POST
  ua = request_data.get('user-agent')
  ua_details = RequestAnalyzerTools.get_user_agent_details(ua)

  return JsonResponse(ua_details, safe=False, json_dumps_params={'indent': 2})

#--------------------- end RequestAnalyzer tools ---------------------#



#--------------------- start Images tools ---------------------#

@require_http_methods(['GET'])
@tool_handler(limitation=['requests', 'bandwidth'])
def get_image_placeholder(request, width, height=None, color=None):
  color = MyImageHandler.handle_color(color)
  height = height or width

  image = MyImageHandler.generate_placeholder_image(width, height, color)
  response = MyImageHandler.image_response(image)

  return response


@require_http_methods(['GET'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_username_to_profile_pic(request, size, username, color=None):
  color = MyImageHandler.handle_color(color)

  image = MyImageHandler.generate_avatar_image(size, username, color)
  response = MyImageHandler.image_response(image)

  return response


@require_http_methods(['POST'])
@required_post_fields(['image'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_image_to_thumbnail(request):
  image_file = request.FILES.get('image')
  new_width = int(request.POST.get('width') or 128)

  image = MyImageHandler.generate_thumbnail(image_file, new_width)

  return MyImageHandler.image_response(image)


@require_http_methods(['POST'])
@required_post_fields(['image'])
@tool_handler(limitation=['requests', 'bandwidth'])
def remove_image_meta_data(request):
  image_file = request.FILES.get('image')

  image = MyImageHandler.generate_cleaned_image_form_exif(image_file)

  return MyImageHandler.image_response(image)


@require_http_methods(['POST'])
@required_post_fields(['image'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_image_to_b64(request):
  image_file = request.FILES.get('image')

  b64 = MyImageHandler.generate_b64_from_image(image_file)

  return HttpResponse(b64)

@require_http_methods(['POST'])
@required_post_fields(['image'])
@tool_handler(limitation=['requests', 'bandwidth'])
def convert_b64_to_image(request):
  request_data = json.loads(request.body.decode('utf8')) or request.POST
  image_b64 = request_data.get('image')

  image = MyImageHandler.generate_image_from_b64(image_b64)
  response = MyImageHandler.image_response(image)

  return response


@require_http_methods(['POST'])
@required_post_fields(['text'])
@tool_handler(limitation=['requests', 'bandwidth'])
def generate_qrcode(request):
  request_data = json.loads(request.body.decode('utf8')) or request.POST
  string = request_data.get('text')

  image = MyImageHandler.generate_qr_code(string)

  return MyImageHandler.image_response(image)

#--------------------- end Images tools ---------------------#



#--------------------- start scraping tools ---------------------#

@require_http_methods(['POST'])
@required_post_fields(['url'])
@tool_handler(limitation=['requests'])
def get_fb_user_id(request):
  request_data = json.loads(request.body.decode('utf8')) or request.POST
  acc_url = request_data.get('url')

  user_id = ScrapingTools.get_fb_user_id(acc_url)  or 'Not Found'

  return HttpResponse(user_id)

@tool_handler(limitation=['requests', 'bandwidth'])
def cors_proxy(request):
  cors = ScrapingTools.CorsProxy(request)

  res = cors.simulate_request()
  response = cors.simulate_response(res)

  return response

def unshorten_url_wrapper(full_track=False):
  get_response = lambda track: JsonResponse(track, safe=False, json_dumps_params={'indent': 2}) if full_track else HttpResponse(track[-1])

  @require_http_methods(['POST'])
  @required_post_fields(['url'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  def unshorten_url(request):
    request_data = json.loads(request.body.decode('utf8')) or request.POST
    shortened_url = request_data.get('url')

    track = ScrapingTools.get_url_redirect_track(shortened_url)

    return get_response(track)
  return unshorten_url

#--------------------- end scraping tools ---------------------#


class TextSaver:
  @staticmethod
  def get_account(request):
    token = request.GET.get('token')
    acc = Account.get_user_by_api_key(token)

    if not acc:
      raise PermissionDenied('Token is not valid.')

    return acc

  @staticmethod
  def get_folder(acc):
    user_folder = acc.get_user_folder_location()
    location = os.path.join(user_folder, 'text-saver/')
    return location

  @staticmethod
  def get_file_url(request, file_name):
    path = reverse('tools:textsaver-read', kwargs={'file_name': file_name})
    url = request.build_absolute_uri(path)
    return url

  @staticmethod
  def get_text(request):
    data = request.POST.dict()

    if len(data) == 1 and 'text' in data.keys():
      text = data.get('text')
    elif len(data) >= 1:
      text = json.dumps(data)
    else:
      text = request.body.encode('utf8')

    return text

  @staticmethod
  @require_http_methods(['POST'])
  @tool_handler(limitation=['requests', 'bandwidth', 'storage'])
  def add(request, file_name=None):
    if '/' in file_name:
      return HttpResponseBadRequest(f'filename "{file_name}" is not valid.')

    acc = TextSaver.get_account(request)
    fm = FileManager()

    text = TextSaver.get_text(request)
    if not text:
      return HttpResponseBadRequest('cant find any text in the reponse')

    file_name = file_name or f'{secrets.token_hex(nbytes=8)}.txt'
    location = os.join.path(TextSaver.get_folder(acc), file_name)
    fm.write(location, text+'\n', mode='a', force_location=True)

    file_url = TextSaver.get_file_url(request, file_name)
    return HttpResponse(file_url)

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  def read(request, file_name):
    if '/' in file_name:
      return HttpResponseBadRequest(f'filename "{file_name}" is not valid.')

    acc = TextSaver.get_account(request) # request.user (required)
    fm = FileManager()
    location = os.join.path(TextSaver.get_folder(acc), file_name)

    if fm.is_file_exist(location):
      response = HttpResponse(open(location), content_type='application/text charset=utf-8')
      response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    else:
      response = HttpResponseBadRequest('file is not exist.')

    return response

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests'])
  def delete(request, file_name):
    if '/' in file_name:
      return HttpResponseBadRequest(f'filename "{file_name}" is not valid.')

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
    return JsonResponse(files_urls, safe=False, json_dumps_params={'indent': 2})

  @staticmethod
  def action_handler(request, file_name):
    if request.method == 'GET':
      response = TextSaver.read(request, file_name)
    elif request.method == 'POST':
      response = TextSaver.add(request, file_name)
    return response

