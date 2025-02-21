# pyright: reportMissingTypeArgument = false
from django.contrib import admin
from .models import User, ServiceAPIKey
from django.contrib.auth.models import Permission


class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "content_type")
    search_fields = ("name", "codename")
    list_filter = ("content_type",)


admin.site.register(Permission, PermissionAdmin)
admin.site.register(User)
admin.site.register(ServiceAPIKey)
