from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema

from src.apps.products.models import (
    Product,
    ProductCategory,
    ProductReview,
)
from src.apps.products.serializers import (
    ProductCategoryInputSerializer,
    ProductCategoryOutputSerializer,
    ProductInputSerializer,
    ProductListOutputSerializer,
    ProductDetailOutputSerializer,
    ProductReviewInputSerializer,
    ProductReviewOutputSerializer,
    ProductReviewUpdateInputSerializer,
)
from src.apps.products.services import ProductService, ReviewService
from src.apps.products.filters import ProductFilter, ReviewFilter
from src.core.permissions import OwnerOrReadOnly, StaffOrReadOnly


class ProductListCreateAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListOutputSerializer
    permission_classes = [StaffOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ProductFilter
    service_class = ProductService

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.is_staff:
            return qs
        return qs.filter(inventory__quantity__gt=0)

    @swagger_auto_schema(request_body=ProductInputSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.service_class.create_product(data=serializer.validated_data)
        return Response(
            self.get_serializer(product).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailOutputSerializer
    permission_classes = [StaffOrReadOnly]
    service_class = ProductService

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.is_superuser:
            return qs
        return qs.filter(inventory__quantity__gt=0)

    @swagger_auto_schema(request_body=ProductInputSerializer)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductInputSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated_product = self.service_class.update_product(
            instance=instance, data=serializer.validated_data
        )
        return Response(
            self.get_serializer(updated_product).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.inventory.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductCategoryListCreateAPIView(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategoryOutputSerializer
    permission_classes = [StaffOrReadOnly]

    @swagger_auto_schema(request_body=ProductCategoryInputSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ProductCategoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = ProductCategory.objects.create(**serializer.validated_data)
        return Response(
            self.get_serializer(category).data, status=status.HTTP_201_CREATED
        )


class ProductCategoryDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategoryOutputSerializer
    permission_classes = [StaffOrReadOnly]


class ProductReviewListCreateAPIView(generics.ListAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewOutputSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ReviewFilter
    service_class = ReviewService

    @swagger_auto_schema(request_body=ProductReviewInputSerializer)
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ProductReviewInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = self.service_class.create_review(
            user=user, data=serializer.validated_data
        )
        return Response(
            self.get_serializer(review).data, status=status.HTTP_201_CREATED
        )


class ProductReviewDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewOutputSerializer
    permission_classes = [OwnerOrReadOnly]
    service_class = ReviewService

    @swagger_auto_schema(request_body=ProductReviewUpdateInputSerializer)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductReviewUpdateInputSerializer(
            data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        updated_review = self.service_class.update_review(
            instance=instance, data=serializer.validated_data
        )
        return Response(
            self.get_serializer(updated_review).data,
            status=status.HTTP_200_OK,
        )
