from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .managers import ToolDatabaseManager
from utils.helpers import FileManager

import os, secrets


User = get_user_model()

class TextSaverModel(models.Model):
  user = models.ForeignKey(User, related_name='user_text_saver_tool_records', on_delete=models.CASCADE)
  seen = models.BooleanField(default=False)
  file_name = models.CharField(max_length=50, unique=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)

  objects = ToolDatabaseManager()

  def get_absolute_url_read(self):
    return reverse(f'tools:text-saver-simple-db-read', kwargs={'filename': self.file_name})

  def get_absolute_url_delete(self):
    return reverse(f'tools:text-saver-simple-db-delete', kwargs={'filename': self.file_name})

  # handler methods
  @staticmethod
  def get_folder(acc):
    user_folder = acc.get_user_folder_location()
    location = os.path.join(user_folder, 'text-saver/')
    return location

  @staticmethod
  def get_file_path(file_name):
    path = reverse('tools:text-saver-simple-db-read', kwargs={'filename': file_name})
    return path

  @staticmethod
  def get_delete_path(file_name):
    path = reverse('tools:text-saver-simple-db-delete', kwargs={'filename': file_name})
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


  # polymorphism methods
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
    result = []
    if user.is_authenticated: 
      result = cls.objects.get_user_records(user)
      result.select_for_update().update(seen=True)

    return result

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


class FHostModel(models.Model):
  file_name = models.CharField(max_length=80, db_index=True, unique=True)
  text = models.TextField()
  is_public = models.BooleanField(default=True)
  allowed_origins = models.TextField(blank=True, null=True)

  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)


  def __str__(self):
    return self.file_name

