from django.contrib.auth import get_user_model
from django.test import TestCase

from src.apps.products.models import (
    Product,
    ProductInventory,
    ProductCategory,
    ProductReview,
)
from src.apps.products.services import ProductService, ReviewService

User = get_user_model()


class TestProductService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = ProductService
        cls.product_data = {
            "name": "Test product",
            "price": 10.00,
            "discount": {
                "percentage": 10,
            },
            "weight": 10.00,
            "inventory": {
                "quantity": 100,
            },
            "category": {
                "name": "Test",
            },
            "short_description": "Test long description",
            "long_description": "Test long description",
        }
        cls.modified_product_data = {
            "name": "Test product",
            "price": 100.00,
            "discount": {
                "percentage": 20,
            },
            "weight": 5.00,
            "inventory": {
                "quantity": 50,
            },
            "category": {
                "name": "New",
            },
            "short_description": "Test long description",
            "long_description": "Test long description",
        }

    def test_product_service_correctly_creates_product(self):
        product = self.service_class.create_product(data=self.product_data)
        product_id = product.id

        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(ProductCategory.objects.all().count(), 1)
        self.assertEqual(ProductInventory.objects.all().count(), 1)

        self.assertEqual(Product.objects.get(id=product_id), product)
        self.assertTrue(product.is_discounted)
        self.assertNotEqual(product.price, product.discount_price)

    def test_product_service_does_not_create_duplicate_category(self):
        test_category = ProductCategory.objects.create(name="Test")
        product = self.service_class.create_product(data=self.product_data)
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(ProductCategory.objects.all().count(), 1)
        self.assertEqual(product.category.name, test_category.name)

    def test_product_service_correctly_updates_product(self):
        inventory_data = self.modified_product_data["inventory"]
        product = self.service_class.create_product(data=self.product_data)
        updated_product = self.service_class.update_product(
            instance=product, data=self.modified_product_data
        )
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(ProductCategory.objects.all().count(), 2)
        self.assertEqual(ProductInventory.objects.all().count(), 1)

        self.assertEqual(Product.objects.get(id=product.id), updated_product)
        self.assertEqual(
            Product.objects.get(id=updated_product.id).inventory.quantity,
            inventory_data["quantity"],
        )

    def test_product_service_does_not_create_duplicate_category_with_update(self):
        test_category = ProductCategory.objects.create(name="New")
        product = self.service_class.create_product(data=self.product_data)
        updated_product = self.service_class.update_product(
            instance=product, data=self.modified_product_data
        )
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(ProductCategory.objects.all().count(), 2)
        self.assertEqual(updated_product.category.name, test_category.name)
        self.assertNotEqual(updated_product.price, updated_product.discount_price)


class TestReviewService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.service_class = ReviewService

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

        cls.product_review_data = {
            "product_id": cls.product.id,
            "description": "Test review description",
            "rating": 4.5,
        }
        cls.modified_product_review_data = {
            "description": "Updated test review description",
            "rating": 4.03,
        }

    def test_review_service_correctly_creates_review(self):
        review = self.service_class.create_review(
            user=self.user, data=self.product_review_data
        )

        self.assertEqual(ProductReview.objects.all().count(), 1)
        self.assertEqual(ProductReview.objects.get(id=review.id), review)
        self.assertEqual(ProductReview.objects.get(id=review.id).product, self.product)

        self.assertEqual(self.product.review_count, 1)
        self.assertEqual(self.product.avg_rating, review.rating)

    def test_review_service_correctly_updates_review(self):
        review = self.service_class.create_review(
            user=self.user, data=self.product_review_data
        )
        updated_review = self.service_class.update_review(
            instance=review, data=self.modified_product_review_data
        )

        self.assertEqual(ProductReview.objects.all().count(), 1)
        self.assertEqual(ProductReview.objects.get(id=updated_review.id), review)

        self.assertEqual(self.product.review_count, 1)
        self.assertEqual(self.product.avg_rating, review.rating)
