from django.db import models
from django.core.exceptions import PermissionDenied


class AccountQuerySet(models.QuerySet):
  def get_user_acc_by_api_key(self, api_key, *, required=False):
    acc = self.filter(token=api_key).first()

    if required and not acc: 
      raise PermissionDenied('Not-Permited for this action.')

    return acc

  def get_user_acc_from_api_or_web(self, request, *, required=False):
    user = request.user.is_authenticated and request.user
    token = request.GET.get('token', 'blablabla')
    acc = user and self.get(user=user)
    acc = acc or self.get_user_acc_by_api_key(token, required=required)

    return acc

class AccountManager(models.Manager):
  def get_queryset(self):
    return AccountQuerySet(self.model, using=self._db, hints=self._hints)

  def get_user_acc_by_api_key(self, api_key, *, required=False):
    return self.get_queryset().get_user_acc_by_api_key(api_key, required=required)

  def get_user_acc_from_api_or_web(self, request, *, required=False):
    return self.get_queryset().get_user_acc_from_api_or_web(request, required=required)

