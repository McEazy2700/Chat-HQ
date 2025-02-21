from typing import Any, Optional, cast
from rest_framework import permissions
from rest_framework.views import Request
from rest_framework.viewsets import ViewSet

from users.models.auth import ServiceAPIKey


class ServicePermissions(permissions.BasePermission):
    def has_permission(self, request: Request, view: ViewSet):
        api_key = cast(
            Optional[str],
            cast(dict[str, Any], request.META).get("HTTP_X_SERVICE_API_KEY"),
        )

        if not api_key:
            return False

        parts = api_key.split(" ")
        return ServiceAPIKey.objects.filter(
            service_name=parts[0], key=parts[1]
        ).exists()
