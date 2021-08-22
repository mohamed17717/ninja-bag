from django.db import models


class ToolDatabaseQuerySet(models.QuerySet):
  def check_user_has_records(self, user):
    return bool(self.filter(user=user).first())

  def check_user_has_new_records(self, user):
    return bool(self.filter(user=user, seen=False).first())


class ToolDatabaseManager(models.Manager):
  def get_queryset(self):
    return ToolDatabaseQuerySet(self.model, using=self._db, hints=self._hints)

  def check_user_has_records(self, user):
    return self.get_queryset().check_user_has_records(user)

  def check_user_has_new_records(self, user):
    return self.get_queryset().check_user_has_new_records(user)


