from django.contrib import admin
from .models import WifiProfileLink


@admin.register(WifiProfileLink)
class WifiProfileLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "expires_at", "is_active", "created_by")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("token_hash", "created_at")
    search_fields = ("created_by__username",)
