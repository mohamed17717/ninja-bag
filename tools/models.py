from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponse

from classes.FileManager import FileManager
from accounts.models import Account

import os, secrets

from decorators import login_required


User = get_user_model()

class TextSaverModel(models.Model):
  user = models.ForeignKey(User, related_name='user_text_saver_tool_records', on_delete=models.CASCADE)
  seen = models.BooleanField(default=False)
  file_name = models.CharField(max_length=50, unique=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  def get_absolute_url_read(self):
    return reverse('tools:textsaver-read', kwargs={'file_name': self.file_name})

  def get_absolute_url_delete(self):
    return reverse('tools:textsaver-delete', kwargs={'file_name': self.file_name})

  # handler methods
  @staticmethod
  def get_folder(acc):
    user_folder = acc.get_user_folder_location()
    location = os.path.join(user_folder, 'text-saver/')
    return location

  @staticmethod
  def get_file_path(file_name):
    path = reverse('tools:textsaver-read', kwargs={'file_name': file_name})
    return path

  @staticmethod
  def get_delete_path(file_name):
    path = reverse('tools:textsaver-delete', kwargs={'file_name': file_name})
    return path

  @staticmethod
  def validate(**kwargs):
    errors = {
      'text': (lambda text: text == '', 'cant find any text in the request'),
      'file_name': (lambda file_name: '/' in str(file_name), f'filename is not valid.'),
      'location': (lambda location: not FileManager.is_file_exist(location), 'file is not exist')
    }

    for name, value in kwargs.items():
      error = errors.get(name, (lambda x: False, ''))
      condition_func, msg = error
      if condition_func(value):
        raise ValidationError(msg)


  # polumorphism methods
  @classmethod
  def check_user_has_records(cls, user):
    exist = cls.objects.filter(user=user).first()
    return bool(exist)

  @classmethod
  def check_user_has_new_records(cls, user):
    exist = cls.objects.filter(user=user, seen=False).first()
    return bool(exist)


  @classmethod
  def add(cls, acc, text, file_name):
    cls.validate(text=text, file_name=file_name)

    file_name = file_name or f'{secrets.token_hex(nbytes=8)}.txt'
    folder_name = cls.get_folder(acc)
    location = os.path.join(folder_name, file_name)
    FileManager.write(location, text+'\n', mode='a', force_location=True)

    file_url = cls.get_file_path(file_name)

    try: cls.objects.create(user=acc.user, file_name=file_name)
    except: pass

    return file_url

  @classmethod
  def list_all(cls, user):
    return cls.objects.filter(user=user)

  @classmethod
  def delete(cls, acc, file_name):
    cls.validate(file_name=file_name)

    folder_name = cls.get_folder(acc)
    location = os.path.join(folder_name, file_name)
    delete_status = FileManager.delete(location)

    cls.objects.filter(user=acc.user, file_name=file_name).delete()
    return delete_status

  @classmethod
  def read(cls, acc, file_name):
    folder_name = cls.get_folder(acc)
    location = os.path.join(folder_name, file_name)

    cls.validate(file_name=file_name, location=location)

    return location


