from rest_framework import serializers

from payments.models.payments import Payment


class InitiatePaymentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "narration", "payment_type"]
