import base64
from datetime import timedelta
import os
from typing import Any, cast
import uuid
import jwt
import secrets
from django.db import models
from django.utils import timezone
from django.conf import settings

from users.models.users import User


class TimedAuthTokenPair(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, unique=True)
    refresh_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def create_for_user(cls, user: User):
        auth_settings = cast(dict[str, Any], settings.CUSTOM_AUTH)
        encoded = jwt.encode(
            {
                "email": user.email,
                "iat": timezone.now(),
                "exp": timezone.now()
                + timedelta(hours=auth_settings.get("TOKEN_VALID_DURATION_HOURS") or 2),
            },
            cast(str, settings.SECRET_KEY),
        )
        refresh_token = secrets.token_hex(32)

        return TimedAuthTokenPair.objects.create(
            user=user,
            token=encoded,
            refresh_token=refresh_token,
            expires_at=timezone.now()
            + timedelta(
                hours=auth_settings.get("REFRESH_TOKEN_VALID_DURATION_HOURS") or 2
            ),
        )


class ServiceAPIKey(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    service_name = models.CharField(max_length=255, unique=True, blank=True)
    service_base_url = models.CharField(max_length=255, null=True, blank=True)
    service_user_logout_endpoint = models.CharField(
        max_length=255, null=True, blank=True
    )
    key = models.CharField(
        max_length=255, unique=True, null=True, blank=True, editable=False
    )
    issuer_key = models.CharField(
        max_length=255, unique=True, null=True, blank=True, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.key is None:
            self.key = base64.urlsafe_b64encode(os.urandom(30)).decode()
            self.issuer_key = base64.urlsafe_b64encode(os.urandom(30)).decode()
        return super().save(*args, **kwargs)
