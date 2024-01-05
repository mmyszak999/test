from django import forms
from django.db.models import Case, When, F, Avg
from django.db import models
from django_filters import rest_framework as filters
from src.apps.products.models import Product, ProductCategory, ProductReview, User


class ProductFilter(filters.FilterSet):
    category = filters.ModelMultipleChoiceFilter(
        queryset=ProductCategory.objects.all(),
        field_name="category__name",
        to_field_name="name",
    )
    uncategorized = filters.BooleanFilter(field_name="category", lookup_expr="isnull")
    price = filters.LookupChoiceFilter(
        field_class=forms.DecimalField,
        lookup_choices=[
            ("exact", "Equals"),
            ("gt", "Greater than"),
            ("lt", "Less than"),
        ],
    )
    discounted = filters.BooleanFilter(
        label="Is discounted",
        method="filter_is_discounted",
    )

    average_rating = filters.NumberFilter(
        label="Average rating equals", method="filter_average_rating"
    )
    average_rating__lt = filters.NumberFilter(
        label="Average rating lower than", method="filter_average_rating"
    )
    average_rating__gt = filters.NumberFilter(
        label="Average rating higher than", method="filter_average_rating"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "price",
        ]

    def filter_average_rating(self, queryset, name, value):
        if value is not None:
            queryset = queryset.annotate(
                average_rating=Avg("reviews__rating", distinct=True)
            )
            if name == "average_rating":
                queryset = queryset.filter(average_rating=value)
            if name == "average_rating__lt":
                queryset = queryset.filter(average_rating__lt=value)
            if name == "average_rating__gt":
                queryset = queryset.filter(average_rating__gt=value)
        return queryset

    def filter_is_discounted(self, queryset, name, value):
        if value is not None:
            queryset = queryset.annotate(
                discounted=Case(
                    When(price=F("discount_price"), then=False), default=True
                )
            ).filter(discounted=value)
        return queryset


class ReviewFilter(filters.FilterSet):
    product = filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
        to_field_name="name",
        field_name="product__name",
    )
    user = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        to_field_name="username",
        field_name="user__username",
    )
    rating = filters.LookupChoiceFilter(
        field_class=forms.DecimalField,
        lookup_choices=[
            ("exact", "Equals"),
            ("gt", "Greater than"),
            ("lt", "Less than"),
        ],
    )

    class Meta:
        model = ProductReview
        fields = ["rating"]
