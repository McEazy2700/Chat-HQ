# pyright: reportMissingTypeArgument = false
from django.contrib import admin
from .models import ServiceAPIKey, User
from django.contrib.auth.models import Permission


class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "content_type")
    search_fields = ("name", "codename")
    list_filter = ("content_type",)


class ServiceAPIKeyAdmin(admin.ModelAdmin):
    readonly_fields = ("key", "issuer_key")


class CustomUserAdmin(admin.ModelAdmin):
    filter_horizontal = ("user_permissions",)


admin.site.register(Permission, PermissionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ServiceAPIKey, ServiceAPIKeyAdmin)
