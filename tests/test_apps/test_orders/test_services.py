from django.http.response import Http404
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core import mail
from rest_framework.exceptions import ValidationError

from src.apps.accounts.models import UserAddress, UserProfile
from src.apps.payments.models import PaymentDetails
from src.apps.products.models import Product, ProductInventory, ProductCategory
from src.apps.orders.models import Coupon, Order, OrderItem, Cart, CartItem
from src.apps.orders.services import CouponService, CartService, OrderService

User = get_user_model()


class TestCouponService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = CouponService
        cls.coupon_data = {
            "code": "test10",
            "amount": 10,
            "is_active": True,
            "min_order_total": 20,
        }
        cls.modified_coupon_data = {
            "code": "updatedtest10",
            "amount": 20,
            "is_active": False,
            "min_order_total": 40,
        }
        cls.incorrect_coupon_data = {
            "code": "wrongtest10",
            "amount": 20,
            "is_active": True,
            "min_order_total": 10,
        }

    def test_coupon_service_correctly_creates_coupo(self):
        coupon = self.service_class.create_coupon(data=self.coupon_data)

        self.assertEqual(Coupon.objects.all().count(), 1)
        self.assertEqual(Coupon.objects.get(id=coupon.id), coupon)

    def test_coupon_service_correctly_updates_coupon(self):
        coupon = self.service_class.create_coupon(data=self.coupon_data)
        updated_coupon = self.service_class.update_coupon(
            instance=coupon, data=self.modified_coupon_data
        )
        self.assertEqual(Coupon.objects.all().count(), 1)
        self.assertEqual(Coupon.objects.get(id=coupon.id), updated_coupon)

    def test_coupon_service_raises_validation_error_on_incorrect_min_total(self):
        with self.assertRaises(ValidationError):
            self.service_class.create_coupon(data=self.incorrect_coupon_data)

        self.assertEqual(Coupon.objects.all().count(), 0)

    def test_coupon_service_raises_validation_error_on_incorrect_min_total_update(self):
        coupon = self.service_class.create_coupon(data=self.coupon_data)
        with self.assertRaises(ValidationError):
            self.service_class.update_coupon(
                instance=coupon, data=self.incorrect_coupon_data
            )

        self.assertEqual(Coupon.objects.all().count(), 1)
        self.assertEqual(
            Coupon.objects.get(id=coupon.id).amount, self.coupon_data["amount"]
        )
        self.assertEqual(
            Coupon.objects.get(id=coupon.id).min_order_total,
            self.coupon_data["min_order_total"],
        )


class TestCartService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = CartService

        cls.user = User.objects.create(username="testuser")
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

        cls.cart_item_data = {
            "product_id": cls.product.id,
            "quantity": 10,
        }
        cls.modified_cart_item_data = {
            "quantity": 5,
        }

    def test_cart_service_correctly_creates_cart_item(self):
        cart_item = self.service_class.create_cart_item(
            cart_id=self.cart.id, data=self.cart_item_data
        )

        self.assertEqual(CartItem.objects.all().count(), 1)
        self.assertEqual(CartItem.objects.get(id=cart_item.id).cart, self.cart)

    def test_cart_service_raises_validation_error_when_stock_is_small(self):
        self.cart_item_data["quantity"] = self.product_inventory.quantity + 1
        with self.assertRaises(ValidationError):
            cart_item = self.service_class.create_cart_item(
                cart_id=self.cart.id, data=self.cart_item_data
            )
        self.assertEqual(CartItem.objects.all().count(), 0)

    def test_cart_service_updates_quantity_instead_of_duplicating_cart_item(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        cart_item = self.service_class.create_cart_item(
            cart_id=self.cart.id, data=self.cart_item_data
        )

        self.assertEqual(CartItem.objects.all().count(), 1)
        self.assertEqual(CartItem.objects.get(id=cart_item.id), cart_item)
        self.assertEqual(CartItem.objects.get(id=cart_item.id).quantity, 11)

    def test_cart_service_correctly_updates_cart_item(self):
        quantity = self.modified_cart_item_data["quantity"]
        cart_item = self.service_class.create_cart_item(
            cart_id=self.cart.id, data=self.cart_item_data
        )
        updated_cart_item = self.service_class.update_cart_item(
            instance=cart_item, data=self.modified_cart_item_data
        )
        self.assertIs(cart_item, updated_cart_item)
        self.assertEqual(CartItem.objects.all().count(), 1)
        self.assertEqual(
            CartItem.objects.get(id=updated_cart_item.id).quantity, quantity
        )

    def test_cart_service_deletes_cart_item_on_update_with_quantity_zero(self):
        self.modified_cart_item_data["quantity"] = 0
        cart_item = self.service_class.create_cart_item(
            cart_id=self.cart.id, data=self.cart_item_data
        )
        self.service_class.update_cart_item(
            instance=cart_item, data=self.modified_cart_item_data
        )
        self.assertEqual(CartItem.objects.all().count(), 0)

    def test_cart_service_raises_validation_error_when_stock_is_small_on_update(self):
        quantity = self.cart_item_data["quantity"]
        self.modified_cart_item_data["quantity"] = self.product_inventory.quantity + 1
        cart_item = self.service_class.create_cart_item(
            cart_id=self.cart.id, data=self.cart_item_data
        )
        with self.assertRaises(ValidationError):
            cart_item = self.service_class.update_cart_item(
                instance=cart_item, data=self.modified_cart_item_data
            )
        self.assertEqual(CartItem.objects.all().count(), 1)
        self.assertEqual(cart_item.quantity, quantity)


class TestOrderService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = OrderService

        cls.user = User.objects.create(username="testuser", email="testuser@gmail.com")
        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            phone_number="692267652",
            birthday="1999-01-01",
        )
        cls.other_user = User.objects.create(
            username="otheruser", email="otheruser@gmail.com"
        )
        cls.other_user_profile = UserProfile.objects.create(
            user=cls.other_user,
            phone_number="692267654",
            birthday="1999-01-01",
        )

        cls.address = UserAddress.objects.create(
            address_1="Test 6/15",
            address_2="Testowa 3/4",
            country="PL",
            city="Warszawa",
            postalcode="00-001",
        )
        cls.other_address = UserAddress.objects.create(
            address_1="Test 1/1",
            address_2="Testowa 2/2",
            country="PL",
            city="Poznan",
            postalcode="11-111",
        )
        cls.user_profile.address.add(cls.address)

        cls.coupon = Coupon.objects.create(
            code="test10",
            amount=10,
            min_order_total=20,
            is_active=True,
        )
        cls.inactive_coupon = Coupon.objects.create(
            code="inactive10",
            amount=10,
            min_order_total=20,
            is_active=False,
        )
        cls.higher_total_coupon = Coupon.objects.create(
            code="bigtotal20",
            amount=20,
            min_order_total=40,
            is_active=True,
        )

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
        cls.order_data_no_coupon = {
            "address_id": cls.address.id,
        }
        cls.order_data_no_coupon_wrong_address = {
            "address_id": cls.other_address.id,
        }
        cls.order_data_coupon = {
            "address_id": cls.address.id,
            "coupon_code": "test10",
        }
        cls.order_data_inactive_coupon = {
            "address_id": cls.address.id,
            "coupon_code": "inactive10",
        }
        cls.order_data_big_total_coupon = {
            "address_id": cls.address.id,
            "coupon_code": "bigtotal20",
        }

        cls.stripe_session = {
            "id": "cs_test_id",
            "object": "checkout.session",
            "metadata": {"order_id": "###"},
            "mode": "payment",
            "payment_method_types": ["card"],
            "payment_status": "paid",
        }
        cls.payment_intent = {
            "id": "pi_test_id",
            "object": "payment_intent",
            "amount": 1000,
            "charges": {
                "object": "list",
                "data": [
                    {
                        "id": "ch_test_intent",
                        "object": "charge",
                        "amount": 1000,
                    }
                ],
            },
        }

    def test_order_service_correctly_creates_order_with_no_coupon(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )

        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Order.objects.get(id=order.id), order)
        self.assertEqual(Cart.objects.all().count(), 0)
        self.assertEqual(CartItem.objects.all().count(), 0)

    def test_order_service_correctly_creates_order_with_coupon(self):
        data = self.order_data_coupon
        order = self.service_class.create_order(self.cart.id, user=self.user, data=data)

        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Order.objects.get(id=order.id), order)
        self.assertEqual(Coupon.objects.get(code=data["coupon_code"]), order.coupon)
        self.assertEqual(order.total, order.before_coupon - order.coupon.amount)

    def test_order_service_disallows_inactive_coupon(self):
        with self.assertRaises(Http404):
            order = self.service_class.create_order(
                self.cart.id, user=self.user, data=self.order_data_inactive_coupon
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_raises_valdiation_error_with_total_smaller_than_coupon_total(
        self,
    ):
        with self.assertRaises(ValidationError):
            order = self.service_class.create_order(
                self.cart.id, user=self.user, data=self.order_data_big_total_coupon
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_sends_email_after_creating_order(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Order #{}".format(order.id))
        self.assertEqual(
            mail.outbox[0].body,
            """
            Thank you for purchasing in our store.
            We received your order, awaiting payment.
            THIS IS NOT SHIPPING CONFIRMATION EMAIL.
            """,
        )
        self.assertEqual(mail.outbox[0].from_email, "ecommapi@ecommapi.com")
        self.assertEqual(mail.outbox[0].to, ["{}".format(order.user.email)])

    def test_order_service_disallows_wrong_user_creation_of_orders(self):
        with self.assertRaises(Http404):
            order = self.service_class.create_order(
                self.cart.id, user=self.other_user, data=self.order_data_no_coupon
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_disallows_using_not_related_address(self):
        with self.assertRaises(Http404):
            order = self.service_class.create_order(
                self.cart.id,
                user=self.user,
                data=self.order_data_no_coupon_wrong_address,
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_correctly_updates_order(self):
        data = self.order_data_no_coupon
        update_data = self.order_data_coupon

        order = self.service_class.create_order(self.cart.id, user=self.user, data=data)
        updated_order = self.service_class.update_order(
            instance=order, user=self.user, data=update_data
        )

        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(
            Coupon.objects.get(code=update_data["coupon_code"]), updated_order.coupon
        )

    def test_order_service_disallows_wrong_user_creation_of_orders_on_update(self):
        data = self.order_data_no_coupon
        update_data = self.order_data_coupon
        order = self.service_class.create_order(self.cart.id, user=self.user, data=data)

        with self.assertRaises(Http404):
            order = self.service_class.update(
                instance=order, user=self.other_user, data=update_data
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_disallows_wrong_user_creation_of_orders_on_update(self):
        data = self.order_data_no_coupon
        update_data = self.order_data_no_coupon_wrong_address
        order = self.service_class.create_order(self.cart.id, user=self.user, data=data)

        with self.assertRaises(Http404):
            updated_order = self.service_class.update_order(
                instance=order, user=self.user, data=update_data
            )
        self.assertEqual(Order.objects.all().count(), 1)

    def test_order_service_raises_validation_error_with_empty_cart(self):
        self.cart_item.delete()
        with self.assertRaises(ValidationError):
            order = self.service_class.create_order(
                self.cart.id, user=self.user, data=self.order_data_no_coupon
            )
        self.assertEqual(Order.objects.all().count(), 0)

    def test_order_service_correctly_updates_inventory_of_products(self):
        product_inventory_quantity = self.product.inventory.quantity
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        order_item = OrderItem.objects.filter(order=order).get()

        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(
            order_item.product.inventory.quantity,
            product_inventory_quantity - order_item.quantity,
        )

    def test_order_service_correctly_updates_product_inventory_on_delete(self):
        product_quantity = int(self.product.inventory.quantity)
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        product_quantity_before_deletion = (
            OrderItem.objects.filter(order=order).get().product.inventory.quantity
        )
        self.service_class.destroy_order(order)
        product_quantity_after_deletion = int(self.product.inventory.quantity)
        self.assertNotEqual(product_quantity, product_quantity_before_deletion)
        self.assertEqual(product_quantity, product_quantity_after_deletion)

    def test_order_service_fullfills_order_after_payment(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        order_id = order.id

        self.stripe_session["metadata"]["order_id"] = order_id
        self.service_class.fullfill_order(
            session=self.stripe_session, payment_intent=self.payment_intent
        )
        order = Order.objects.get(id=order_id)

        self.assertTrue(order.order_accepted)
        self.assertTrue(order.payment_accepted)

    def test_order_service_correctly_updates_inventory_after_payment(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )

        self.stripe_session["metadata"]["order_id"] = order.id
        self.service_class.fullfill_order(
            session=self.stripe_session, payment_intent=self.payment_intent
        )
        order_item = OrderItem.objects.get(order_id=order.id)

        self.assertEqual(order_item.quantity, order_item.product.inventory.sold)

    def test_order_service_sends_email_after_payment(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        self.stripe_session["metadata"]["order_id"] = order.id
        self.service_class.fullfill_order(
            session=self.stripe_session, payment_intent=self.payment_intent
        )

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject, "Order #{} payment confirmation".format(order.id)
        )
        self.assertEqual(
            mail.outbox[1].body,
            """
            Thank you for purchasing in our store.
            We received your payment. Your products will be sent soon
            """,
        )
        self.assertEqual(mail.outbox[1].from_email, "ecommapi@ecommapi.com")
        self.assertEqual(mail.outbox[1].to, ["{}".format(order.user.email)])

    def test_order_service_correctly_creates_payment_details(self):
        order = self.service_class.create_order(
            self.cart.id, user=self.user, data=self.order_data_no_coupon
        )
        self.stripe_session["metadata"]["order_id"] = order.id
        self.service_class.fullfill_order(
            session=self.stripe_session, payment_intent=self.payment_intent
        )
        self.assertEqual(PaymentDetails.objects.all().count(), 1)
        self.assertEqual(
            Order.objects.get(id=order.id).payment, PaymentDetails.objects.get()
        )
        self.assertEqual(
            Order.objects.get(id=order.id).user, PaymentDetails.objects.get().user
        )
