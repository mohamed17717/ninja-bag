from django.db import models
from jsonfield import JSONField
from django.shortcuts import resolve_url, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from utils.helpers import dynamic_import
import secrets

from .managers import  (
  UpcomingToolManager,
  ToolViewsFunctionsManager,
  ToolManager
)

User = get_user_model()

class Category(models.Model):
  name = models.CharField(max_length=128)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  class Meta:
    verbose_name = 'Category'
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name

  @property
  def tools(self):
    return self.category_tools.all()


class Tool(models.Model):
  # required
  name = models.CharField(max_length=128)
  app_type = models.CharField(max_length=32) # api || web based
  tool_id = models.CharField(max_length=128, unique=True, editable=False, blank=True) # generated 32 char
  logo = models.ImageField(upload_to='tool_logo', blank=True, null=True)
  description = models.TextField(blank=True, null=True) # SEO && after title
  url_reverser = models.CharField(max_length=64, default='toolsframe:tool') # 'app_name:home'

  endpoints = JSONField(blank=True, null=True)
  category = models.ManyToManyField(Category, related_name='category_tools')

  active = models.BooleanField(default=True)
  status = models.CharField(max_length=32, blank=True, null=True) # alpha || beta
  # counters
  uses_count = models.IntegerField(default=0)
  views_count = models.IntegerField(default=0)
  # dates
  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = ToolManager()

  class Meta:
    verbose_name = 'Tool'
    verbose_name_plural = 'Tools'

  def __str__(self):
    return f'{self.pk}- {self.tool_id}'

  def save(self, *args, **kwargs):
    if not self.pk:
      self.tool_id = slugify(self.name + ' ' + secrets.token_hex(nbytes=4))
    return super(Tool, self).save(*args, **kwargs)

  def get_absolute_url(self):
    try:
      url = reverse(self.url_reverser)
    except:
      url = reverse(self.url_reverser, kwargs={'tool_id':self.tool_id})

    return url

  def increase_uses_count(self):
    self.uses_count += 1
    return self.save()

  def increase_views_count(self):
    self.views_count += 1
    return self.save()

  @property
  def db_class(self):
    db_obj = getattr(self, 'tool_db', None)
    db_name = db_obj and db_obj.name

    db_class = None
    if db_name:
      db_class = dynamic_import(f'tools.models.{db_name}')

    return db_class

  def get_db_records(self, user):
    db = self.db_class
    return db and db.list_all(user) or []


class UpcomingTool(models.Model):
  name = models.CharField(max_length=128)
  description = models.TextField()

  upvote = models.IntegerField(blank=True, null=True, default=0)
  downvote = models.IntegerField(blank=True, null=True, default=0)

  active = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = UpcomingToolManager()

  def __str__(self):
    return self.name


class SuggestedTool(models.Model):
  user = models.ForeignKey(User, related_name='user_suggested_tools', on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField()

  seen = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    user_info = f'{self.pk} - {self.user.username}'
    description = self.description[:30]
    status = "👀" if self.seen else "🔒"

    return f'{user_info} ({description}) {status}'


class ToolIssueReport(models.Model):
  tool =  models.ForeignKey(Tool, related_name='tool_issue_reports', on_delete=models.CASCADE)
  user = models.ForeignKey(User, related_name='user_issue_reports', on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField()

  seen = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    user_info = f'{self.pk} - {self.user.username}'
    description = self.description[:30]
    status = "👀" if self.seen else "🔒"

    return f'{user_info} ({description[:17]}...) {status}'


# handle (tool record) in database and (tool views and models)
class ToolViewsFunctions(models.Model):
  name = models.CharField(max_length=120, unique=True)
  tool = models.ForeignKey(Tool, on_delete=models.SET_NULL, related_name='tool_views',blank=True, null=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = ToolViewsFunctionsManager()

  def __str__(self):
    return self.name

class ToolDatabaseClass(models.Model):
  name = models.CharField(max_length=120, unique=True)
  tool = models.OneToOneField(Tool, on_delete=models.SET_NULL, related_name='tool_db', blank=True, null=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    return self.name
