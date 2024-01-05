from typing import Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.serializers import ValidationError

from src.apps.accounts.models import UserAddress
from src.apps.orders.models import (
    Order,
    OrderItem,
    Cart,
    CartItem,
    Coupon,
)
from src.apps.payments.models import PaymentDetails
from src.apps.products.models import Product
from src.apps.orders.validators import (
    validate_item_quantity,
    validate_coupon_total,
    validate_coupon,
)

User = get_user_model()


class CouponService:
    """
    Service for creating and updating coupons.
    """

    @classmethod
    @transaction.atomic
    def create_coupon(cls, data: dict[str, Any]) -> Coupon:
        min_total = data["min_order_total"]
        amount = data["amount"]
        validate_coupon(amount=amount, min_total=min_total)

        coupon = Coupon.objects.create(**data)
        return coupon

    @classmethod
    @transaction.atomic
    def update_coupon(cls, instance: Coupon, data: dict[str, Any]) -> Coupon:
        min_total = data["min_order_total"]
        amount = data["amount"]
        validate_coupon(amount=amount, min_total=min_total)

        fields = [
            "code",
            "amount",
            "is_active",
            "min_order_total",
        ]
        for field in fields:
            try:
                setattr(instance, field, data[field])
            except KeyError as err:
                raise err("Missing or invalid data.")
        instance.save()
        return instance


class CartService:
    """
    Service for managing carts. Creating and updating cart items checks quantity
    available in product's inventory and in case of deficiency, raises ValidationError.
    When updating, if the quantity is equal to 0, it removes the item from the cart.
    """

    @classmethod
    @transaction.atomic
    def create_cart_item(cls, cart_id: int, data: dict[str, Any]) -> CartItem:
        product_id = data.pop("product_id")
        quantity = data.pop("quantity")

        product = get_object_or_404(Product, id=product_id)
        max_quantity = product.inventory.quantity
        validate_item_quantity(quantity, max_quantity)

        try:
            cartitem = CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cartitem.quantity += quantity
            cartitem.save()
        except CartItem.DoesNotExist:
            product = get_object_or_404(Product, id=product_id)
            cart = get_object_or_404(Cart, id=cart_id)
            cartitem = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
            )
            cartitem.save()
        return cartitem

    @classmethod
    def _check_quantity(cls, instance: CartItem, quantity: int):
        if quantity == 0:
            instance.delete()
            return False
        return True

    @classmethod
    @transaction.atomic
    def update_cart_item(cls, instance: CartItem, data: dict[str, Any]):
        quantity = data["quantity"]
        max_quantity = instance.product.inventory.quantity
        validate_item_quantity(quantity, max_quantity)
        if cls._check_quantity(instance=instance, quantity=quantity):
            try:
                setattr(instance, "quantity", quantity)
            except KeyError as err:
                raise err("Missing or invalid data.")
            instance.save()
            return instance
        return


class OrderService:
    """
    Service for managing orders. Creates an Order instance based on cart.
    With a successful operation, it lowers the available quantity of each Product
    and deletes the cart used to create an order.

    Optional coupons are checked if they exist, are active and
    the minimal total requirement is fulfilled. After an order is created,
    email is sent out to the buyer.

    After a payment is confirmed by Stripe, StripeWebhookView calls .fullfill_order()
    method which updates quantity sold of each item and change .payment_accepted
    attribute of an order to `True`. It also sends out an email to the buyer with
    payment confirmation message and creates PaymentDetails object.
    """

    @classmethod
    def _create_order_items(cls, instance: Order, cart_items):
        if not cart_items:
            raise ValidationError({"Missing items": "The cart is empty"})
        for cartitem in cart_items:
            product = cartitem.product
            quantity = cartitem.quantity
            max_quantity = product.inventory.quantity

            validate_item_quantity(quantity=quantity, max_quantity=max_quantity)

            OrderItem.objects.create(order=instance, product=product, quantity=quantity)
            product_inventory = product.inventory
            product_inventory.quantity = product_inventory.quantity - quantity
            product_inventory.save()
        return

    @classmethod
    def _send_email_before_payment(cls, order_id: int, email: str):
        send_mail(
            "Order #{}".format(order_id),
            """
            Thank you for purchasing in our store.
            We received your order, awaiting payment.
            THIS IS NOT SHIPPING CONFIRMATION EMAIL.
            """,
            "ecommapi@ecommapi.com",
            ["{}".format(email)],
            fail_silently=False,
        )

    @classmethod
    @transaction.atomic
    def create_order(cls, cart_id: int, user: User, data: dict[str, Any]) -> Order:
        
        print(get_object_or_404(
            UserAddress, id=data["address_id"], userprofile__user=user
        ), "wow1")
        address = get_object_or_404(
            UserAddress, id=data["address_id"], userprofile__user=user
        )
        print(get_object_or_404(Cart, id=cart_id, user=user), "wow2")
        cart = get_object_or_404(Cart, id=cart_id, user=user)
        cart_items = cart.cart_items.select_related(
            "product", "product__inventory"
        ).all()

        order = Order.objects.create(user=user, address=address)

        cls._create_order_items(instance=order, cart_items=cart_items)

        if "coupon_code" in data.keys():
            coupon = get_object_or_404(Coupon, code=data["coupon_code"], is_active=True)
            validate_coupon_total(
                total=order.before_coupon, min_total=coupon.min_order_total
            )
            order.coupon = coupon
            order.save()
        cart.delete()
        cls._send_email_before_payment(order_id=order.id, email=order.user.email)
        return order

    @classmethod
    @transaction.atomic
    def update_order(cls, instance: Order, user: User, data: dict[str, Any]) -> Order:
        if "coupon_code" in data.keys():
            coupon = get_object_or_404(Coupon, code=data["coupon_code"], is_active=True)
            validate_coupon_total(
                total=instance.before_coupon, min_total=coupon.min_order_total
            )
            instance.coupon = coupon
            instance.save()

        instance.address = get_object_or_404(
            UserAddress, id=data["address_id"], userprofile__user=user
        )
        instance.save()
        return instance

    @classmethod
    @transaction.atomic
    def destroy_order(cls, instance: Order):
        orderitems = instance.order_items.select_related(
            "product", "product__inventory"
        ).all()
        for orderitem in orderitems:
            product_inventory = orderitem.product.inventory
            product_inventory.quantity += orderitem.quantity
            product_inventory.save()
        instance.delete()
        return

    @classmethod
    def _update_product_inventory(cls, order_instance: Order):
        order_items = order_instance.order_items.select_related(
            "product", "product__inventory"
        ).all()
        for orderitem in order_items:
            product_inventory = orderitem.product.inventory
            product_inventory.sold += orderitem.quantity
            product_inventory.save()
        return

    @classmethod
    def _send_email_after_payment(cls, order_id: int, email: str):
        send_mail(
            "Order #{} payment confirmation".format(order_id),
            """
            Thank you for purchasing in our store.
            We received your payment. Your products will be sent soon
            """,
            "ecommapi@ecommapi.com",
            ["{}".format(email)],
            fail_silently=False,
        )

    @classmethod
    @transaction.atomic
    def fullfill_order(cls, session, payment_intent):
        stripe_charge_id = payment_intent["charges"]["data"][0]["id"]
        amount = payment_intent["amount"] / 100
        order_id = session["metadata"]["order_id"]
        order = get_object_or_404(Order, id=order_id)
        order.order_accepted = True
        order.payment_accepted = True
        order.save()
        payment_details = PaymentDetails.objects.create(
            user=order.user, stripe_charge_id=stripe_charge_id, amount=amount
        )
        order.payment = payment_details
        order.save()

        cls._update_product_inventory(order)
        cls._send_email_after_payment(order_id=order_id, email=order.user.email)
        return
