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

    def __str__(self):
        return self.user.username


class Job(models.Model):
    title = models.CharField(max_length=65)
    description = models.CharField(max_length=300, null=True, blank=True)
    user = models.ForeignKey(User, related_name="jobs")
    price = models.IntegerField()
    charge_id = models.CharField(max_length=60)
    mover_profile = models.ForeignKey(UserProfile, null=True, blank=True)
    complete = models.BooleanField(default=False)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)

