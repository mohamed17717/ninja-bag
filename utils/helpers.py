from django.shortcuts import redirect
import json, os, hashlib
import unicodedata


class Redirector:
  HOMEPAGE_URL_REVERSER = 'toolsframe:homepage'
  LOGIN_URL_REVERSER = 'accounts:login-page'

  @classmethod
  def go_home(cls):
    return redirect(cls.HOMEPAGE_URL_REVERSER)

  @classmethod
  def go_login(cls):
    return redirect(cls.LOGIN_URL_REVERSER)

  @classmethod
  def go_previous_page(cls, request):
    return redirect(request.META.get('HTTP_REFERER', '/'))

class FileManager:
  @staticmethod
  def create_location(location):
    status = False
    try:
      os.makedirs(location)
      status = True
    except FileExistsError:
      status = True

    return status

  @staticmethod
  def read(location, mode='r', to_json=None, lines=None):
    mode = mode if mode in ['r', 'rb'] else 'r'

    with open(location, mode, encoding='utf8') as f:
      data = f.read()

    if to_json == None and location.endswith('.json'):
      to_json = True

    data = unicodedata.normalize("NFKD", data)
    if to_json:
      data = json.loads(data)
    elif lines:
      data = data.split('\n')

    return  data

  @classmethod
  def write(cls, location, data, mode='w', set_hash_name=False,force_location=False):
    mode = mode if mode in ['w', 'a', 'wb', 'ab'] else 'w'
    is_binary = mode.endswith('b')

    if force_location:
      file_location = os.path.dirname(location)
      if file_location:
        cls.create_location(file_location)

    if type(data) != str and not is_binary:
      data = json.dumps(data, ensure_ascii=False, indent=2)

    if set_hash_name:
      *_dir, _file = location.split('/')

      content = data if is_binary else data.encode('utf8')
      hash_content = hashlib.sha1(content).hexdigest()[:8]

      _file = _file.split('.')
      _file.insert(-1, hash_content)
      _file = '.'.join(_file)

      _dir.append(_file)
      location = '/'.join(_dir)

    encoding = None if is_binary else 'utf8'
    data = unicodedata.normalize("NFKD", data)
    with open(location, mode, encoding=encoding) as f:
      f.write(data)

  @staticmethod
  def is_file_exist(location):
    return os.path.isfile(location) and os.access(location, os.R_OK)

  @classmethod
  def delete(cls, location):
    if cls.is_file_exist(location):
      os.remove(location)
      return True
    return False

  @staticmethod
  def listdir(location):
    try: dirs = os.listdir(location)
    except: dirs = []

    return dirs


class SizeCalculator:
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

  def get_file_size(self, file_path):
    return os.path.getsize(file_path)

  def get_folder_size(self, location, unit='MB'):
    size = self.get_folder_size_raw(location)
    return self.convert_size(size, unit)

  def get_folder_size_raw(self, location):
    size = 0
    for path, dirs, files in os.walk(location):
      for f in files:
        file_path = os.path.join(path, f)
        size += self.get_file_size(file_path)
    return size

  def get_request_size(self, request, unit):
    size = len(request.data)
    return self.convert_size(size, unit)

  def get_response_size(self, response, unit):
    if response.status_code > 250:
      return 0

    size = len(response.content)
    return self.convert_size(size, unit)


