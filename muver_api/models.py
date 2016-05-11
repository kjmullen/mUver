import stripe
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
    stripe_account_id = models.CharField(max_length=24, null=True, blank=True)
    customer_id = models.CharField(max_length=24, null=True, blank=True)
    in_progress = models.BooleanField(default=False)
    # strikes = models.OneToManyField(Strikes)

    def __str__(self):
        return self.user.username


class Job(models.Model):
    title = models.CharField(max_length=65)
    description = models.CharField(max_length=300, null=True, blank=True)
    user = models.ForeignKey(User, related_name="jobs")
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    price = models.IntegerField()
    charge_id = models.CharField(max_length=60, null=True, blank=True)
    mover_profile = models.ForeignKey(UserProfile, null=True, blank=True)
    complete = models.BooleanField(default=False)
    image_url = models.URLField(null=True, blank=True)
    destination_a = models.CharField(max_length=80)
    destination_b = models.CharField(max_length=80)
    distance = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmation_user = models.BooleanField(default=False)
    confirmation_mover = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def capture_charge(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        charge = stripe.Charge.retrieve(self.charge_id)
        mover = UserProfile.objects.get(pk=self.mover_profile.id)
        charge.destination = mover.stripe_account_id
        charge.application_fee = charge.amount * 0.20
        self.complete = True
        charge.capture()
        return charge


class Strike(models.Model):
    user = models.ForeignKey(User, related_name="strikes")
    profile = models.ForeignKey(UserProfile, related_name="strikes")
    comment = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "Strike on {} from {}".format(self.profile, self.user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserProfile.objects.create(user=instance)

