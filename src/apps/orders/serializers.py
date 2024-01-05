from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from src.apps.accounts.models import UserProfile
from src.apps.accounts.serializers import (
    UserAddressOutputSerializer,
    UserOrderOutputSerializer,
)
from src.apps.orders.models import (
    Order,
    Cart,
    CartItem,
    Coupon,
)
from src.apps.payments.serializers import PaymentDetailsOutputSerializer


class CouponInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    amount = serializers.IntegerField(validators=[MinValueValidator(0)])
    is_active = serializers.BooleanField()
    min_order_total = serializers.IntegerField(validators=[MinValueValidator(10)])


class CouponOutputSerializers(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Coupon
        fields = (
            "id",
            "code",
            "amount",
            "min_order_total",
            "is_active",
            "created",
            "updated",
        )
        read_only_fields = fields


class CouponOrderOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            "code",
            "amount",
        )
        read_only_fields = fields


class CartItemInputSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(default=1, validators=[MinValueValidator(1)])


class CartItemQuantityInputSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(default=1, validators=[MinValueValidator(0)])


class CouponOrderInputSerializer(serializers.Serializer):
    code = serializers.CharField()


class CartItemOutputSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "quantity",
            "total_item_price",
            "total_discount_item_price",
            "amount_saved",
            "final_price",
        )
        read_only_fields = fields


class CartOutputSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    cart_items = CartItemOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "username",
            "cart_items",
            "total",
        )
        read_only_fields = fields


class OrderInputSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required=False)
    address_id = serializers.CharField()


class OrderItemOutputSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "quantity",
            "total_item_price",
            "total_discount_item_price",
            "amount_saved",
            "final_price",
        )
        read_only_fields = fields


class OrderOutputSerializer(serializers.ModelSerializer):
    userprofile = UserOrderOutputSerializer(
        source="user.userprofile", many=False, read_only=True
    )
    coupon = CouponOrderOutputSerializer(many=False, read_only=True)
    address = UserAddressOutputSerializer(many=False, read_only=True)
    order_items = OrderItemOutputSerializer(many=True, read_only=True)
    payment = PaymentDetailsOutputSerializer(many=False, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "userprofile",
            "address",
            "coupon",
            "before_coupon",
            "total",
            "address",
            "payment_accepted",
            "order_accepted",
            "being_delivered",
            "received",
            "order_items",
            "payment",
            "created",
            "updated",
        )
        read_only_fields = fields
