from django.db import models
from django.contrib.auth import get_user_model

from jsonfield import JSONField


User = get_user_model()


def get_client_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip

class Profile(models.Model):
  user = models.ForeignKey(User, related_name='user_profile', on_delete=models.CASCADE)
  name = models.CharField(max_length=50, blank=True, null=True)
  age = models.IntegerField(blank=True, null=True)

  picture = models.ImageField(upload_to='thumbnails', default='thumbnails/default.jpg')
  shitty_data = JSONField()

  def serialize(self):
    return {
      'user': self.user.__dict__, # user.serialize(),
      'name': self.name,
      'age': self.age
    }

class WebRequest(models.Model):
  time = models.DateTimeField(auto_now_add=True)
  host = models.CharField(max_length=1000)
  path = models.CharField(max_length=1000)
  method = models.CharField(max_length=50)
  uri = models.CharField(max_length=2000)
  status_code = models.IntegerField()
  user_agent = models.CharField(max_length=1000,blank=True,null=True)
  remote_addr = models.GenericIPAddressField(protocol='both', unpack_ipv4=False)
  remote_addr_fwd = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, blank=True, null=True)
  meta = models.TextField()
  cookies = models.TextField(blank=True,null=True)
  get = models.TextField(blank=True,null=True)
  post = models.TextField(blank=True,null=True)
  raw_post = models.TextField(blank=True,null=True)
  is_secure = models.BooleanField()
  is_ajax = models.BooleanField()
  user = models.ForeignKey(User,blank=True,null=True, on_delete=models.DO_NOTHING)
