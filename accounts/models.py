from django.db import models
from django.contrib.auth import get_user_model

from jsonfield import JSONField

from toolsframe.models import Tool

User = get_user_model()


class Account(models.Model):
  # TODO: Define fields here
  user = models.ForeignKey(User, related_name='user_profile', on_delete=models.CASCADE)
  user_api_key = models.CharField(max_length=128, unique=True, editable=False, blank=True)

  picture = models.ImageField(upload_to='profile_pic', blank=True, null=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  # limitation
  total_size_allowed = models.IntegerField(default=100) # MB
  total_requests_allowed = models.IntegerField(default=1000) # request/month

  requests_count = models.IntegerField(default=0)

  class Meta:
    verbose_name = 'Account'
    verbose_name_plural = 'Accounts'

  def __str__(self):
    pass

  def save(self):
    pass

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here


class PremiumToolOwnership(models.Model):
  # TODO: Define fields here
  user = models.ForeignKey(User, related_name='user_tool_ownerships', on_delete=models.SET_NULL, blank=True, null=True)
  tool = models.ForeignKey(Tool, related_name='tool_owners', on_delete=models.PROTECT)

  expiration_period = models.IntegerField(default=30)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)


  class Meta:
    verbose_name = 'PremiumToolOwnership'
    verbose_name_plural = 'PremiumToolOwnerships'

  def __str__(self):
    pass

  def save(self):
    pass

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here
  def is_expired(self):
    pass

  def get_period_to_expire(self):
    pass
