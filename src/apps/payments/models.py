from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()


class PaymentDetails(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment Details"
        verbose_name_plural = "Payment Details"
