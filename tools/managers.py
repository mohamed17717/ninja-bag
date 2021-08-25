from django.db import models


class ToolDatabaseQuerySet(models.QuerySet):
  def get_user_records(self, user):
    return self.filter(user=user)
  
  def check_user_has_records(self, user):
    return self.get_user_records(user).exists()

  def check_user_has_new_records(self, user):
    return self.filter(user=user, seen=False).exists()


class ToolDatabaseManager(models.Manager):
  def get_queryset(self):
    return ToolDatabaseQuerySet(self.model, using=self._db, hints=self._hints)

  def get_user_records(self, user):
    return self.get_queryset().get_user_records(user)

  def check_user_has_records(self, user):
    return self.get_queryset().check_user_has_records(user)

  def check_user_has_new_records(self, user):
    return self.get_queryset().check_user_has_new_records(user)


