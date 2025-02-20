from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models.auth import TimedAuthTokenPair

User = get_user_model()


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
