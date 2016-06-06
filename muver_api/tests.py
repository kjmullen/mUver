import time
import datetime
from django.utils import timezone
import stripe
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from muver_api.models import Job, UserProfile
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class TestListCreateJob(APITestCase):

    def setUp(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        self.user = User.objects.create_user(username="test",
                                             email="",
                                             password="pass_word")
        self.mover_user = User.objects.create_user(username="mover_test",
                                                   email="",
                                                   password="pass_word")
        self.job = Job.objects.create(user=self.user,
                                      price=80,
                                      title="test title",
                                      pickup_for="tester mctesterson",
                                      phone_number="8056376389",
                                      destination_a="las vegas, nv",
                                      destination_b="henderson, nv",
                                      )

    def test_create_job(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        token = Token.objects.get(user_id=self.user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('list_create_job')
        data = {"title": "test title2", "price": 80, "pickup_for": "tester mctesterson",
                "phone_number": "8056376389", "destination_a": "las vegas, nv",
                "destination_b": "henderson, nv"}
        response = self.client.post(url, data, format='json')
        self.job.job_posted()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(data['title'], 'test title2')
        self.assertTrue(self.user.profile.in_progress, True)
        self.assertEqual(self.user.profile, UserProfile.objects.first())
        self.assertEqual(self.job.status, "Job needs a mover.")

    def test_add_mover(self):
        mover_profile = self.mover_user.profile
        mover_profile.mover = True
        account = stripe.Account.create(
            country='US',
            managed=True,
        )
        account.tos_acceptance.date = int(time.time())
        account.tos_acceptance.ip = '24.234.237.43'
        account.save()

        account.legal_entity.first_name = 'Jonathan'
        account.legal_entity.last_name = 'Goode'
        account.legal_entity.dob.month = '01'
        account.legal_entity.dob.day = '10'
        account.legal_entity.dob.year = '1986'
        account.legal_entity.type = "individual"

        bank_info_dict = {"object": "bank_account", "country": 'US',
                          "currency": 'usd',
                          "routing_number": "110000000",
                          "account_number": "000123456789"}

        account.external_accounts.create(external_account=bank_info_dict)

        account.legal_entity.address.line1 = "3180 18th St"

        account.legal_entity.address.postal_code = '94110'
        account.legal_entity.address.city = 'San Francisco'
        account.legal_entity.address.state = 'CA'
        account.legal_entity.ssn_last_4 = '1234'
        account.save()

        mover_profile.stripe_account_id = account['id']
        mover_profile.save()

    # def test_mover_on_job(self):
        mover_profile = self.mover_user.profile
        token = stripe.Token.create(
            card={
                "number": '4242424242424242',
                "exp_month": 12,
                "exp_year": 2017,
                "cvc": '123'
            },
        )
        customer = stripe.Customer.create(source=token['id'])
        charge = stripe.Charge.create(
            amount=self.job.price * 100,
            currency="usd",
            customer=customer,
            destination=mover_profile.stripe_account_id,
            capture=False,
        )
        self.job.charge_id = charge['id']
        self.job.mover_profile = mover_profile

        self.job.save()

        self.job.in_progress()
        self.assertEqual(self.job.mover_profile, self.mover_user.profile)
        self.assertEqual(self.job.status, "Mover accepted job.")

        self.assertFalse(self.job.time_check(), False)

        self.assertTrue(self.job.minutes_left() < 60, True)

        two_hours_old = timezone.now() - datetime.timedelta(hours=2)
        self.job.time_accepted = two_hours_old
        self.job.save()
        self.assertTrue(self.job.time_check(), True)

    # def test_users_complete_job(self):
        self.job.user_finished()
        self.assertFalse(self.user.profile.in_progress, False)

        self.job.mover_finished()
        self.assertFalse(self.mover_user.profile.in_progress, False)

        self.job.job_complete()
        self.assertTrue(self.job.complete, True)
        self.assertEqual(self.job.status, "Job complete.")

    def test_job_conflict(self):
        self.job.mover_profile = self.mover_user.profile
        self.job.job_conflict()
        self.assertEqual(self.job.status, "A conflict occurred with user/mover.")
        self.assertTrue(self.job.conflict, True)
        self.assertFalse(self.user.profile.in_progress, False)
        self.assertFalse(self.mover_user.profile.in_progress, False)


    def test_demo_user_reset(self):

        self.user.profile.demo_reset()
        self.assertFalse(self.user.profile.in_progress, False)
        self.assertEqual(self.user.jobs.count(), 0)

    def test_ban_unban_user(self):
        self.user.profile.ban_user()
        self.assertFalse(self.user.profile.in_progress, False)
        self.assertFalse(self.user.is_active, False)
        self.assertTrue(self.user.profile.banned, True)

        self.user.profile.unban_user()
        self.assertTrue(self.user.is_active, True)
        self.assertFalse(self.user.profile.banned, False)

