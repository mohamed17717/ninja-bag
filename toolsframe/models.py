from django.db import models
from jsonfield import JSONField
from django.shortcuts import resolve_url
from django.urls import reverse

import secrets

class Category(models.Model):
  name = models.CharField(max_length=128)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  class Meta:
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here
  def get_tools(self):
    return self.category_tools.all()



class Tool(models.Model):
  # TODO: Define fields here

  name = models.CharField(max_length=128)
  genre = models.CharField(max_length=32) # api || web based
  tool_id = models.CharField(max_length=128, unique=True, editable=False, blank=True) # generated 32 char
  
  logo = models.ImageField(upload_to='tool_logo', blank=True, null=True)
  description = models.TextField(blank=True, null=True) # SEO && after title
  notes = models.TextField(blank=True, null=True) # its limited or totally free

  app_name = models.CharField(max_length=128, blank=True, null=True)
  url_reverser = models.CharField(max_length=64, default='toolsframe:tool') # 'app_name:home'

  api_endpoints = JSONField(blank=True, null=True)

  category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category_tools', blank=True, null=True)

  access_lvl = models.IntegerField(default=0) # 0 not-require auth | 1 require auth | 2 premium | 3 partial premium
  # limitation is upon the user account

  # counters
  uses_count = models.IntegerField(default=0)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  class Meta:
    verbose_name = 'Tool'
    verbose_name_plural = 'Tools'

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.pk:
      self.tool_id = secrets.token_hex(nbytes=16)
    return super(Tool, self).save(*args, **kwargs)

  def get_absolute_url(self):
    # return resolve_url(self.url_reverser, tool_id=self.tool_id)
    try:
      url = reverse(self.url_reverser)
    except:
      url = reverse(self.url_reverser, kwargs={'tool_id':self.tool_id})

    return url

  # TODO: Define custom methods here
  def increase_uses_count(self):
    self.uses_count += 1
    return self.save()
