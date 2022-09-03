from django.db import models
from django.db.models import F
from django.shortcuts import get_object_or_404
from utils.decorators import cache_counter

# ------------------------------------------------------------- #

class UpcomingToolQuerySet(models.QuerySet):
  def get_active(self):
    return self.filter(active=True)

class UpcomingToolManager(models.Manager):
  def get_queryset(self):
    return UpcomingToolQuerySet(model=self.model, using=self._db, hints=self._hints)

  def get_active(self):
    return self.get_queryset().get_active()

# ------------------------------------------------------------- #

class ToolQuerySet(models.QuerySet):
  def get_tools_that_has_db(self):
    return self.filter(has_db=True)

  def get_tools_that_has_db_for_aside_section(self, user):
    # tools that user has records in && flag tell if there is new record
    tools = self.get_tools_that_has_db()
    aside_tools = []
    for tool in tools:
      db = tool.db_class

      if db.objects.check_user_has_records(user):
        aside_tools.append((tool, db.objects.check_user_has_new_records(user)))

    return aside_tools

  def list_for_homepage(self):
    return self.filter(active=True).prefetch_related('category')

  def get_tool_by_tool_id(self, tool_id):
    return self.filter(tool_id=tool_id).first()

  def force_get(self, **kwargs):
    return get_object_or_404(self.model, **kwargs)

  @cache_counter('tool_views_{}')
  def increase_views_count(self, pk):
    self.select_for_update().filter(pk=pk).update(views_count=F('views_count')+100)

  @cache_counter('tool_uses_{}')
  def increase_uses_count(self, pk):
    self.select_for_update().filter(pk=pk).update(uses_count=F('uses_count')+100)

class ToolManager(models.Manager):
  def get_queryset(self):
    return ToolQuerySet(model=self.model, using=self._db, hints=self._hints)

  def get_tools_that_has_db(self):
    return self.get_queryset().get_tools_that_has_db()

  def get_tools_that_has_db_for_aside_section(self, user):
    return self.get_queryset().get_tools_that_has_db_for_aside_section(user)

  def list_for_homepage(self):
    return self.get_queryset().list_for_homepage()

  def increase_uses_count(self, pk):
    return self.get_queryset().increase_uses_count(pk)

  def get_tool_by_tool_id(self, tool_id):
    return self.get_queryset().get_tool_by_tool_id(tool_id)

  def force_get(self, **kwargs):
    return self.get_queryset().force_get(**kwargs)

  def increase_views_count(self, pk):
    return self.get_queryset().increase_views_count(pk)

# ------------------------------------------------------------- #

