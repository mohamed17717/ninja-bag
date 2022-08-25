from django.utils.text import slugify
from django.http import HttpResponse
from django.urls import path

from abc import ABC, abstractmethod, abstractproperty
from enum import Enum

from .controller import RequestAnalyzerTools


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
    url = self.data['url'].strip('/') + '/'
    return path(url, self.data['view'])

  def get_docs(self):
    docs_dict = { **self.data } 
    docs_dict.pop('view')
    return docs_dict

class Tool(ABC):
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
    ...

class WhatsMyIp(Tool):
  name = 'what is my ip ?'
  description = "get your current machine ip"
  categories = ['how server sees you', 'network']
  access_type = ToolAccessType.api.value
  login_required = False
  active = True
  endpoints = None

  # views
  def get_my_ip(self, request):
    ip = RequestAnalyzerTools.get_ip(request)
    return HttpResponse(ip)

  def get_endpoints(self):
    self.endpoints = [
      Endpoint({
          "url": "/get-my-ip/",
          "method": "GET",
          "view": self.get_my_ip
      })
    ]
