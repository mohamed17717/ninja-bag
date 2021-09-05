from django.db import models
from django.contrib.auth import get_user_model

import secrets 
from datetime import datetime

from .managers import AccountManager
from utils.helpers import SizeCalculator


User = get_user_model()
size_handler = SizeCalculator()


class Account(models.Model):
  DEFAULT_USER_PICTURE = 'https://cdn2.iconfinder.com/data/icons/people-occupation-job/64/Ninja-Warrior-Assassin-Japan-Fighter-Avatar-Martial_arts-512.png'

  user = models.OneToOneField(User, related_name='user_account', on_delete=models.CASCADE)
  token = models.CharField(max_length=128, unique=True, editable=False, blank=True)

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

  objects = AccountManager()

  class Meta:
    verbose_name = 'Account'
    verbose_name_plural = 'Accounts'

  def __str__(self):
    return self.user.username+f'({self.token})'

  def save(self, *args, **kwargs):
    if not self.pk:
      self.token = secrets.token_hex(nbytes=16)
    
    return super(Account, self).save(*args, **kwargs)


  # computed fields
  @property
  def get_user_name(self):
    name = f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.username
    return name

  @property
  def get_user_picture(self):
    if self.picture:
      picture = self.picture.url
    else:
      picture = self.DEFAULT_USER_PICTURE

    return picture


  # ----------------- limitation plan --------------- #
  def get_user_folder_location(self):
    return f'./users_storage/{self.token[:16]}/'


  def get_user_folder_size(self, unit='MB'):
    location = self.get_user_folder_location()

    try: size = size_handler.get_folder_size(location, unit)
    except: size = 0

    return size

  def check_storage_limit_hookbefore(self, request):
    unit = 'MB'
    used_storage = self.get_user_folder_size(unit)
    request_size = size_handler.get_request_size(request, unit)

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
    request_size = size_handler.get_request_size(request, unit)

    return self.bandwidth_allowed >= (used_bandwidth + request_size)
  def check_bandwidth_limit_hookafter(self, request, response):
    unit = 'MB'
    request_size = size_handler.get_request_size(request, unit)
    response_size = size_handler.get_response_size(response, unit)

    self.bandwidth_used += (request_size + response_size)
    self.save()


  # -------------- subscription plan ---------------- #
  def get_days_since_created(self):
    now = datetime.now()
    return (now - self.created).days

  def reset_user_cycle(self):
    self.requests_used = 0
    self.bandwidth_used = 0

    return self.save()

  @classmethod
  def get_users_whom_cycle_ended(cls):
    cycle_long = 30
    users = cls.objects.all()
    cycle_end_checker = lambda u: u.get_days_since_created() % cycle_long == 0
    users_ended = filter(cycle_end_checker, users)
    return users_ended

  @classmethod
  def reset_users_cycle(cls):
    users = cls.get_users_whom_cycle_ended()
    for user in users:
      user.reset_user_cycle()


