from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.products.models import (
    Product,
    ProductCategory,
    ProductReview,
    ProductInventory,
)

User = get_user_model()


class TestProductCategoryViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.staff = User.objects.create(username="staff", is_staff=True)

        cls.product_category = ProductCategory.objects.create(name="Food")

        cls.product_category_list_url = reverse("products:category-list")
        cls.product_category_detail_url = reverse(
            "products:category-detail", kwargs={"pk": cls.product_category.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_product_category(self):
        response = self.client.get(self.product_category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_category_data = response.data["results"][0]
        self.assertEqual(product_category_data["name"], self.product_category.name)

    def test_user_can_retrieve_product_category_by_id(self):
        response = self.client.get(self.product_category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_delete_product_category(self):
        response = self.client.delete(self.product_category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ProductCategory.objects.exists())

    def test_staff_can_retrieve_product_category(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.product_category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_category_data = response.data["results"][0]
        self.assertEqual(product_category_data["name"], self.product_category.name)

    def test_staff_can_retrieve_product_category_by_id(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.product_category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_delete_product_category(self):
        self.client.force_login(user=self.staff)
        response = self.client.delete(self.product_category_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductCategory.objects.exists())

    def test_anonymous_user_can_retrieve_product_category(self):
        self.client.logout()
        response = self.client.get(self.product_category_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_category_data = response.data["results"][0]
        self.assertEqual(product_category_data["name"], self.product_category.name)

    def test_anonymous_user_can_retrieve_product_category_by_id(self):
        self.client.logout()
        response = self.client.get(self.product_category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_delete_product_category(self):
        self.client.logout()
        response = self.client.delete(self.product_category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(ProductCategory.objects.exists())


class TestProductViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.staff = User.objects.create(username="staff", is_staff=True)

        cls.product_category = ProductCategory.objects.create(name="Food")
        cls.product_inventory = ProductInventory.objects.create(quantity=100, sold=0)
        cls.product = Product.objects.create(
            name="Rice",
            price="2.99",
            discount_price="2.49",
            short_description="Test short description",
            long_description="Test long description",
            weight="1.00",
            category=cls.product_category,
            inventory=cls.product_inventory,
        )

        cls.product_list_url = reverse("products:product-list")
        cls.product_detail_url = reverse(
            "products:product-detail", kwargs={"pk": cls.product.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_product(self):
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_data = response.data["results"][0]
        self.assertEqual(product_data["name"], self.product.name)
        self.assertEqual(product_data["price"], self.product.price)
        self.assertEqual(
            product_data["inventory"]["quantity"], self.product.inventory.quantity
        )

    def test_user_can_retrieve_product_by_id(self):
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_create_product(self):
        response = self.client.post(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_product(self):
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Product.objects.exists())

    def test_anonymous_user_can_retrieve_product(self):
        self.client.logout()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_data = response.data["results"][0]
        self.assertEqual(product_data["name"], self.product.name)
        self.assertEqual(product_data["price"], self.product.price)
        self.assertEqual(
            product_data["inventory"]["quantity"], self.product.inventory.quantity
        )

    def test_anonymous_user_can_retrieve_product_by_id(self):
        self.client.logout()
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_product(self):
        self.client.logout()
        response = self.client.post(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_delete_product(self):
        self.client.logout()
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Product.objects.exists())

    def test_non_staff_user_cannot_retrieve_products_with_quantity_equal_to_zero(self):
        self.product.inventory.quantity = 0
        self.product.inventory.save()

        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_anonymous_user_cannot_retrieve_products_with_quantity_equal_to_zero(self):
        self.product.inventory.quantity = 0
        self.product.inventory.save()

        self.client.logout()
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_staff_can_retrieve_products_with_quantity_0(self):
        self.product.inventory.quantity = 0
        self.product.inventory.save()

        self.client.force_login(user=self.staff)
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_staff_can_delete_product(self):
        self.client.force_login(user=self.staff)
        response = self.client.delete(self.product_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.exists())
        self.assertFalse(ProductInventory.objects.exists())


class TestProductReviewViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.other_user = User.objects.create(username="otheruser")

        cls.product_category = ProductCategory.objects.create(name="Food")
        cls.product_inventory = ProductInventory.objects.create(quantity=100, sold=0)
        cls.product = Product.objects.create(
            name="Rice",
            price="2.99",
            discount_price="2.49",
            short_description="Test short description",
            long_description="Test long description",
            weight="1.00",
            category=cls.product_category,
            inventory=cls.product_inventory,
        )
        cls.product_review = ProductReview.objects.create(
            user=cls.user, product=cls.product, description="Test review", rating=4.50
        )

        cls.product_review_list_url = reverse("products:review-list")
        cls.product_review_detail_url = reverse(
            "products:review-detail", kwargs={"pk": cls.product_review.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_product_review(self):
        response = self.client.get(self.product_review_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_review_data = response.data["results"][0]
        self.assertEqual(
            product_review_data["description"], self.product_review.description
        )

    def test_user_can_retrieve_product_review_by_id(self):
        response = self.client.get(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_own_product_review(self):
        response = self.client.delete(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductReview.objects.exists())

    def test_other_user_can_retrieve_other_users_product_review_by_id(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_delete_other_users_product_review(self):
        self.client.force_login(user=self.other_user)
        response = self.client.delete(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ProductReview.objects.exists())

    def test_anonymous_user_can_retrieve_product_review(self):
        self.client.logout()
        response = self.client.get(self.product_review_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        product_review_data = response.data["results"][0]
        self.assertEqual(
            product_review_data["description"], self.product_review.description
        )

    def test_anonymous_user_can_retrieve_product_review_by_id(self):
        self.client.logout()
        response = self.client.get(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_delete_product_review(self):
        self.client.logout()
        response = self.client.delete(self.product_review_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(ProductReview.objects.exists())
