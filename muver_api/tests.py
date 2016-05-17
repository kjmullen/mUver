import time

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
        data = {"title": "test title", "price": 80, "pickup_for": "tester mctesterson",
                "phone_number": "8056376389", "destination_a": "las vegas, nv",
                "destination_b": "henderson, nv"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 2)
        self.assertEqual(data['title'], 'test title')
        self.assertEqual(self.user.profile, UserProfile.objects.first())

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
        mover_profile.mover = True
        mover_profile.save()

