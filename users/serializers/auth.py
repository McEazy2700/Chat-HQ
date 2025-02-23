from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method

from users.models.auth import TimedAuthTokenPair
from users.models.users import User


class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class VerifyTokenRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class TimedAuthTokenPairSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TimedAuthTokenPair
        fields = ["token", "refresh_token", "user", "expires_at"]


class UserWithPermissionsSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField(
        help_text="List of user permissions (codenames).",
    )
    subscription_payment_paid = serializers.SerializerMethodField(
        help_text="Whether user has made a subscription payment",
    )

    class Meta:
        model = User
        fields = ["id", "email", "permissions", "subscription_payment_paid"]

    @swagger_serializer_method(
        serializer_or_field=serializers.ListSerializer(child=serializers.CharField())
    )
    def get_permissions(self, user: User):
        permission_codenames = []

        for perm in user.user_permissions.all():
            permission_codenames.append(perm.codename)

        for group in user.groups.all():
            for perm in group.permissions.all():
                if perm.codename not in permission_codenames:
                    permission_codenames.append(perm.codename)

        return permission_codenames

    @swagger_serializer_method(
        serializer_or_field=serializers.BooleanField(allow_null=True)
    )
    def get_subscription_payment_paid(self, user: User):
        from payments.models.payments import Payment, PaymentType

        return Payment.objects.filter(
            user=user, payment_type=PaymentType.Subscription
        ).exists()
