from django.urls import path
from src.apps.orders.views import (
    CartItemsDetailAPIView,
    CartItemsListCreateAPIView,
    CartListCreateAPIView,
    CartDetailAPIView,
    CouponListCreateAPIView,
    CouponDetailAPIView,
    OrderCreateAPIView,
    OrderDetailAPIView,
    OrderListAPIView,
)
from src.apps.payments.views import (
    StripeSessionView,
    StripeConfigView,
)

app_name = "orders"

urlpatterns = [
    path("coupons/", CouponListCreateAPIView.as_view(), name="coupon-list"),
    path("coupons/<uuid:pk>/", CouponDetailAPIView.as_view(), name="coupon-detail"),
    path("carts/", CartListCreateAPIView.as_view(), name="cart-list"),
    path("carts/<uuid:pk>/", CartDetailAPIView.as_view(), name="cart-detail"),
    path(
        "carts/<uuid:pk>/items/",
        CartItemsListCreateAPIView.as_view(),
        name="cart-item-list",
    ),
    path(
        "carts/<uuid:pk>/items/<uuid:cart_item_pk>/",
        CartItemsDetailAPIView.as_view(),
        name="cart-item-detail",
    ),
    path("carts/<uuid:pk>/order/", OrderCreateAPIView.as_view(), name="create-order"),
    path("orders/", OrderListAPIView.as_view(), name="order-list"),
    path("orders/<uuid:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("orders/<uuid:pk>/session/", StripeSessionView.as_view(), name="stripe-setup"),
    path("orders/stripe/", StripeConfigView.as_view(), name="stripe-detail"),
]
