from django.urls import include, path
from django.conf import settings
from src.apps.payments.views import StripeWebhookView


urlpatterns = [
    path("accounts/", include("src.apps.accounts.urls", namespace="accounts")),
    path("products/", include("src.apps.products.urls", namespace="products")),
    path("", include("src.apps.orders.urls", namespace="orders")),
    path("stripe/webhook/", StripeWebhookView.as_view()),
]

if settings.DEBUG:
    from src.swagger import schema_view
    from django.conf.urls.static import static
    
    print("gej")
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path(
            "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"
        ),
    ]
    
    
