import time
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from muver_api.models import UserProfile, Job
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    def update(self, instance, validated_data):
        instance.mover_profile = validated_data.get(
            'mover_profile', instance.mover_profile)
        instance.confirmation_mover = validated_data.get(
            'confirmation_mover', instance.confirmation_mover)
        instance.confirmation_user = validated_data.get(
            'confirmation_user', instance.confirmation_user)
        return super().update(instance, validated_data)

    class Meta:
        model = Job
        fields = "__all__"


class ChargeSerializer(serializers.Serializer):

    token = serializers.CharField(max_length=60)
    amount = serializers.IntegerField()
    title = serializers.CharField(max_length=65)
    description = serializers.CharField(max_length=300,
                                        required=False,
                                        default=None)
    save_billing = serializers.BooleanField(default=False)
    destination_a = serializers.CharField(max_length=80)
    destination_b = serializers.CharField(max_length=80)
    phone_number = serializers.CharField(max_length=10)
    # confirmation_mover = serializers.BooleanField(required=False,
    #                                               default=False)
    # confirmation_user = serializers.BooleanField(required=False,
    #                                              default=False)

    def create(self, validated_data):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = validated_data['amount']
        user = validated_data['user']
        title = validated_data['title']
        description = validated_data['description']
        phone_number = validated_data['phone_number']
        destination_a = validated_data['destination_a']
        destination_b = validated_data['destination_b']
        token = validated_data['token']
        save = validated_data['save_billing']

        try:
            if save:
                customer = stripe.Customer.create(
                    source=token,
                    description="mUver customer"
                )
                user.profile.customer_id = customer['id']
                user.profile.save()

                charge = stripe.Charge.create(
                    amount=amount * 100,
                    currency="usd",
                    customer=customer['id'],
                    capture=False
                )
                price = charge['amount'] / 100
                job = Job.objects.create(user=user,
                                         price=price,
                                         charge_id=charge['id'],
                                         title=title,
                                         description=description,
                                         phone_number=phone_number,
                                         destination_a=destination_a,
                                         destination_b=destination_b
                                         )
                return job
            else:
                charge = stripe.Charge.create(
                    amount=amount * 100,
                    currency='usd',
                    source=token,
                    description="Charge for mUver job",
                    capture=False,
                )
                price = charge['amount'] / 100
                job = Job.objects.create(user=user,
                                         price=price,
                                         charge_id=charge['id'],
                                         title=title,
                                         description=description,
                                         phone_number=phone_number,
                                         destination_a=destination_a,
                                         destination_b=destination_b
                                         )
                return job
        except stripe.error.CardError as e:
            pass

    def update(self, instance, validated_data):
        pass


class StripeAccountSerializer(serializers.Serializer):

    country = serializers.CharField(max_length=4, default='US')
    currency = serializers.CharField(max_length=5, default='usd')
    account_number = serializers.CharField(max_length=17)
    routing_number = serializers.CharField(max_length=9)
    first_name = serializers.CharField(max_length=35)
    last_name = serializers.CharField(max_length=35)
    dob_month = serializers.IntegerField(max_value=12)
    dob_day = serializers.IntegerField(max_value=31)
    dob_year = serializers.IntegerField()
    address_line_one = serializers.CharField(max_length=40)
    address_line_two = serializers.CharField(max_length=40,
                                             required=False, default=None)
    address_city = serializers.CharField(max_length=40)
    address_state = serializers.CharField(max_length=2)
    postal_code = serializers.CharField(max_length=10)
    ssn_last_four = serializers.IntegerField(max_value=9999)

    def create(self, validated_data):

        stripe.api_key = settings.STRIPE_SECRET_KEY
        country = validated_data['country']
        currency = validated_data['currency']
        account_number = validated_data['account_number']
        routing_number = validated_data['routing_number']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        dob_month = validated_data['dob_month']
        dob_day = validated_data['dob_day']
        dob_year = validated_data['dob_year']
        address_line_one = validated_data['address_line_one']
        address_line_two = validated_data['address_line_two']
        address_city = validated_data['address_city']
        address_state = validated_data['address_state']
        postal_code = validated_data['postal_code']
        ssn_last_four = validated_data['ssn_last_four']

        try:
            account = stripe.Account.create(
                country=country,
                managed=True,
            )
            account.tos_acceptance.date = int(time.time())
            account.tos_acceptance.ip = '24.234.237.43'
            account.save()

            account.legal_entity.first_name = first_name
            account.legal_entity.last_name = last_name
            account.legal_entity.dob.month = dob_month
            account.legal_entity.dob.day = dob_day
            account.legal_entity.dob.year = dob_year
            account.legal_entity.type = "individual"

            bank_info_dict = {"object": "bank_account", "country": country,
                              "currency": currency,
                              "routing_number": routing_number,
                              "account_number": account_number}

            account.external_accounts.create(external_account=bank_info_dict)

            account.legal_entity.address.line1 = address_line_one
            account.legal_entity.address.line2 = address_line_two
            account.legal_entity.address.postal_code = postal_code
            account.legal_entity.address.city = address_city
            account.legal_entity.address.state = address_state
            account.legal_entity.ssn_last_4 = ssn_last_four
            account.save()

            user = validated_data['user']
            user.profile.stripe_account_id = account['id']
            user.profile.save()

            return account

        except stripe.error.InvalidRequestError as e:
            pass

    def update(self, instance, validated_data):
        pass

# class CaptureChargeSerializer(serializers.Serializer):
#
#     charge_id = serializers.CharField(max_length=60)
#
#     def create(self, validated_data):
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         charge = stripe.Charge.retrieve(validated_data['charge_id'])
#         charge.capture()
