import base64
import os
from typing import Any, cast
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.views import Request, Response, exceptions, status

from payments.models.payments import Payment, PaymentStatus
from payments.serializers.payments import (
    InitiatePaymentRequestSerializer,
    PaymentDetailsSerializer,
    VerifyPaymentRequestSerializer,
)


class PaymentViewSet(viewsets.GenericViewSet):
    @swagger_auto_schema(
        request_body=InitiatePaymentRequestSerializer,
        responses={status.HTTP_201_CREATED: PaymentDetailsSerializer},
        tags=["Payments"],
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="initiate_payment",
        url_name="initiate-payment",
        permission_classes=[permissions.IsAuthenticated],
    )
    def initiate_payment(self, request: Request):
        serializer = InitiatePaymentRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)
        payment = serializer.save(
            user=request.user,
            reference=base64.urlsafe_b64encode(os.urandom(30)).decode(),
        )

        return Response(
            PaymentDetailsSerializer(payment).data, status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        request_body=VerifyPaymentRequestSerializer,
        responses={status.HTTP_201_CREATED: PaymentDetailsSerializer},
        tags=["Payments"],
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="verify_payment",
        url_name="verify-payment",
        permission_classes=[permissions.IsAuthenticated],
    )
    def verify_payment(self, request: Request):
        from users.models.users import User

        serializer = VerifyPaymentRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)
        payment = get_object_or_404(Payment, reference=validated_data.get("reference"))

        if not payment:
            raise exceptions.NotFound("Payment not found")
        if payment.user != request.user:
            raise exceptions.PermissionDenied(
                "You are not allowed to perform this action"
            )

        print("Updating Payment", payment)
        payment.status = PaymentStatus.Success
        payment.save()

        print("Saved Payment")

        user = get_object_or_404(User, id=payment.user.id)
        user_content_type = ContentType.objects.get_for_model(User)

        send_message_permission = Permission.objects.get(
            codename="can_send_message", content_type=user_content_type
        )
        view_chat_permission = Permission.objects.get(
            codename="can_view_chat", content_type=user_content_type
        )
        edit_message_permission = Permission.objects.get(
            codename="can_edit_message", content_type=user_content_type
        )

        user.user_permissions.add(send_message_permission)
        user.user_permissions.add(view_chat_permission)
        user.user_permissions.add(edit_message_permission)

        return Response(
            PaymentDetailsSerializer(payment).data, status=status.HTTP_201_CREATED
        )
