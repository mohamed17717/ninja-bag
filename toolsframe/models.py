from django.db import models
from jsonfield import JSONField


class Category(models.Model):
  name = models.CharField(max_length=128)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return ('')



class Tool(models.Model):
  # TODO: Define fields here

  name = models.CharField(max_length=128)
  genre = models.CharField(max_length=8) # api || web based
  tool_id = models.CharField(max_length=128, unique=True, editable=False, blank=True) # generated 32 char
  
  logo = models.ImageField(upload_to='tool_logo', blank=True, null=True)
  description = models.TextField(blank=True, null=True) # SEO && after title
  notes = models.TextField(blank=True, null=True) # its limited or totally free

  app_name = models.CharField(max_length=128, blank=True, null=True)
  url_reverser = models.CharField(max_length=64) # 'app_name:home'

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

  def save(self):
    pass

  def get_absolute_url(self):
    return ('')

  # TODO: Define custom methods here
