import logging

from django.conf.global_settings import LOGGING
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from muver_api.models import UserProfile, Job
from muver_api.permissions import IsOwnerOrReadOnly, IsOwnerOrMoverOrReadOnly
from muver_api.serializers import UserSerializer, UserProfileSerializer, \
    JobSerializer, StripeAccountSerializer, \
    CustomerSerializer, StrikeSerializer
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)
logger.info("muver_api.views logger")


# def url_please(request):
#     logger.info("path: %s" % request.path)
#     return HttpResponse(request.path)


# class ObtainAuthTokenWithUserID(ObtainAuthToken):
#    def post(self, request):
#        serializer = self.serializer_class(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        user = serializer.validated_data['user']
#        token, created = Token.objects.get_or_create(user=user)
#        user_id = user.id
#        profile_id = user.profile.id
#        return Response({'token': token.key, 'id': user_id,
#                         'profile_id': profile_id})


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

        logger.error(serializer.errors)

        serializer.save(user=self.request.user)

    def get_queryset(self):

        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('lng', None)
        sort = self.request.query_params.get('sort', None)

        if latitude and longitude:
            qs = super().get_queryset()
            pnt = GEOSGeometry(
                'POINT(' + str(longitude) + ' ' + str(latitude) + ')',
                srid=4326)
            new_query = qs.filter(mover_profile=None) \
                .filter(complete=False).exclude(conflict=True).annotate(
                distance=Distance('point_a', pnt))
            if sort == "price-low":
                return new_query.order_by('distance', 'price')
            elif sort == "price-high":
                return new_query.order_by('distance', '-price')
            elif sort == "dist-low":
                return new_query.order_by('distance', 'trip_distance')
            elif sort == "dist-high":
                return new_query.order_by('distance', '-trip_distance')
            else:
                new_query.order_by('distance')
                return qs

        else:
            without_location = Job.objects.filter(mover_profile=None).filter(
                complete=False).exclude(conflict=True)
            sort = self.request.GET.get('sort', '')

            if sort == "price-low":
                return without_location.order_by('price')
            elif sort == "price-high":
                return without_location.order_by('-price')
            elif sort == "dist-low":
                return without_location.order_by('trip_distance')
            elif sort == "dist-high":
                return without_location.order_by('-trip_distance')
            else:
                return without_location.order_by('-created_at')


class JobsByUser(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        if not user.profile.mover:
            return Job.objects.filter(user=user).filter(confirmation_user=False) \
                .exclude(conflict=True).order_by("-modified_at")
        else:
            profile = user.profile
            return Job.objects.filter(mover_profile=profile.id)\
                .filter(confirmation_mover=False).exclude(conflict=True)\
                .order_by("-modified_at")


class CompletedJobsByUser(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        if not user.profile.mover:
            return Job.objects.filter(user=user).filter(confirmation_user=True) \
                .exclude(conflict=True).order_by("-modified_at")
        else:
            return Job.objects.filter(mover_profile=user.profile.id) \
                .exclude(conflict=True).filter(confirmation_mover=True)\
                .order_by("-modified_at")


class RetrieveUpdateDestroyJob(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (IsOwnerOrMoverOrReadOnly,)


class CreateCustomer(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(None, status=status.HTTP_201_CREATED)

        logger.error("ERROR: Customer stripe account creation failed with:\n"
                     "{}\nUser: {}".format(serializer.errors, request.user))

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccount(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request):
        serializer = StripeAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(None, status=status.HTTP_201_CREATED)

        logger.error("ERROR: Stripe managed account creation failed with:\n"
                     "{}\nUser: {}".format(serializer.errors, request.user))

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CreateStrike(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request):
        serializer = StrikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(None, status=status.HTTP_201_CREATED)
        logger.error("ERROR: Strike failed creation. \n{}".format(
            serializer.errors))

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
