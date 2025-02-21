import os
from typing import Any
import uuid
import base64
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PaymentStatus(models.TextChoices):
    Success = "success"
    Pending = "pending"
    Canceled = "canceled"
    Failed = "failed"


class PaymentType(models.TextChoices):
    Subscription = "subscription"
    Renewal = "renewal"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=255, unique=True)
    payment_type = models.CharField(
        max_length=255,
        choices=PaymentType.choices,
        default=PaymentType.Subscription,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.Pending,
        null=True,
        blank=True,
    )
    amount = models.BigIntegerField(
        null=True, blank=True, help_text="payment amount in kobo"
    )
    narration = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.reference is None:
            self.reference = base64.urlsafe_b64encode(os.urandom(30)).decode()
        return super().save(*args, **kwargs)
