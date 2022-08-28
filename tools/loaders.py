from django.utils.text import slugify
from django.http import HttpResponse
from django.urls import path
from django.shortcuts import resolve_url

from abc import ABC, abstractmethod, abstractproperty
from enum import Enum

from utils.decorators import require_http_methods_for_class, required_post_fields_for_class
from utils.views_mixins import JsonResponseOverride, ImageResponse
from utils.mixins import ExtractPostRequestData

from .controller import RequestAnalyzerTools
from .controller.ImageTools import MyImageHandler


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
#         # "view": self.get_my_request_headers
#       })
#     ]


def load_tool_classes():
  return ToolAbstract.__subclasses__()

