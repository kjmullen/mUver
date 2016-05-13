import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True,
                                related_name="profile")
    mover = models.BooleanField(default=False)
    stripe_account_id = models.CharField(max_length=24, null=True, blank=True)
    customer_id = models.CharField(max_length=24, null=True, blank=True)
    in_progress = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    display_name = models.CharField(max_length=50, default=None, null=True,
                                    blank=True)
    phone_number = models.CharField(max_length=10, default=None, null=True,
                                    blank=True)

    def ban_user(self):
        self.banned = True
        self.in_progress = False
        self.user.is_active = False
        self.save()
        self.user.save()

    def unban_user(self):
        self.banned = False
        self.user.is_active = True
        self.save()
        self.user.save()

    def __str__(self):
        return self.user.username


class Job(models.Model):
    title = models.CharField(max_length=65)
    pickup_for = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    user = models.ForeignKey(User, related_name="jobs")
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    price = models.IntegerField()
    charge_id = models.CharField(max_length=60, null=True, blank=True)
    mover_profile = models.ForeignKey(UserProfile, null=True, blank=True)
    complete = models.BooleanField(default=False)
    conflict = models.BooleanField(default=False)
    image_url = models.URLField(null=True, blank=True)
    destination_a = models.CharField(max_length=80)
    destination_b = models.CharField(max_length=80)
    distance = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmation_user = models.BooleanField(default=False)
    confirmation_mover = models.BooleanField(default=False)
    report_user = models.BooleanField(default=False)
    strike_mover = models.BooleanField(default=False)
    repost = models.BooleanField(default=False)
    status = models.CharField(max_length=80, null=True, blank=True)

    def job_posted(self):
        self.status = "Job needs a mover."
        self.user.profile.in_progress = True
        self.user.profile.save()
        self.save()

    def in_progress(self):
        self.status = "Mover accepted job."
        self.mover_profile.in_progress = True
        self.mover_profile.save()
        self.save()

    def job_conflict(self):
        self.status = "A conflict occurred with user/mover."
        self.conflict = True
        self.user.profile.in_progress = False
        self.user.profile.save()
        self.mover_profile.in_progress = False
        self.mover_profile.save()
        self.save()

    def mover_finished(self):
        if not self.confirmation_user:
            self.status = "Mover set the job to complete. " \
                          "Waiting for user confirmation."
        else:
            self.status = "Job complete."
            charge = stripe.Charge.retrieve(self.charge_id)
            fee = int(charge.amount * 0.20)
            charge.capture(application_fee=fee)
        self.confirmation_mover = True
        self.save()

    def user_finished(self):
        if not self.confirmation_mover:
            self.status = "User set the job to complete. " \
                          "Waiting for mover confirmation."
        else:
            self.status = "Job complete."
            self.complete = True
            charge = stripe.Charge.retrieve(self.charge_id)
            fee = int(charge.amount * 0.20)
            charge.capture(application_fee=fee)
        self.confirmation_user = True
        self.save()

    def job_complete(self):
        self.status = "Job complete."
        self.complete = True
        self.save()

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
    job = models.ForeignKey(Job, related_name="strikes")
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

