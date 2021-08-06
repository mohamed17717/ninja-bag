import json, os
import hashlib

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

