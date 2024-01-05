from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from src.apps.products.models import Product, ProductInventory, ProductCategory
from src.apps.orders.models import Coupon, Cart, CartItem, Coupon, Order, OrderItem

User = get_user_model()


class TestCouponViews(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")
        cls.staff = User.objects.create(username="staff", is_staff=True)
        cls.coupon = Coupon.objects.create(
            code="testcode10", amount=10, min_order_total=20, is_active=True
        )

        cls.coupon_list_url = reverse("orders:coupon-list")
        cls.coupon_detail_url = reverse(
            "orders:coupon-detail", kwargs={"pk": cls.coupon.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_retrieves_empty_coupon_queryset(self):
        response = self.client.get(self.coupon_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_user_cannot_retrieve_coupon_by_id(self):
        response = self.client.get(self.coupon_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_coupon(self):
        response = self.client.delete(self.coupon_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_retrieve_coupon(self):
        self.client.logout()
        response = self.client.get(self.coupon_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_retrieve_coupon_by_id(self):
        self.client.logout()
        response = self.client.get(self.coupon_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_delete_coupon_by_id(self):
        self.client.logout()
        response = self.client.delete(self.coupon_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Coupon.objects.exists())

    def test_staff_can_retrieve_coupon(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.coupon_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_user_can_retrieve_coupon_by_id(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.coupon_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_delete_product_category(self):
        self.client.force_login(user=self.staff)
        response = self.client.delete(self.coupon_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Coupon.objects.exists())


class TestCartViews(APITestCase):
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
        cls.cart = Cart.objects.create(user=cls.user)
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart, product=cls.product, quantity=10
        )

        cls.cart_list_url = reverse("orders:cart-list")
        cls.cart_detail_url = reverse("orders:cart-detail", kwargs={"pk": cls.cart.id})

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_cart(self):
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(uuid.UUID(response.data["results"][0]["id"]), self.cart.id)

    def test_user_can_retrieve_cart_by_id(self):
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_cart(self):
        response = self.client.delete(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.exists())

    def test_other_user_cannot_retrieve_other_users_cart(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 0)

    def test_other_user_cannot_retrieve_other_users_cart_by_id(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_other_users_cart(self):
        self.client.force_login(user=self.other_user)
        response = self.client.delete(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Cart.objects.exists())

    def test_anonymous_user_cannot_retrieve_cart(self):
        self.client.logout()
        response = self.client.get(self.cart_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_retrieve_other_cart_by_id(self):
        self.client.logout()
        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_delete_cart(self):
        self.client.logout()
        response = self.client.delete(self.cart_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Cart.objects.exists())


class TestCartItemViews(APITestCase):
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
        cls.cart = Cart.objects.create(user=cls.user)
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart, product=cls.product, quantity=10
        )

        cls.cart_item_list_url = reverse(
            "orders:cart-item-list", kwargs={"pk": cls.cart.id}
        )
        cls.cart_item_detail_url = reverse(
            "orders:cart-item-detail",
            kwargs={"pk": cls.cart.id, "cart_item_pk": cls.cart_item.id},
        )

        cls.other_cart = Cart.objects.create(user=cls.other_user)
        cls.other_cart_item = CartItem.objects.create(
            cart=cls.other_cart, product=cls.product, quantity=10
        )

        cls.wrong_cart_correct_cart_item_detail_url = reverse(
            "orders:cart-item-detail",
            kwargs={"pk": cls.other_cart.id, "cart_item_pk": cls.cart_item.id},
        )
        cls.correct_cart_wrong_cart_item_detail_url = reverse(
            "orders:cart-item-detail",
            kwargs={"pk": cls.cart.id, "cart_item_pk": cls.other_cart_item.id},
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_cart_items(self):
        response = self.client.get(self.cart_item_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            uuid.UUID(response.data["results"][0]["id"]), self.cart_item.id
        )

    def test_user_can_retrieve_cart_item_by_id(self):
        response = self.client.get(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_cart_item(self):
        response = self.client.delete(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())

    def test_user_cannot_retrieve_cart_item_with_wrong_cart_id(self):
        response = self.client.get(self.wrong_cart_correct_cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_retrieve_cart_item_belonging_to_other_users_cart(self):
        response = self.client.get(self.correct_cart_wrong_cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_retrieve_other_users_cart_item(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.cart_item_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 0)

    def test_other_user_cannot_retrieve_other_users_cart_item_by_id(self):
        self.client.force_login(user=self.other_user)
        response = self.client.get(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_other_users_cart_item(self):
        self.client.force_login(user=self.other_user)
        response = self.client.delete(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(CartItem.objects.filter(cart__user=self.user).exists())

    def test_anonymous_user_cannot_retrieve_cart_item(self):
        self.client.logout()
        response = self.client.get(self.cart_item_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_retrieve_cart_item_by_id(self):
        self.client.logout()
        response = self.client.get(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_delete_cart_item(self):
        self.client.logout()
        response = self.client.delete(self.cart_item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(CartItem.objects.filter(cart__user=self.user).exists())


class TestOrderViews(APITestCase):
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
        cls.cart = Cart.objects.create(user=cls.user)
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart, product=cls.product, quantity=10
        )
        cls.order = Order.objects.create(user=cls.user)
        cls.order_item = OrderItem.objects.create(
            order=cls.order, product=cls.product, quantity=10
        )

        cls.order_list_url = reverse("orders:order-list")
        cls.order_detail_url = reverse(
            "orders:order-detail", kwargs={"pk": cls.order.id}
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_user_can_retrieve_order(self):
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(uuid.UUID(response.data["results"][0]["id"]), self.order.id)

    def test_user_can_retrieve_order_by_id(self):
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_order(self):
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Order.objects.exists())
        self.assertFalse(OrderItem.objects.exists())

    def test_other_user_cannot_retrieve_other_users_order(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 0)

    def test_other_user_cannot_retrieve_other_users_order_by_id(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_other_users_order(self):
        self.client.force_login(self.other_user)
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(Order.objects.exists())
        self.assertTrue(OrderItem.objects.exists())

    def test_anonymous_user_cannot_retrieve_order(self):
        self.client.logout()
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_retrieve_order_by_id(self):
        self.client.logout()
        response = self.client.get(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_delete_order(self):
        self.client.logout()
        response = self.client.delete(self.order_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertTrue(Order.objects.exists())
        self.assertTrue(OrderItem.objects.exists())
