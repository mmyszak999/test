from django.contrib.auth import get_user_model
from django.test import TestCase

from src.apps.accounts.models import UserAddress, UserProfile
from src.apps.accounts.services import UserProfileService

User = get_user_model()


class TestUserProfileService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = UserProfileService

        cls.user_profile_data = {
            "user": {
                "username": "testuser1",
                "email": "testuser1@gmail.com",
                "first_name": "Jerry",
                "last_name": "Johnson",
                "password": "password123",
                "repeat_password": "password123",
            },
            "address": {
                "address_1": "Testowa 1/4",
                "address_2": "Test 7/5",
                "country": "PL",
                "city": "Radom",
                "postalcode": "00-001",
            },
            "phone_number": "+48692267650",
            "birthday": "1999-01-01",
        }
        cls.modified_user_profile_data = {
            "user": {
                "email": "testuser1@gmail.com",
                "first_name": "Jerry",
                "last_name": "Johnson",
            },
            "phone_number": "+48692267650",
            "birthday": "1999-01-02",
        }
        cls.modified_user_profile_data_one_address = {
            "user": {
                "email": "testuser1@gmail.com",
                "first_name": "Jerry",
                "last_name": "Johnson",
            },
            "address": [
                {
                    "id": 1,
                    "address_1": "Testowa 4/4",
                    "address_2": "Test 7/5",
                    "country": "PL",
                    "city": "Zielona Góra",
                    "postalcode": "00-002",
                },
            ],
            "phone_number": "+48692267650",
            "birthday": "1999-01-02",
        }

        cls.modified_user_profile_data_two_addresses = {
            "user": {
                "email": "testuser1@gmail.com",
                "first_name": "Jerry",
                "last_name": "Johnson",
            },
            "address": [
                {
                    "id": 1,
                    "address_1": "Testowa 4/4",
                    "address_2": "Test 7/5",
                    "country": "PL",
                    "city": "Zielona Góra",
                    "postalcode": "00-002",
                },
                {
                    "id": 2,
                    "address_1": "Test 4/9",
                    "address_2": "Testowa 9/1",
                    "country": "PL",
                    "city": "Białystok",
                    "postalcode": "00-001",
                },
            ],
            "phone_number": "+48692267650",
            "birthday": "1999-01-02",
        }

    def test_user_profile_service_correctly_creates_user(self):
        user_profile = self.service_class.register_user(data=self.user_profile_data)
        account_id = user_profile.id

        self.assertEqual(UserProfile.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserAddress.objects.all().count(), 1)

        self.assertEqual(UserProfile.objects.get(id=account_id), user_profile)

    def test_user_profile_service_correctly_updates_user_no_address(self):
        user_profile = self.service_class.register_user(data=self.user_profile_data)

        user_profile = self.service_class.update_user(
            instance=user_profile, data=self.modified_user_profile_data
        )
        account_id = user_profile.id

        self.assertEqual(UserProfile.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserAddress.objects.all().count(), 0)

        self.assertEqual(UserProfile.objects.get(id=account_id), user_profile)

    def test_user_profile_service_correctly_updates_user_one_address(self):
        user_profile = self.service_class.register_user(data=self.user_profile_data)
        user_profile = self.service_class.update_user(
            instance=user_profile, data=self.modified_user_profile_data_one_address
        )
        account_id = user_profile.id

        self.assertEqual(UserProfile.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserAddress.objects.all().count(), 1)

        self.assertEqual(UserProfile.objects.get(id=account_id), user_profile)
        self.assertEqual(
            UserAddress.objects.get(id=1), user_profile.address.all().get(id=1)
        )

    def test_user_profile_service_correctly_updates_user_multiple_addresses(self):
        user_profile = self.service_class.register_user(data=self.user_profile_data)

        updated_user_profile = self.service_class.update_user(
            instance=user_profile, data=self.modified_user_profile_data_two_addresses
        )
        account_id = updated_user_profile.id

        self.assertEqual(UserProfile.objects.all().count(), 1)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(UserAddress.objects.all().count(), 2)

        self.assertEqual(UserProfile.objects.get(id=account_id), updated_user_profile)
        self.assertEqual(
            UserAddress.objects.get(id=1), updated_user_profile.address.all().get(id=1)
        )

    def test_user_profile_service_does_not_create_duplicate_addresses(self):
        address_data = self.modified_user_profile_data_one_address["address"][0]
        UserAddress.objects.create(**address_data)

        user_profile = self.service_class.register_user(data=self.user_profile_data)
        user_profile = self.service_class.update_user(
            instance=user_profile, data=self.modified_user_profile_data_one_address
        )
        self.assertEqual(UserAddress.objects.all().count(), 1)
        self.assertEqual(UserAddress.objects.get(id=1), user_profile.address.get())
