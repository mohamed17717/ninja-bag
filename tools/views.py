from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from accounts.models import Account
from .models import TextSaverModel
from .controller import RequestAnalyzerTools, ImageTools, ScrapingTools
from .controller.ImageTools import MyImageHandler

from decorators import require_http_methods, tool_handler, required_post_fields, function_nickname
from classes.FileManager import FileManager

import json


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

class TextSaverView:

  @staticmethod
  @require_http_methods(['POST'])
  @tool_handler(limitation=['requests', 'storage', 'bandwidth'])
  @function_nickname('text_saver_add')
  def add(request, file_name=None):
    # get account
    acc = Account.get_user_acc_from_api_or_web(request, required=True)
    text = request.body.decode('utf8')

    file_path = TextSaverModel.add(acc, text, file_name)
    file_full_url = request.build_absolute_uri(file_path)

    return HttpResponse(file_full_url)

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  @function_nickname('text_saver_add')
  def read(request, file_name):
    acc = Account.get_user_acc_from_api_or_web(request, required=True)

    location = TextSaverModel.read(acc, file_name)

    response = HttpResponse(open(location), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    return response

  @staticmethod
  @require_http_methods(['GET'])
  @tool_handler(limitation=['requests', 'bandwidth'])
  @function_nickname('text_saver_add')
  def read_text(request, file_name):
    acc = Account.get_user_acc_from_api_or_web(request, required=True)
    location = TextSaverModel.read(acc, file_name)

    data = FileManager.read(location)

    return HttpResponse(data)


  @staticmethod
  @require_http_methods(['GET', 'DELETE'])
  @tool_handler(limitation=['requests'])
  @function_nickname('text_saver_add')
  def delete(request, file_name):
    acc = Account.get_user_acc_from_api_or_web(request, required=True)

    delete_status = TextSaverModel.delete(acc, file_name)

    response = HttpResponse() if delete_status else HttpResponseBadRequest('file is not exist') 
    if request.user:
      response = redirect(request.META.get('HTTP_REFERER', '/'))
    return response

  @classmethod
  def as_view(cls, request, file_name):
    views = {
      'POST': cls.add,
      'GET': cls.read,
      'DELETE': cls.delete,
    }

    return views.get(request.method)(request, file_name)
