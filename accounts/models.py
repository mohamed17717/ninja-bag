from django.db import models
from django.contrib.auth import get_user_model

from jsonfield import JSONField

from toolsframe.models import Tool

import secrets 
from datetime import datetime

User = get_user_model()

import os
def convert_size(size, unit):
  units = {
    'B' : lambda size: size / 1024**0,
    'KB': lambda size: size / 1024**1,
    'MB': lambda size: size / 1024**2,
    'GB': lambda size: size / 1024**3,
    'TB': lambda size: size / 1024**4,
  }

  unit_size = units[unit](size)
  return unit_size

def get_folder_size(location, unit='MB'):
  size = 0
  for path, dirs, files in os.walk(location):
    for f in files:
      fp = os.path.join(path, f)
      size += os.path.getsize(fp)

  return convert_size(size, unit)

def get_request_size(request, unit):
  size = len(request.body)
  return convert_size(size, unit)

def get_response_size(response, unit):
  if response.status_code > 250:
    return 0

  size = len(response.content)
  return convert_size(size, unit)


class Account(models.Model):
  DEFAULT_USER_PICTURE = 'https://variety.com/wp-content/uploads/2015/07/naruto_movie-lionsgate.jpg?w=681&h=383&crop=1'


  user = models.ForeignKey(User, related_name='user_account', on_delete=models.CASCADE)
  user_api_key = models.CharField(max_length=128, unique=True, editable=False, blank=True)

  picture = models.ImageField(upload_to='profile_pic', blank=True, null=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  # limitation
  storage_allowed = models.IntegerField(default=10) # MB
  bandwidth_allowed = models.IntegerField(default=100) # MB
  requests_allowed = models.IntegerField(default=1000) # request/month

  # storage_used = models.IntegerField(default=0) # MB
  bandwidth_used = models.FloatField(default=0) # MB
  requests_used = models.IntegerField(default=0) # request/month

  class Meta:
    verbose_name = 'Account'
    verbose_name_plural = 'Accounts'

  def __str__(self):
    return self.user.username+f'({self.user_api_key})'

  def save(self, *args, **kwargs):
    if not self.pk:
      self.user_api_key = secrets.token_hex(nbytes=16)
    
    return super(Account, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return ('')


  def check_storage_limit_hookbefore(self, request):
    unit = 'MB'
    used_storage = self.get_user_folder_size(unit)
    request_size = get_request_size(request, unit)

    return self.storage_allowed >= (used_storage + request_size)


  def check_requests_limit_hookbefore(self, request):
    requests_available = self.requests_allowed - self.requests_used
    return requests_available > 0
  def check_requests_limit_hookafter(self, request, response):
    self.requests_used += 1
    self.save()


  def check_bandwidth_limit_hookbefore(self, request):
    unit = 'MB'
    used_bandwidth = self.bandwidth_used
    request_size = get_request_size(request, unit)

    return self.bandwidth_allowed >= (used_bandwidth + request_size)
  def check_bandwidth_limit_hookafter(self, request, response):
    unit = 'MB'
    request_size = get_request_size(request, unit)
    response_size = get_response_size(response, unit)

    self.bandwidth_used += (request_size + response_size)
    self.save()



  def reset_user_cycle(self):
    self.requests_used = 0
    self.bandwidth_used = 0

    return self.save()

  def get_user_folder_location(self):
    return f'./users_storage/{self.user_api_key[:16]}/'

  def get_user_folder_size(self, unit='MB'):
    location = self.get_user_folder_location()

    try: size = get_folder_size(location, unit)
    except: size = 0

    return size

  def get_days_since_created(self):
    now = datetime.now()
    return (now - self.created).days


  def get_user_name(self):
    name = f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.username
    return name

  def get_user_picture(self):
    if self.picture:
      picture = self.picture.url
    else:
      picture = self.DEFAULT_USER_PICTURE

    return picture

  @staticmethod
  def get_user_by_api_key(api_key):
    acc = Account.objects.filter(user_api_key=api_key).first()
    return acc

  @staticmethod
  def get_users_whom_cycle_ended():
    cycle_long = 30
    users = Account.objects.all()
    cycle_end_checker = lambda u: u.get_days_since_created() % cycle_long == 0
    users_ended = filter(cycle_end_checker, users)
    return users_ended

  @staticmethod
  def reset_users_cycle():
    users = Account.get_users_whom_cycle_ended()
    for user in users:
      user.reset_user_cycle()



class PremiumToolOwnership(models.Model):
  period_long = 30
  # TODO: Define fields here
  user = models.ForeignKey(User, related_name='user_tool_ownerships', on_delete=models.SET_NULL, blank=True, null=True)
  tool = models.ForeignKey(Tool, related_name='tool_owners', on_delete=models.PROTECT)

  is_forever = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)
  last_pay = models.DateField(blank=True)

  class Meta:
    verbose_name = 'PremiumToolOwnership'
    verbose_name_plural = 'PremiumToolOwnerships'

  def __str__(self):
    pass

  def save(self, *args, **kwargs):
    if not self.pk:
      self.last_pay = datetime.now()

    return super(PremiumToolOwnership, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here
  def is_expired(self):
    return self.is_forever or self.get_period_to_expire() > 0

  def get_period_to_expire(self):
    period = datetime.now() - self.created
    period_long = self.period_long
    return period_long - (period % period_long)

  def pay(self):
    self.last_pay = datetime.now()

  @staticmethod
  def get_ownerships_expire_soon(days_to_expiration=5):
    period_before = PremiumToolOwnership.period_long - days_to_expiration
    period_before_date = datetime.datetime.now() - datetime.timedelta(days=period_before)

    # filter on people who pay 25 days ago or more
    ownerships = PremiumToolOwnership.objects.filter(
      last_pay__lte=period_before_date, is_forever=False)

    return ownerships

  @staticmethod
  def check_user_access_to_tool(user, tool):
    obj = PremiumToolOwnership.objects.filter(user=user, tool=tool).first()
    is_exist = bool(obj)
    result = is_exist and obj.is_expired()
    return result
