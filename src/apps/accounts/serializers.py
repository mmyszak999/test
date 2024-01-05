from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django_countries.serializers import CountryFieldMixin
from django_countries.serializer_fields import CountryField
from src.apps.accounts.models import UserAddress, UserProfile


User = get_user_model()


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        )
        read_only_fields = fields


class UserAddressOutputSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = (
            "id",
            "address_1",
            "address_2",
            "country",
            "state",
            "city",
            "postalcode",
        )
        read_only_fields = fields


class RegistrationOutputSerializer(serializers.ModelSerializer):

    user = UserOutputSerializer(many=False, read_only=True)
    address = UserAddressOutputSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "user",
            "phone_number",
            "birthday",
            "address",
        )
        read_only_fields = fields


class UserAddressInputSerializer(serializers.Serializer):
    address_1 = serializers.CharField()
    address_2 = serializers.CharField(required=False)
    country = CountryField()
    state = serializers.CharField(required=False)
    city = serializers.CharField()
    postalcode = serializers.CharField()


class UserInputSerializer(serializers.Serializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Username already in use!"
            )
        ]
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Email already in use!"
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )
    repeat_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    def validate(self, data):
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError(
                _("The two password fields didn't match.")
            )
        return data


class RegistrationInputSerializer(serializers.Serializer):

    user = UserInputSerializer(required=True)
    phone_number = serializers.CharField()
    birthday = serializers.DateField()
    address = UserAddressInputSerializer()


class UserUpdateInputSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()


class UserProfileUpdateInputSerializer(serializers.Serializer):
    user = UserUpdateInputSerializer(required=False)
    phone_number = serializers.CharField(required=False)
    birthday = serializers.DateField(required=False)
    address = UserAddressInputSerializer(many=True, required=False)


class UserProfileListOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(many=False, read_only=True)
    address = UserAddressOutputSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "phone_number",
            "birthday",
            "address",
        )
        read_only_fields = fields


class UserProfileDetailOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(many=False, read_only=True)
    address = UserAddressOutputSerializer(many=True, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "phone_number",
            "birthday",
            "address",
            "created",
            "updated",
        )
        read_only_fields = fields


class UserOrderOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = ("id", "user", "phone_number")
        read_only_fields = fields
