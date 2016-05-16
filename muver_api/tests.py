import stripe
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from muver_api.models import Job
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class TestListCreateJob(APITestCase):

    def setUp(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        self.user = User.objects.create_user(username="test",
                                             email="",
                                             password="password")
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
