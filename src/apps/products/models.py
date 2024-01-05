from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ProductCategory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class ProductInventory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    quantity = models.IntegerField()
    sold = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self) -> str:
        return f"Available stock : {self.quantity} | {self.product.name}"


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )

    weight = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)

    short_description = models.CharField(max_length=1000, blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    inventory = models.OneToOneField(
        ProductInventory, on_delete=models.CASCADE, related_name="product"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return self.name

    def set_discount(self, percentage: float):
        self.discount_price = round((self.price * (1 - percentage / 100)), 2)
        self.save()

    def remove_discount(self):
        self.discount_price = None
        self.save()

    @property
    def is_discounted(self) -> bool:
        return bool(self.discount_price)

    @property
    def dollar_price(self):
        return "$%s" % self.price

    @property
    def dollar_discount_price(self):
        return "$%s" % self.discount_price if self.discount_price else ""

    @property
    def avg_rating(self):
        return self.reviews.aggregate(models.Avg("rating")).get("rating__avg")

    @property
    def review_count(self):
        return self.reviews.count()

    def get_absolute_url(self) -> str:
        return f"/api/products/{self.pk}/"

    @property
    def endpoint(self) -> str:
        return self.get_absolute_url()


class ProductReview(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    description = models.TextField()
    rating = models.FloatField(default=0.0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Review of {self.product.name} | Author: {self.user.username}"

    def get_absolute_url(self):
        return f"/api/products/reviews/{self.pk}/"

    @property
    def endpoint(self):
        return self.get_absolute_url()
