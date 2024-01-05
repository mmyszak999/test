from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.accounts.models import UserProfile, UserAddress

User = get_user_model()


class TestUserProfileViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.other_user = User.objects.create(username="otheruser")

        cls.address = UserAddress.objects.create(
            address_1="Test 6/15",
            address_2="Testowa 3/4",
            country="PL",
            city="Warszawa",
            postalcode="00-001",
        )

        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            phone_number="692267652",
            birthday="1999-01-01",
        )

        cls.other_user_profile = UserProfile.objects.create(
            user=cls.other_user,
            phone_number="+48692267654",
            birthday="1999-01-01",
        )
        cls.user_profile.address.add(cls.address)

        cls.user_profile_list_url = reverse("accounts:user-profile-list")
        cls.user_profile_detail_url = reverse(
            "accounts:user-profile-detail",
            kwargs={"pk": cls.user_profile.id},
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_profile(self):
        response = self.client.get(self.user_profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        user_profile_data = response.data["results"][0]
        self.assertEqual(
            user_profile_data["phone_number"], self.user_profile.phone_number
        )
        self.assertEqual(user_profile_data["birthday"], self.user_profile.birthday)

    def test_user_can_retrieve_profile_by_uuid(self):
        response = self.client.get(self.user_profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_retrieve_other_users_profile(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.user_profile_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_retrieve_profile(self):
        self.client.logout()
        response = self.client.get(self.user_profile_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
