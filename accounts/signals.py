from django.contrib.auth import get_user_model

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile

from .models import Account

import requests

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
  if created:
    Account.objects.create(user=instance)

# used in pipeline when login with social accounts
def get_avatar(backend, user, response, is_new, *args, **kwargs):
  if is_new:
    # get image url
    pic_key_name = {
      'google-oauth2': 'picture',
      'github': 'avatar_url'
    }.get(backend.name)

    pic_url = response.get(pic_key_name)
    if not pic_url: return

    # request the url and get the pic
    try:
      res = requests.get(pic_url)
      pic = ContentFile(res.content)
      assert pic
    except: return

    # set pic to its db field
    account = Account.objects.filter(user=user).first()

    pic_name = slugify(user.username + " social") + '.jpg'
    account.picture.save(pic_name, pic)
    account.save()
