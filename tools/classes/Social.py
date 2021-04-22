import re, requests


class Facebook:
  def __init__(self, url):
    self.url = url

  def get_fb_user_id(self):
    res = requests.get(self.url)
    src = res.text
    match = re.findall(r'userID":"(.+?)"', src)
    return match[0] if match else None

