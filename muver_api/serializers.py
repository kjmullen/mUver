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

    mover_profile = UserProfileSerializer

    class Meta:
        model = Job
        fields = "__all__"
