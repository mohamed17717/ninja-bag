from django.db import models
from django.contrib.auth import get_user_model

from jsonfield import JSONField

from toolsframe.models import Tool

import secrets 
from datetime import datetime

User = get_user_model()


class Account(models.Model):
  # TODO: Define fields here
  user = models.ForeignKey(User, related_name='user_account', on_delete=models.CASCADE)
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
    return self.user.username

  def save(self, *args, **kwargs):
    if not self.pk:
      self.user_api_key = secrets.token_hex(nbytes=16)
    
    return super(Account, self).save(*args, **kwargs)

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here
  def get_total_size_used(self):
    ...

  def get_free_size(self):
    return self.total_size_allowed - self.get_total_size_used()

  def is_new_size_available(self, new_size):
    return new_size <= self.get_free_size()

  def increase_request(self):
    self.requests_count += 1
    return self.save()

  def get_requests_available(self):
    return self.total_requests_allowed - self.requests_count

  def is_new_request_available(self):
    return self.get_requests_available() > 0

  def reset_requests_month(self):
    self.requests_count = 0
    return self.save()

  @staticmethod
  def get_user_by_api_key(api_key):
    ...

  @staticmethod
  def get_users_to_reset_requests():
    # get using created
    ...

  @staticmethod
  def reset_requests_month():
    users = Account.get_users_to_reset_requests()
    for user in users:
      user.reset_requests_month()

  



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
