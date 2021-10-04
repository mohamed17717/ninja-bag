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


  def get_user_folder_location(self):
    return f'./users_storage/{self.token[:16]}/'

  def get_user_folder_size(self, unit='MB'):
    location = self.get_user_folder_location()

    try: size = size_handler.get_folder_size(location, unit)
    except: size = 0

    return size

