from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True,
                                related_name="profile")
    mover = models.BooleanField(default=False)
    billing_saved = models.BooleanField(default=False)

#
# class Job(models.Model):
#     title = models.CharField(max_length=65)
#     description = models.CharField(max_length=300)
#     user = models.ForeignKey(User, related_name="jobs")
#     price = models.IntegerField()
#     complete = models.BooleanField(default=False)
#     in_progress = models.BooleanField(default=False)
#     charge_id = models.CharField(max_length=60)
#     mover_profile = models.ForeignKey(UserProfile, null=True, blank=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)

