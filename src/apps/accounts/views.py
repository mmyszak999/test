from rest_framework import permissions, generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from src.apps.accounts.models import UserAddress, UserProfile
from src.apps.accounts.serializers import (
    RegistrationInputSerializer,
    UserAddressOutputSerializer,
    UserProfileListOutputSerializer,
    UserProfileDetailOutputSerializer,
    RegistrationOutputSerializer,
    UserProfileUpdateInputSerializer,
)
from src.apps.accounts.services import UserProfileService


class UserProfileListAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListOutputSerializer

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(user=user)


class UserProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailOutputSerializer
    service_class = UserProfileService

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(user=user)

    @swagger_auto_schema(request_body=UserProfileUpdateInputSerializer)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserProfileUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_userprofile = self.service_class.update_user(
            instance=instance, data=serializer.validated_data
        )
        return Response(
            self.get_serializer(updated_userprofile).data, status=status.HTTP_200_OK
        )


class UserRegisterAPIView(generics.GenericAPIView):
    serializer_class = RegistrationOutputSerializer
    permission_classes = [permissions.AllowAny]
    service_class = UserProfileService

    @swagger_auto_schema(
        request_body=RegistrationInputSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = RegistrationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_profile = self.service_class.register_user(data=serializer.validated_data)
        return Response(
            self.get_serializer(user_profile).data,
            status=status.HTTP_201_CREATED,
        )


class AdressListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressOutputSerializer

    def get_queryset(self):
        qs = self.queryset
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(userprofile__user=user)
