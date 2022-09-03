import importlib
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from utils import emoji
from utils.mixins import OptimizeImageField

import secrets

from .managers import  (
  UpcomingToolManager,
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
  LOGO_MINIMUM_DIMENSION = 170
  # required
  name = models.CharField(max_length=128)
  app_type = models.CharField(max_length=32) # api || web based
  tool_id = models.CharField(max_length=128, unique=True, editable=False, blank=True, db_index=True)
  logo = models.ImageField(upload_to='tool_logo', blank=True, null=True)
  description = models.TextField(blank=True, null=True) # SEO && after title
  url_reverser = models.CharField(max_length=64, default='toolsframe:tool') # 'app_name:home'
  endpoints = models.JSONField(blank=True, null=True)
  manager_class = models.CharField(max_length=64, blank=True, null=True)

  category = models.ManyToManyField(Category, related_name='category_tools')

  login_required = models.BooleanField(default=False)
  active = models.BooleanField(default=True, db_index=True)
  has_db = models.BooleanField(default=False)

  uses_count = models.IntegerField(default=0)
  views_count = models.IntegerField(default=0)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = ToolManager()

  class Meta:
    verbose_name = 'Tool'
    verbose_name_plural = 'Tools'

  def __str__(self):
    status = emoji.ACTIVE if self.active else emoji.DISABLE
    return f'{self.pk}- {self.tool_id} {status}{" | NoImage" if not self.logo else ""}'

  def save(self, *args, **kwargs):
    if not self.pk and not self.tool_id:
      self.tool_id = slugify(self.name + ' ' + secrets.token_hex(nbytes=4))

    if self.logo:
      OptimizeImageField(self.logo, self.LOGO_MINIMUM_DIMENSION)

    return super(Tool, self).save(*args, **kwargs)

  def get_absolute_url(self):
    try:
      url = reverse(self.url_reverser)
    except:
      url = reverse(self.url_reverser, kwargs={'tool_id':self.tool_id})

    return url

  def get_manager_instance(self):
    module_path, class_name = self.manager_class.rsplit('.', 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()

  @property
  def db_class(self):
    manager_instance = self.get_manager_instance()
    db = manager_instance.get_db_table()
    return db

  def get_db_records(self, user):
    db = self.db_class
    return db and db.list_all(user) or []

  def increase_uses_count(self):
    self.uses_count += 1
    self.save()


class UpcomingTool(models.Model):
  name = models.CharField(max_length=128)
  description = models.TextField()

  upvote = models.IntegerField(blank=True, null=True, default=0)
  downvote = models.IntegerField(blank=True, null=True, default=0)

  active = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = UpcomingToolManager()

  class Meta:
    indexes = [
      models.Index(fields=['active'], name='upcoming_active_idx')
    ]

  def __str__(self):
    status = emoji.ACTIVE if self.active else emoji.DISABLE
    return f'{self.name} {status}'


class SuggestedTool(models.Model):
  user = models.ForeignKey(User, related_name='user_suggested_tools', on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField()

  seen = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    user = self.user
    username = user.username if user else 'Anonymous' 
    description = self.description[:30]
    status = emoji.SEEN if self.seen else emoji.UN_SEEN

    return f'{self.pk} - {username} {username} ({description}) {status}'


class ToolIssueReport(models.Model):
  tool =  models.ForeignKey(Tool, related_name='tool_issue_reports', on_delete=models.CASCADE)
  user = models.ForeignKey(User, related_name='user_issue_reports', on_delete=models.SET_NULL, blank=True, null=True)
  description = models.TextField()

  seen = models.BooleanField(default=False)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def __str__(self):
    user = self.user
    username = user.username if user else 'Anonymous' 
    description = self.description[:30]
    status = emoji.SEEN if self.seen else emoji.UN_SEEN

    return f'{self.pk} - {username} {username} ({description}) {status}'


