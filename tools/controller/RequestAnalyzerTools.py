import user_agents
from django.http import HttpRequest

def get_ip(request:HttpRequest) -> str:
  key_names = [
    ('HTTP_X_FORWARDED_FOR', lambda ip: ip.split(',')[0]), 
    ('REMOTE_ADDR', lambda ip: ip), 
    ('HTTP_X_REAL_IP', lambda ip: ip)
  ]

  ip = None
  for key, cleaner in key_names:
    ip = cleaner(request.META.get(key, ''))
    if ip: break

  return ip

def get_proxy_anonymity(request:HttpRequest) -> str:
  ELITE, ANONYMOUS, TRANSPARENT, NO_PROXY = 'elite', 'anonymous', 'transparent', 'none'

  proxy_msgs = {
    ELITE: 'Its {proxy_type} proxy (our server doesn\'t see any proxy, only see this ip -> {ip})',
    ANONYMOUS: 'Its {proxy_type} proxy (telling its a proxy but not telling about your real ip -> {ip})',
    TRANSPARENT: 'Its {proxy_type} proxy (telling its a proxy at -> {proxy_ip} , and telling about your real ip -> {ip})',
    NO_PROXY: 'Didn\'t identify any proxy'
  }
  get_proxy_msg = lambda proxy_type, ip, proxy_ip: proxy_msgs[proxy_type].format(proxy_type=proxy_type, ip=ip, proxy_ip=proxy_ip)

  proxy_headers = [
    # elite
    # Anonymous
    'HTTP_AUTHORIZATION', 'HTTP_FROM', 'HTTP_PROXY_AUTHORIZATION', 'HTTP_PROXY_CONNECTION', 'HTTP_VIA',
    # transparent
    # 'HTTP_X_FORWARDED_FOR'
  ]

  proxy_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
  real_ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_REAL_IP')

  proxy_type = ELITE
  if proxy_ip:
    """ Then its Transparent or Anonymous or None """
    if proxy_ip != real_ip and real_ip: 
      proxy_type = TRANSPARENT
    elif len([h for h in proxy_headers if request.META.get(h)]):
      proxy_type = ANONYMOUS
    elif proxy_ip == real_ip:
      proxy_type = NO_PROXY
    else:
      proxy_type = NO_PROXY

  return get_proxy_msg(proxy_type, real_ip, proxy_ip)

def get_request_headers(request:HttpRequest) -> dict:
  headers = {}

  for key, value in request.META.items():
    if key.startswith('HTTP_'):
      key = key.replace('HTTP_', '')
      headers[key] = value

  return headers

def get_user_agent_details(ua:str) -> dict:
  user_agent = user_agents.parse(ua)
  return {
    'ua': str(user_agent),

    'browser': {
      'family': user_agent.browser.family,
      'version': user_agent.browser.version,
      'version_string': user_agent.browser.version_string,
    },

    'os': {
      'family': user_agent.os.family,
      'version': user_agent.os.version,
      'version_string': user_agent.os.version_string,
    },

    'device': {
      'family': user_agent.device.family,
      'brand': user_agent.device.brand,
      'model': user_agent.device.model,
    },

    'flags': {
      'is_mobile': user_agent.is_mobile,
      'is_tablet': user_agent.is_tablet,
      'is_touch_capable': user_agent.is_touch_capable,
      'is_pc': user_agent.is_pc,
      'is_bot': user_agent.is_bot,
    }
  }

