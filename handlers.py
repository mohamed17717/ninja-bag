from accounts.models import Account
from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied


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

  def get_acc(self, api_key, limits):
    acc = api_key and Account.get_user_by_api_key(api_key)

    if len(limits) and not acc:
      raise PermissionDenied('Invalid token !!')

    return acc

  def run_func(self, func, request, *args, **kwargs):
    try:
      response = func(request, *args, **kwargs)
    except Exception as e:
      responce = HttpResponseBadRequest(e)
    
    return responce

