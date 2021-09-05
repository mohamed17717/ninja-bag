import user_agents


def get_ip(request) -> str:
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip

def get_proxy_anonymity(request) -> str:
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

  anonymity = 'anonymous'
  if len(found_headers) == 0:
    anonymity = 'elite'
  elif rename_header('X-Forwarded-For') in found_headers:
    anonymity = 'transparent'

  return anonymity

def get_request_headers(request) -> dict:
  headers = {}

  for key, value in request.META.items():
    if key.startswith('HTTP_'):
      key = key.replace('HTTP_', '')
      headers[key] = value

  return headers

def get_user_agent_details(ua) -> dict:
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

