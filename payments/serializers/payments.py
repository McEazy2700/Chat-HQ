from rest_framework import serializers

from payments.models.payments import Payment


class InitiatePaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "narration", "payment_type"]


class PaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "reference",
            "payment_type",
            "status",
            "amount",
            "narration",
            "last_updated",
            "created_at",
        ]


class VerifyPaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["reference"]
