from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponse

from .classes.FileManager import FileManager
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
    fm = FileManager()

    errors = {
      'text': (lambda text: text == '', 'cant find any text in the request'),
      'file_name': (lambda file_name: '/' in str(file_name), f'filename is not valid.'),
      'location': (lambda location: not fm.is_file_exist(location), 'file is not exist')
    }

    for name, value in kwargs.items():
      error = errors.get(name, (lambda x: False, ''))
      condition_func, msg = error
      if condition_func(value):
        raise ValidationError(msg)


  # polumorphism methods
  @staticmethod
  def check_user_has_records(user):
    exist = TextSaverModel.objects.filter(user=user).first()
    return bool(exist)

  @staticmethod
  def check_user_has_new_records(user):
    exist = TextSaverModel.objects.filter(user=user, seen=False).first()
    return bool(exist)


  @staticmethod
  def add(acc, text, file_name):
    TextSaverModel.validate(text=text, file_name=file_name)

    fm = FileManager()

    file_name = file_name or f'{secrets.token_hex(nbytes=8)}.txt'
    folder_name = TextSaverModel.get_folder(acc)
    location = os.path.join(folder_name, file_name)
    fm.write(location, text+'\n', mode='a', force_location=True)

    file_url = TextSaverModel.get_file_path(file_name)

    try: TextSaverModel.objects.create(user=acc.user, file_name=file_name)
    except: pass

    return file_url

  @staticmethod
  def list_all(user):
    # acc = Account.objects.get(user=user)

    # fm = FileManager()

    # folder_name = TextSaverModel.get_folder(acc)
    # files_names = fm.listdir(folder_name)
    # files_read_paths = [TextSaverModel.get_file_path(f) for f in files_names]
    # files_delete_path = [TextSaverModel.get_delete_path(f) for f in files_names]

    # return list(zip(files_read_paths, files_delete_path))

    return TextSaverModel.objects.filter(user=user)

  @staticmethod
  def delete(acc, file_name):
    TextSaverModel.validate(file_name=file_name)

    fm = FileManager()

    folder_name = TextSaverModel.get_folder(acc)
    location = os.path.join(folder_name, file_name)
    delete_status = fm.delete(location)

    TextSaverModel.objects.filter(user=acc.user, file_name=file_name).delete()
    return delete_status

  @staticmethod
  @login_required
  def read(acc, file_name):
    fm = FileManager()

    folder_name = TextSaverModel.get_folder(acc)
    location = os.path.join(folder_name, file_name)

    TextSaverModel.validate(file_name=file_name, location=location)

    return location


