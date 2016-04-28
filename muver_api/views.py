from django.contrib.auth.models import User
from django.shortcuts import render
from muver_api.models import UserProfile, Job
from muver_api.serializers import UserSerializer, UserProfileSerializer, \
    JobSerializer
from rest_framework import generics
from rest_framework import permissions


class DetailUser(generics.RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUser(generics.CreateAPIView):

    model = User
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class DetailUserProfile(generics.RetrieveAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class ListUserProfile(generics.ListAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class ListCreateJob(generics.ListCreateAPIView):

    queryset = Job.objects.all()
    serializer_class = JobSerializer
