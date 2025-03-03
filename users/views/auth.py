from django.utils import timezone
import jwt
from typing import Any, cast
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import Request, Response, exceptions, status
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings

from includes.serializers import MessageResponseSerializer
from users.models.auth import TimedAuthTokenPair
from users.models.users import User
from users.permissions.services import ServicePermissions
from users.serializers.auth import (
    LoginRequestSerializer,
    RefreshTokenRequestSerializer,
    SignupRequestSerializer,
    TimedAuthTokenPairSerializer,
    UserWithPermissionsSerializer,
    VerifyTokenRequestSerializer,
)


class AuthViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        request_body=SignupRequestSerializer,
        responses={status.HTTP_201_CREATED: MessageResponseSerializer},
        tags=["Auth"],
    )
    @action(methods=["POST"], detail=False, url_path="signup", url_name="signup")
    def signup(self, request: Request):
        serializer = SignupRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        if validated_data.get("password1") != validated_data.get("password2"):
            raise exceptions.ValidationError("Passwords do not match")
        _ = User.objects.create_user(
            email=cast(str, validated_data.get("email")),
            password=cast(str, validated_data.get("password1")),
        )

        response = {"message": "Signup successful"}
        response_serializer = MessageResponseSerializer(data=response)
        _ = serializer.is_valid()

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        request_body=LoginRequestSerializer,
        responses={status.HTTP_200_OK: TimedAuthTokenPairSerializer},
        tags=["Auth"],
    )
    @action(methods=["POST"], detail=False, url_path="token", url_name="token")
    def token_create(self, request: Request):
        serializer = LoginRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)
        user = get_object_or_404(User, email=validated_data.get("email"))
        is_valid = user.check_password(cast(str, validated_data.get("password", "")))

        if not is_valid:
            raise exceptions.AuthenticationFailed("Incorrect email or password")
        token = TimedAuthTokenPair.create_for_user(user)

        return Response(
            TimedAuthTokenPairSerializer(token).data, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=VerifyTokenRequestSerializer,
        responses={status.HTTP_200_OK: TimedAuthTokenPairSerializer},
        tags=["Auth"],
    )
    @action(methods=["POST"], detail=False, url_path="verify", url_name="verify")
    def verify(self, request: Request):
        serializer = VerifyTokenRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)
        token = get_object_or_404(TimedAuthTokenPair, token=validated_data.get("token"))

        try:
            jwt.decode(token.token, cast(str, settings.SECRET_KEY), algorithms="HS256")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token Expired")

        return Response(
            TimedAuthTokenPairSerializer(token).data, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=RefreshTokenRequestSerializer,
        responses={status.HTTP_200_OK: TimedAuthTokenPairSerializer},
        tags=["Auth"],
    )
    @action(methods=["POST"], detail=False, url_path="refresh", url_name="refresh")
    def refresh_token(self, request: Request):
        serializer = RefreshTokenRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)
        token = get_object_or_404(
            TimedAuthTokenPair, refresh_token=validated_data.get("refresh_token")
        )

        if timezone.now() > token.expires_at:
            _ = token.delete()
            raise exceptions.AuthenticationFailed("Refresh Token Expired")

        new_token = TimedAuthTokenPair.create_for_user(token.user)
        _ = token.delete()

        return Response(
            TimedAuthTokenPairSerializer(new_token).data, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        request_body=VerifyTokenRequestSerializer,
        responses={status.HTTP_200_OK: UserWithPermissionsSerializer},
        tags=["Auth"],
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="service_verify_token",
        url_name="service_verify_token",
        permission_classes=[ServicePermissions],
    )
    def service_verify_token(self, request: Request):
        serializer = VerifyTokenRequestSerializer(data=request.data)
        _ = serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)
        token = get_object_or_404(TimedAuthTokenPair, token=validated_data.get("token"))

        try:
            print(token.token)
            jwt.decode(token.token, cast(str, settings.SECRET_KEY), algorithms="HS256")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token Expired")

        return Response(
            UserWithPermissionsSerializer(token.user).data, status=status.HTTP_200_OK
        )
