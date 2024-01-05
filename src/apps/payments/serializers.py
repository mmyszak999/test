from rest_framework import serializers

from src.apps.payments.models import PaymentDetails


class PaymentDetailsOutputSerializer(serializers.ModelSerializer):
    userprofile_id = serializers.CharField(source="user.userprofile.id", read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PaymentDetails
        fields = (
            "userprofile_id",
            "stripe_charge_id",
            "amount",
            "created",
        )
        read_only_fields = fields
