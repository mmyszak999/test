from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from src.apps.products.models import (
    ProductCategory,
    ProductInventory,
    Product,
    ProductReview,
)


class ProductCategoryInputSerializer(serializers.Serializer):
    name = serializers.CharField()


class ProductCategoryOutputSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ProductCategory
        fields = ("id", "name", "created", "updated")
        read_only_fields = fields


class ProductCategoryOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
        )
        read_only_fields = fields


class ProductInventoryInputSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(initial=0, allow_null=True)


class DiscountInputSerializer(serializers.Serializer):
    percentage = serializers.FloatField(
        default=0.0, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )


class ProductInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.FloatField(default=0, allow_null=True)
    weight = serializers.FloatField(default=0, allow_null=True, required=False)
    short_description = serializers.CharField(required=False)
    long_description = serializers.CharField(required=False)
    discount = DiscountInputSerializer(default=0.0, required=False)
    category = ProductCategoryInputSerializer(many=False)
    inventory = ProductInventoryInputSerializer(many=False, required=True)


class ProductInventoryOutputSerializer(serializers.ModelSerializer):
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ProductInventory
        fields = ("quantity", "sold", "updated")
        read_only_fields = fields


class ProductListOutputSerializer(serializers.ModelSerializer):
    inventory = ProductInventoryOutputSerializer(many=False, read_only=True)
    category = ProductCategoryOutputSerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "discount_price",
            "dollar_price",
            "dollar_discount_price",
            "avg_rating",
            "review_count",
            "inventory",
            "category",
        )
        read_only_fields = fields


class ProductDetailOutputSerializer(serializers.ModelSerializer):
    inventory = ProductInventoryOutputSerializer(many=False, read_only=True)
    category = ProductCategoryOutputSerializer(many=False, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "short_description",
            "long_description",
            "price",
            "discount_price",
            "dollar_price",
            "dollar_discount_price",
            "avg_rating",
            "review_count",
            "weight",
            "inventory",
            "category",
            "created",
            "updated",
        )
        read_only_fields = fields


class ProductReviewInputSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    description = serializers.CharField()
    rating = serializers.FloatField(
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )


class ProductReviewUpdateInputSerializer(serializers.Serializer):
    description = serializers.CharField()
    rating = serializers.FloatField(
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )


class ProductReviewOutputSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    product_id = serializers.CharField(source="product.id", read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ProductReview
        fields = (
            "id",
            "username",
            "product_id",
            "description",
            "rating",
            "created",
            "updated",
        )
        read_only_fields = fields
