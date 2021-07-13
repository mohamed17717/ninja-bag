import re, requests, json
from django.http import HttpResponse

def get_url_redirect_track(url):
  res = requests.head(url, allow_redirects=True)
  track = [r.url for r in res.history] + [res.url]

  return track


def get_fb_user_id(url):
  res = requests.get(url)
  src = res.text

  match = re.findall(r'userID":"(.+?)"', src)
  user_id = match[0] if match else None

  return user_id


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
