from django.contrib.auth import get_user_model

from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Profile


User = get_user_model()

#example
# create profile on create user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)
