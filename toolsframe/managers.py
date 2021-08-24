from django.db import models
from django.shortcuts import get_object_or_404


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

class ToolViewsFunctionsQuerySet(models.QuerySet):
  def get_active(self):
    return self.filter(active=True)

  def reverse_view_func_to_tool(self, func):
    view_obj = self.filter(name=func.__name__).first()
    tool = view_obj and view_obj.tool
    return tool


class ToolViewsFunctionsManager(models.Manager):
  def get_queryset(self):
    return ToolViewsFunctionsQuerySet(model=self.model, using=self._db, hints=self._hints)

  def reverse_view_func_to_tool(self, func):
    return self.get_queryset().reverse_view_func_to_tool(func)

# ------------------------------------------------------------- #

class ToolQuerySet(models.QuerySet):
  def get_tools_that_has_db(self):
    return self.filter(tool_db__isnull=False)

  def get_tools_that_has_db_for_aside_section(self, user):
    # tools that user has records in && flag tell if there is new record
    tools = self.get_tools_that_has_db()
    chosen_ones = []
    for tool in tools:
      db = tool.get_db_class()
      if db.objects.check_user_has_records(user):
        chosen_ones.append((tool, db.objects.check_user_has_new_records(user)))

    return chosen_ones

  def list_for_homepage(self):
    return self.filter(active=True)

  def increase_uses_count_by_pk(self, pk):
    tool = self.filter(pk=pk).first()
    tool and tool.increase_uses_count()

  def get_tool_by_tool_id(self, tool_id):
    return self.filter(tool_id=tool_id).first()

  def force_get(self, **kwargs):
    return get_object_or_404(self.model, **kwargs)




class ToolManager(models.Manager):
  def get_queryset(self):
    return ToolQuerySet(model=self.model, using=self._db, hints=self._hints)

  def get_tools_that_has_db(self):
    return self.get_queryset().get_tools_that_has_db()

  def get_tools_that_has_db_for_aside_section(self, user):
    return self.get_queryset().get_tools_that_has_db_for_aside_section(user)

  def list_for_homepage(self):
    return self.get_queryset().list_for_homepage()

  def increase_uses_count_by_pk(self, pk):
    return self.get_queryset().increase_uses_count_by_pk(pk)

  def get_tool_by_tool_id(self, tool_id):
    return self.get_queryset().get_tool_by_tool_id(tool_id)

  def force_get(self, **kwargs):
    return self.get_queryset().force_get(**kwargs)

# ------------------------------------------------------------- #
