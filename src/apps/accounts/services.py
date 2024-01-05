from typing import Any
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from src.apps.accounts.models import UserProfile, UserAddress

User = get_user_model()


class UserProfileService:
    """
    Service for managing registration of UserProfile and
    updating it. Creates new addresses and deletes those, not used
    in any UserProfile.
    """

    @classmethod
    def _create_user(cls, data: dict[str, Any]) -> User:
        password = data.pop("password")
        user = User.objects.create(**data)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def _create_address(cls, data: dict[str, Any]) -> UserAddress:
        address, _ = UserAddress.objects.get_or_create(**data)
        return address

    @classmethod
    @transaction.atomic
    def register_user(cls, data: dict[str, Any]) -> UserProfile:
        user_data = data.pop("user")
        user_data.pop("repeat_password")
        address_data = data.pop("address")

        user = cls._create_user(data=user_data)
        address = cls._create_address(data=address_data)

        user_profile = UserProfile.objects.create(user=user, **data)
        user_profile.address.add(address)
        return user_profile

    @classmethod
    def _update_user(cls, instance: User, data: dict[str, Any]) -> User:
        instance.first_name = data.get("first_name", instance.first_name)
        instance.last_name = data.get("last_name", instance.last_name)
        instance.email = data.get("email", instance.email)
        instance.save()
        return instance

    @classmethod
    def _update_address(cls, data: dict[str, Any]) -> list:
        """
        Returns list of indexes of created/updated UserAdresses.
        """
        address_ids = []
        for address in data:
            address_instance, created = UserAddress.objects.update_or_create(
                pk=address.get("id"), defaults=address
            )
            address_ids.append(address_instance.pk)
        return address_ids

    @classmethod
    @transaction.atomic
    def update_user(cls, instance: UserProfile, data: dict[str, Any]) -> UserProfile:
        user_data = data.pop("user")
        address_data = data.pop("address", [])

        user = instance.user
        cls._update_user(instance=user, data=user_data)

        instance.address.set(cls._update_address(data=address_data))

        fields = ["phone_number", "birthday"]
        for field in fields:
            try:
                setattr(instance, field, data[field])
            except KeyError as err:
                raise err(f"{err} : Missing or wrong data")
        instance.save()

        # Removal of addresses not related to any UserProfile object
        addresses = set(UserProfile.objects.all().values_list("address", flat=True))
        addresses.discard(None)
        UserAddress.objects.filter(~Q(id__in=addresses)).delete()

        return instance
