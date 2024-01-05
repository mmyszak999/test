from django.urls import path
from django.conf import settings
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from src.apps.accounts.views import (
    AdressListCreateAPIView,
    UserRegisterAPIView,
    UserProfileListAPIView,
    UserProfileDetailAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("users/", UserProfileListAPIView.as_view(), name="user-profile-list"),
    path(
        "users/<uuid:pk>/",
        UserProfileDetailAPIView.as_view(),
        name="user-profile-detail",
    ),
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("addresses/", AdressListCreateAPIView.as_view(), name="address-list"),
]

if getattr(settings, "REST_USE_JWT", False):
    from rest_framework_simplejwt.views import TokenVerifyView
    from dj_rest_auth.jwt_auth import get_refresh_view

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]
