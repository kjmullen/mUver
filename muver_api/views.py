import logging

from django.conf.global_settings import LOGGING
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from muver_api.models import UserProfile, Job
from muver_api.permissions import IsOwnerOrReadOnly, IsOwnerOrMoverOrReadOnly
from muver_api.serializers import UserSerializer, UserProfileSerializer, \
    JobSerializer, StripeAccountSerializer, \
    CustomerSerializer
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)
logger.info("muver_api.views logger")  # should work


# def url_please(request):
#     logger.info("path: %s" % request.path)  # should work
#     return HttpResponse(request.path)


class ObtainAuthTokenWithUserID(ObtainAuthToken):
   def post(self, request):
       serializer = self.serializer_class(data=request.data)
       serializer.is_valid(raise_exception=True)
       user = serializer.validated_data['user']
       token, created = Token.objects.get_or_create(user=user)
       user_id = user.id
       profile_id = user.profile.id
       return Response({'token': token.key, 'id': user_id,
                        'profile_id': profile_id})


class DetailUser(generics.RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUser(generics.CreateAPIView):

    model = User
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class DetailUserProfile(APIView):

    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)


class ListUserProfile(generics.ListAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RetrieveUpdateUserProfile(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)


class ListCreateJob(generics.ListCreateAPIView):

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobsByUser(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        return Job.objects.filter(user=user)


class CompletedJobsByUser(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        return Job.objects.filter(user=user).filter(complete=True)


class RetrieveUpdateDestroyJob(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrMoverOrReadOnly,)


    # def get_permissions(self):
    #     if self.request.job.mover_profile:
    #         permission_classes = (IsAuthenticatedOrReadOnly,)
    #     else:
    #         permission_classes = (IsOwnerOrReadOnly,)
    #     return super().get_permissions()

#
# class CreateCharge(APIView):
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     def post(self, request):
#         serializer = ChargeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(None, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,
#                         status=status.HTTP_400_BAD_REQUEST)


class CreateCustomer(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(None, status=status.HTTP_201_CREATED)
        logger.error(serializer.errors)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccount(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request):
        serializer = StripeAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(None, status=status.HTTP_201_CREATED)

        # logger.info("error with stripe account creation")
        # logger.debug(serializer)
        logger.error(serializer.errors)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
