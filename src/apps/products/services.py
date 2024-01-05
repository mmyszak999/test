from typing import Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from src.apps.products.models import (
    ProductCategory,
    ProductInventory,
    Product,
    ProductReview,
)


User = get_user_model()


class ProductService:
    """
    Service for managing creating and updating product instances.
    """

    @classmethod
    @transaction.atomic
    def create_product(cls, data: dict[str, Any]) -> Product:
        inventory_data = data.pop("inventory")
        category_data = data.pop("category")
        discount_data = data.pop("discount")

        inventory = ProductInventory.objects.create(**inventory_data)
        category, created = ProductCategory.objects.get_or_create(**category_data)

        product = Product.objects.create(inventory=inventory, category=category, **data)
        if discount_data:
            if percentage := discount_data.get("percentage", None):
                product.set_discount(percentage)
        return product

    @classmethod
    @transaction.atomic
    def update_product(cls, instance: Product, data: dict[str, Any]) -> Product:
        inventory_data = data.pop("inventory")
        category_data = data.pop("category")
        discount_data = data.pop("discount")

        inventory = instance.inventory
        inventory.quantity = inventory_data.get("quantity", inventory.quantity)
        inventory.save()

        fields = ["name", "price", "weight", "short_description", "long_description"]
        for field in fields:
            try:
                setattr(instance, field, data[field])
            except KeyError as err:
                raise err(f"{err} : Missing or wrong data")
        instance.category, created = ProductCategory.objects.get_or_create(
            **category_data
        )
        instance.save()
        if discount_data:
            if percentage := discount_data.get("percentage", None):
                instance.set_discount(percentage)
        else:
            instance.set_discount(0)

        return instance


class ReviewService:
    """
    Service for managing product reviews.
    """

    @classmethod
    @transaction.atomic
    def create_review(cls, user: User, data: dict[str, Any]) -> ProductReview:
        product_id = data.pop("product_id")
        product = get_object_or_404(Product, id=product_id)
        review = ProductReview.objects.create(user=user, product=product, **data)
        return review

    @classmethod
    @transaction.atomic
    def update_review(
        cls, instance: ProductReview, data: dict[str, Any]
    ) -> ProductReview:
        instance.description = data["description"]
        instance.rating = data["rating"]
        instance.save()
        return instance
