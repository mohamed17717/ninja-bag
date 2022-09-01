from django.utils.text import slugify
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import path
from django.shortcuts import resolve_url

from abc import ABC, abstractmethod, abstractproperty
from enum import Enum

from utils.decorators import require_http_methods_for_class, required_post_fields_for_class
from utils.views_mixins import JsonResponseOverride, ImageResponse
from utils.mixins import ExtractPostRequestData
from utils.helpers import FileManager, Redirector

from .controller import RequestAnalyzerTools
from .controller.ImageTools import MyImageHandler
from .controller import ScrapingTools
from .models import TextSaverModel

from accounts.models import Account


class ToolAccessType(Enum):
  # show in homepage as an api that you can test
  api = 1 
  # show in homepage but its not provide in api
  # it has a fully UI that you will use it from
  web = 2
  # not shown in homepage i am only the one who can use it
  hidden = 3

class Endpoint:
  def __init__(self, data):
    self.data = data

  def get_path(self):
    url = self.data['path'].strip('/') + '/'
    path_name = self.data['path_name'].split(':').pop()
    return path(url, self.data['view'], name=path_name)

  def get_docs(self):
    docs_dict = { **self.data } 
    docs_dict.pop('view')
    try:
      url = resolve_url(self.data['path_name'])
    except:
      url = self.data['path']
      parent_url = resolve_url('tools:tool-parent-path').strip('/')
      url = f'/{parent_url}' + url.replace('<int:', '{').replace('<str:', '{').replace('>', '}')

    docs_dict.update({'url': url})
    return docs_dict

class ToolAbstract(ABC):
  @abstractproperty
  def name(self) -> str: pass

  @abstractproperty
  def description(self) -> str: pass

  @abstractproperty
  def categories(self) -> list: pass

  @abstractproperty
  def access_type(self) -> int: pass

  @abstractproperty
  def login_required(self) -> bool: pass

  @abstractproperty
  def active(self) -> bool: pass

  @property
  def tool_id(self) -> str:
    return slugify(self.name)

  @abstractproperty
  def endpoints(self) -> list: pass

  @abstractmethod
  def get_endpoints(self): ...

  def get_endpoints_paths(self) -> list:
    return [
      endpoint.get_path()
      for endpoint in self.endpoints
    ]

  def get_endpoints_docs(self) -> list:
    return [
      endpoint.get_docs()
      for endpoint in self.endpoints
    ]

  def __init__(self):
    self.get_endpoints()

  def store_in_db(self):
    from toolsframe import models

    obj_fields = {
      'name': self.name,
      'description': self.description,
      'app_type': self.access_type,
      'endpoints': self.get_endpoints_docs(),
      'login_required': self.login_required
    }
    tool, created = models.Tool.objects.get_or_create(
      tool_id=self.tool_id, defaults=obj_fields
    )
    if not created:
      for field, value in obj_fields.items():
        setattr(tool, field, value)
      tool.save()

    tool.category.clear()
    for category_name in self.categories:
      category, created = models.Category.objects.get_or_create(name=category_name)
      tool.category.add(category)



class WhatsMyIp(ToolAbstract):
  name = 'what is my ip ?'
  description = "get your current machine ip"
  categories = ['how server sees you', 'network']
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['GET'])
  def get_my_ip(self, request):
    ip = RequestAnalyzerTools.get_ip(request)
    return HttpResponse(ip)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
          "path": "/get-my-ip/",
          "path_name": f"tools:{self.tool_id}",
          "method": "GET",
          "view": self.get_my_ip
      })
    ]


class ProxyAnonymeter(ToolAbstract):
  name = 'proxy anonymeter'
  description = 'tell you how anonymous your proxy is (transparent, anonymous or elite)'
  categories = ["how server see you", "network"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['GET'])
  def get_my_proxy_anonymity(self, request):
    anonymity = RequestAnalyzerTools.get_proxy_anonymity(request)
    return HttpResponse(anonymity)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/get-my-proxy-anonymity/",
        "path_name": f"tools:{self.tool_id}",
        "method": "GET",
        "view": self.get_my_proxy_anonymity
      })
    ]


class RequestHeaders(ToolAbstract):
  name = 'request headers'
  description = 'tell you how the server see your request headers'
  categories = ["how server see you", "network"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  def get_my_request_headers(self, request):
    headers = RequestAnalyzerTools.get_request_headers(request)
    return JsonResponseOverride(headers)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/get-my-request-headers/",
        "path_name": f"tools:{self.tool_id}",
        "method": "ANY",
        "view": self.get_my_request_headers
      })
    ]


class UserAgentAnalyzer(ToolAbstract):
  name = 'User-Agent Analyzer'
  description = 'get all possible data about the machine using its user-agent'
  categories = ["how server see you", "network"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['GET'])
  def analyze_my_machine_user_agent(self, request):
    ua = request.META['HTTP_USER_AGENT']
    ua_details = RequestAnalyzerTools.get_user_agent_details(ua)

    return JsonResponseOverride(ua_details)

  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['user-agent'])
  def analyze_user_agent(self, request):
    post_data = ExtractPostRequestData(request)
    ua = post_data.get('user-agent')

    ua_details = RequestAnalyzerTools.get_user_agent_details(ua)

    return JsonResponseOverride(ua_details)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/analyze-my-machine/",
        "path_name": f"tools:{self.tool_id}-current-machine",
        "method": "GET",
        "view": self.analyze_my_machine_user_agent
      }),

      Endpoint({
        "path": "/analyze-user-agent/",
        "path_name": f"tools:{self.tool_id}-machine",
        "method": "POST",
        "view": self.analyze_user_agent,
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "user-agent",
              "default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
              "required": True,
              "type": "text",
              "description": "The user-agent you want to analyze"
            }
          ]
        }
      })
    ]


class ImagePlaceholder(ToolAbstract):
  name = 'image placeholder'
  description = 'get a placeholder image with your wanted dimensions and color to set it in your page faster'
  categories = ["developer helper", "image", "frontend helper"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['GET'])
  def get_image_placeholder(self, request, width, height=None, color=None):
    color = MyImageHandler.handle_color(color)
    height = height or width

    image = MyImageHandler.generate_placeholder_image(width, height, color)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/get-image-placeholder/<int:width>/",
        "path_name": f"tools:{self.tool_id}-size",
        "view": self.get_image_placeholder,
        "description": "return a square image with a specific size and a random color",
        "method": "GET",
        "params": {
          "URL": [
            {
              "name": "width",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the size of the image's dimensions in px"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/get-image-placeholder/<int:width>/<str:color>/",
        "path_name": f"tools:{self.tool_id}-size-color",
        "view": self.get_image_placeholder,
        "description": "return a square image with a specific width and color",
        "method": "GET",
        "params": {
          "URL": [
            {
              "name": "width",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the size of the image's dimensions in px"
            },
            {
              "name": "color",
              "default": "rgb(34,139,34)",
              "required": True,
              "type": "text",
              "description": "the color of the image -- can be rgb, hex (without hashtag #) or known html colors"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/get-image-placeholder/<int:width>x<int:height>/",
        "path_name": f"tools:{self.tool_id}-w-h",
        "view": self.get_image_placeholder,
        "description": "return an image with specific width and height and random color",
        "method": "GET",
        "params": {
          "URL": [
            {
              "name": "width",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the width of the image in px"
            },
            {
              "name": "height",
              "default": 200,
              "required": True,
              "type": "number",
              "description": "the height of the image in px"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/get-image-placeholder/<int:width>x<int:height>/<str:color>/",
        "path_name": f"tools:{self.tool_id}-w-h-color",
        "view": self.get_image_placeholder,
        "description": "return an image with specific width, height and color",
        "method": "GET",
        "params": {
          "URL": [
            {
              "name": "width",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the width of the image in px"
            },
            {
              "name": "height",
              "default": 200,
              "required": True,
              "type": "number",
              "description": "the height of the image in px"
            },
            {
              "name": "color",
              "default": "rgb(34,139,34)",
              "required": True,
              "type": "text",
              "description": "the color of the image -- can be rgb, hex (without hashtag #) or known html colors"
            }
          ]
        }
      })

    ]


class ImageUserAvatar(ToolAbstract):
  name = 'dynamic user avatar'
  description = 'generate specific profile picture for every user using first letters of its name'
  categories = ["developer helper", "image", "frontend helper"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['GET'])
  def convert_username_to_profile_pic(self, request, size, username, color=None):
    color = MyImageHandler.handle_color(color)
    image = MyImageHandler.generate_avatar_image(size, username, color)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/username-to-profile-pic/<int:size>/<str:username>/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.convert_username_to_profile_pic,
        "method": "GET",
        "description": "generate profile picture with specific size and random color using user's first letters",
        "params": {
          "URL": [
            {
              "name": "size",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the size of the image's dimensions in px"
            },
            {
              "name": "username",
              "default": "John Doe",
              "required": True,
              "type": "text",
              "description": "The name of the user -- just 2 names"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/username-to-profile-pic/<int:size>/<str:username>/<str:color>/",
        "path_name": f"tools:{self.tool_id}-color",
        "view": self.convert_username_to_profile_pic,
        "method": "GET",
        "description": "generate profile picture with specific size and color using user's first letters",
        "params": {
          "URL": [
            {
              "name": "size",
              "default": 300,
              "required": True,
              "type": "number",
              "description": "the size of the image's dimensions in px"
            },
            {
              "name": "username",
              "default": "John Doe",
              "required": True,
              "type": "text",
              "description": "The name of the user -- just 2 names"
            },
            {
              "name": "color",
              "default": "rgb(34,139,34)",
              "required": True,
              "type": "text",
              "description": "the color of the image -- can be rgb, hex (without hashtag #) or known html colors"
            }
          ]
        }
      }),

    ]


class ImageThumbnail(ToolAbstract):
  name = 'thumbnail generator'
  description = 'convert image to thumbnail with custom width'
  categories = ["developer helper", "image", "frontend helper"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['image'])
  def convert_image_to_thumbnail(self, request):
    image_file = request.FILES.get('image')
    new_width = int(request.POST.get('width') or 128)

    image = MyImageHandler.generate_thumbnail(image_file, new_width)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/image-to-thumbnail/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.convert_image_to_thumbnail,
        "method": "POST",
        "dataType": "form",
        "params": {
          "POST": [
            {
              "name": "image",
              "required": True,
              "type": "file",
              "accept": "accept='image/png, image/jpeg'",
              "description": "The image you want to convert to thumbnail"
            },
            {
              "name": "width",
              "default": 128,
              "required": False,
              "type": "number",
              "description": "The width needed for the image -- (height is computed dynamically to maintain the scale)"
            }
          ]
        }
      })
    ]


class ImageMetaData(ToolAbstract):
  name = 'image meta cleaner'
  description = 'clean image from meta data to reduce its size and make it untraceable'
  categories = ["developer helper", "image"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['image'])
  def remove_image_meta_data(self, request):
    image_file = request.FILES.get('image')

    image = MyImageHandler.generate_cleaned_image_form_exif(image_file)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/remove-image-meta-data/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.remove_image_meta_data,
        "method": "POST",
        "dataType": "form",
        "params": {
          "POST": [
            {
              "name": "image",
              "required": True,
              "type": "file",
              "accept": "accept='image/png, image/jpeg'",
              "description": "The image you want to convert to clean from meta data"
            }
          ]
        }
      })
    ]


class ImageBase64(ToolAbstract):
  name = 'image base64'
  description = 'encode image to base64 string or decode'
  categories = ["developer helper", "image", "encode"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['image'])
  def convert_image_to_b64(self, request):
    image_file = request.FILES.get('image')

    b64 = MyImageHandler.generate_b64_from_image(image_file)

    return HttpResponse(b64)

  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['image'])
  def convert_b64_to_image(self, request):
    post_data = ExtractPostRequestData(request)
    image_b64 = post_data.get('image')

    image = MyImageHandler.generate_image_from_b64(image_b64)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/image-to-b64/",
        "path_name": f"tools:img-2-b64",
        "view": self.convert_image_to_b64,
        "method": "POST",
        "description": "Convert any image to base64 encode",
        "dataType": "form",
        "params": {
          "POST": [
            {
              "name": "image",
              "required": True,
              "type": "file",
              "accept": "accept='image/png, image/jpeg'",
              "description": "The image you want to convert to encode to base64"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/b64-to-image/",
        "path_name": f"tools:b64-to-img",
        "view": self.convert_b64_to_image,
        "method": "POST",
        "description": "Decode any base64 image to the jpg version of it",
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "image",
              "default": "",
              "required": True,
              "type": "text",
              "description": "Base64 string you wanna to convert to the jpg image"
            }
          ]
        }
      })
    ]


class ImageQrCode(ToolAbstract):
  name = 'qr-code generator'
  description = 'convert any text into a qrcode'
  categories = ["image", "encode"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['text'])
  def generate_qrcode(self, request):
    post_data = ExtractPostRequestData(request)
    string = post_data.get('text')

    image = MyImageHandler.generate_qr_code(string)

    return ImageResponse(image)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/gen-qrcode/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.generate_qrcode,
        "method": "POST",
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "text",
              "default": "lorem ipsum text example",
              "required": True,
              "type": "text",
              "description": "The text you want to encode into qr-code"
            }
          ]
        }
      }),

    ]


class Facebook(ToolAbstract):
  name = 'facebook user-id'
  description = 'get the id of any facebook user'
  categories = ["developer helper", "social", "scraping"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['url'])
  def get_fb_user_id(self, request):
    post_data = ExtractPostRequestData(request)
    acc_url = post_data.get('url')

    user_id = ScrapingTools.get_fb_user_id(acc_url)  or 'Not Found'

    return HttpResponse(user_id)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/fb-user-id/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.get_fb_user_id,
        "method": "POST",
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "url",
              "default": "https://facebook.com/mohamed17717/",
              "required": True,
              "type": "text",
              "description": "profile url"
            }
          ]
        }
      })
    ]


class CorsProxy(ToolAbstract):
  name = 'cors proxy'
  description = 'simple proxy give your js in the browser the ability to navigate the web, and avoid cors policy <br /><br /> Url Example: <b>/cors-proxy/?url=https://google.com/?q=coffee</b>'
  categories = ["developer helper", "network", "scraping"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  def cors_proxy(self, request):
    cors = ScrapingTools.CorsProxy(request)

    res = cors.simulate_request()
    response = cors.simulate_response(res)

    return response

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/cors-proxy/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.cors_proxy,
        "method": "ANY",
        "description": "like a proxy it will simulate the request you sent (header/body) on the url you set, then simulate the response back to you",
        "stop_http_testing": True,
        "params": {
          "GET": [
            {
              "name": "url",
              "default": "https://google.com",
              "required": True,
              "type": "text",
              "description": "url you wanna navigate"
            }
          ]
        }
      })
    ]


class UrlShortener(ToolAbstract):
  name = 'url shortener'
  description = 'convert shorten url to the original one'
  categories = ["network"]
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['url'])
  def unshorten_url(self, request):
    post_data = ExtractPostRequestData(request)
    shortened_url = post_data.get('url')

    track = ScrapingTools.get_url_redirect_track(shortened_url)

    return HttpResponse(track[-1])

  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['url'])
  def unshorten_url_track(self, request):
    post_data = ExtractPostRequestData(request)
    shortened_url = post_data.get('url')

    track = ScrapingTools.get_url_redirect_track(shortened_url)

    return JsonResponseOverride(track)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/unshorten-url/",
        "path_name": f"tools:{self.tool_id}",
        "view": self.unshorten_url,
        "method": "POST",
        "description": "unpack the url and return the last destination",
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "url",
              "default": "https://bit.ly/3i4L5Uk",
              "required": True,
              "type": "text",
              "description": "shorten url you wanna to unshorten it"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/unshorten-url/full-track/",
        "path_name": f"tools:{self.tool_id}-track",
        "view": self.unshorten_url_track,
        "method": "POST",
        "description": "unpack the url and return the all redirects till the destination",
        "dataType": "json",
        "params": {
          "POST": [
            {
              "name": "url",
              "default": "https://bit.ly/3i4L5Uk",
              "required": True,
              "type": "text",
              "description": "shorten url you wanna to unshorten it"
            }
          ]
        }
      })

    ]


class TextSaver(ToolAbstract):
  name = 'text saver <simple db>'
  description = 'work as a semi db, that save any text you post to the api. you can read it anytime. it can be used as a cdn also. <b>(token is required) to map saved content to your account</b>'
  categories = ["db", "frontend helper", "store"]
  access_type = ToolAccessType.api.value
  login_required = True
  active = True
  endpoints = None

  # views
  @require_http_methods_for_class(['POST'])
  def add(self, request, filename=None):
    # get account
    acc = Account.objects.get_user_acc_from_api_or_web(request, required=True)

    text = request.data
    if request.POST:
      # it a form
      text = '&'.join(['='.join(map(str, item)) for item in request.POST.dict().items()])

    file_path = TextSaverModel.add(acc, text, filename)
    file_full_url = request.build_absolute_uri(file_path)

    return HttpResponse(file_full_url)

  @require_http_methods_for_class(['GET'])
  def read(self, request, filename):
    acc = Account.objects.get_user_acc_from_api_or_web(request, required=True)

    location = TextSaverModel.read(acc, filename)

    response = HttpResponse(open(location), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

  @require_http_methods_for_class(['GET'])
  def read_text(self, request, filename):
    acc = Account.objects.get_user_acc_from_api_or_web(request, required=True)
    location = TextSaverModel.read(acc, filename)

    data = FileManager.read(location)

    return HttpResponse(data)

  @require_http_methods_for_class(['GET', 'DELETE'])
  def delete(self, request, filename):
    acc = Account.objects.get_user_acc_from_api_or_web(request, required=True)

    delete_status = TextSaverModel.delete(acc, filename)

    response = HttpResponse() if delete_status else HttpResponseBadRequest('file is not exist') 
    if request.user.is_authenticated and request.method == 'GET':
      response = Redirector.go_previous_page(request)
    return response

  @require_http_methods_for_class(['POST'])
  @required_post_fields_for_class(['line'])
  def check_line_exist(self, request, filename):
    acc = Account.objects.get_user_acc_from_api_or_web(request, required=True)

    try:
      location = TextSaverModel.read(acc, filename)
    except:
      return HttpResponse('Please make sure file name is exist.', status=400)

    lines = FileManager.read(location).split('\n')

    post_data = ExtractPostRequestData(request)
    line = post_data.get('line')

    for file_line in lines:
      if line and file_line.startswith(line):
        return HttpResponse('Found', status=200)

    return HttpResponse(f'Not Found', status=404)

  def as_view(self, request, filename):
    views = {
      'POST': self.add,
      'GET': self.read,
      'DELETE': self.delete,
    }
    method = views.get(request.method)
    return method(request, filename)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
        "path": "/save-text/",
        "path_name": f"tools:{self.tool_id}-create",
        "view": self.add,
        "method": "POST",
        "description": "save any text post to this endpoint in your request body.<br>it creates file with random name, and return the full path to that file",
        "dataType": "text",
        "defaultText": "Try to post that example text."
      }),

      Endpoint({
        "path": "/save-text/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-cu",
        "view": self.as_view,
        "method": "POST",
        "description": "save any text post to this endpoint in your request body.<br>it creates/update the file with this name",
        "dataType": "text",
        "defaultText": "Try to post that example text.",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to create|update"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/delete/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-del",
        "view": self.delete,
        "method": "GET",
        "description": "delete the unwanted file, using ite name",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to delete"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/delete/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-delete",
        "view": self.delete,
        "method": "DELETE",
        "description": "delete the unwanted file, using ite name",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to delete"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-d",
        "view": self.as_view,
        "method": "DELETE",
        "description": "delete the unwanted file, using ite name",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to delete"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/read/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-read",
        "view": self.read,
        "method": "GET",
        "description": "read your file saved content",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to read"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/read-text/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-read-text",
        "view": self.read_text,
        "method": "GET",
        "description": "read file and return its content as a text",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to read"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-r",
        "view": self.as_view,
        "method": "GET",
        "description": "read your file saved content",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to read"
            }
          ]
        }
      }),

      Endpoint({
        "path": "/save-text/check-line-exist/<str:filename>/",
        "path_name": f"tools:{self.tool_id}-check-line",
        "view": self.check_line_exist,
        "method": "POST",
        "description": "Check if there is a line in file <b>starts with</b> your text <br> it may used to check a record set from your form, etc...",
        "dataType": "json",
        "params": {
          "URL": [
            {
              "name": "filename",
              "default": "default_file.txt",
              "required": True,
              "type": "text",
              "description": "the name of a file you want to create|update"
            }
          ],
          "POST": [
            {
              "name": "line",
              "default": "check this line",
              "required": True,
              "type": "text",
              "description": "line you want to check inside the file, if any line start with it"
            }
          ]
        }
      }),


    ]



# class NAME(ToolAbstract):
#   name = ''
#   description = ''
#   categories = ['']
#   access_type = ToolAccessType.api.value
#   login_required = False
#   active = True
#   endpoints = None

#   # views
#   @require_http_methods_for_class(['GET'])

#   def get_endpoints(self):
#     self.endpoints = [
#       Endpoint({
#         # "path": ,
#         # "path_name": f"tools:{self.tool_id}",
#         # "method": "ANY",
#         # "view": self.get_my_request_headers,
#       })
#     ]


def load_tool_classes():
  return ToolAbstract.__subclasses__()

