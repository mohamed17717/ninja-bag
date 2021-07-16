from django.http import HttpResponseBadRequest
import os

class Limit:
  def __init__(self, acc):
    self.acc = acc

  def before(self, request):
    return True

  def after(self, request, response):
    return True

class StorageLimit(Limit):
  def __init__(self, acc):
    super().__init__(acc)
    self.before = self.acc.check_storage_limit_hookbefore

class BandwidthLimit(Limit):
  def __init__(self, acc):
    super().__init__(acc)
    self.before = self.acc.check_bandwidth_limit_hookbefore
    self.after = self.acc.check_bandwidth_limit_hookafter

class RequestsLimit(Limit):
  def __init__(self, acc):
    super().__init__(acc)
    self.before = self.acc.check_requests_limit_hookbefore
    self.after = self.acc.check_requests_limit_hookafter

class LimitsHandler:
  def __init__(self, acc):
    if not acc: return

    self.storage = StorageLimit(acc)
    self.bandwidth = BandwidthLimit(acc)
    self.requests = RequestsLimit(acc)


class ToolHandler:
  tools_map = {
    'whats my ip': ['get_my_ip'],
    'proxy meter': ['get_my_proxy_anonimity'],
    #
    #
  }

  def run_limits_before(self, limits_handler, limits, args):
    access_states = []
    for limit_name in limits:
      limit_handler = getattr(limits_handler, limit_name)
      state = limit_handler.before(*args)
      access_states.append(state)

    return access_states

  def run_limits_after(self, limits_handler, limits, args):
    for limit_name in limits:
      limit_handler = getattr(limits_handler, limit_name)
      limit_handler.after(*args)

  def run_func(self, func, request, *args, **kwargs):
    try:
      response = func(request, *args, **kwargs)
    except Exception as e:
      responce = HttpResponseBadRequest(e)
    
    return responce

  def reverse_view_func_to_tool_id(self, func):
    # tools_map_reversed = {}
    # for tool_name, tool_endpoints in ToolHandler.tools_map.items():
    #   func_names = map(lambda f: f.__qualname__, tool_endpoints)
    #   tools_map_reversed[tool_name] = tuple(func_names)

    func_name = func.__qualname__
    for tool_name, tool_endpoints in ToolHandler.tools_map.items():
      if func_name in tool_endpoints:
        return tool_name

    # raise Exception('function is not exist is not exist')


class SizeHandler:
  def convert_size(self, size, unit):
    """ Take size in bits convert it in whatever unit """
    units = {
      'B' : lambda size: size / 1024**0,
      'KB': lambda size: size / 1024**1,
      'MB': lambda size: size / 1024**2,
      'GB': lambda size: size / 1024**3,
      'TB': lambda size: size / 1024**4,
    }

    unit_size = units[unit](size)
    return unit_size

  def get_folder_size(self, location, unit='MB'):
    size = 0
    for path, dirs, files in os.walk(location):
      for f in files:
        fp = os.path.join(path, f)
        size += os.path.getsize(fp)

    return self.convert_size(size, unit)

  def get_request_size(self, request, unit):
    size = len(request.body)
    return self.convert_size(size, unit)

  def get_response_size(self, response, unit):
    if response.status_code > 250:
      return 0

    size = len(response.content)
    return self.convert_size(size, unit)

