from django.contrib import admin

from .models import ShareLink


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ("character", "token", "can_copy", "expires_at", "created_at")
    list_filter = ("can_copy",)
    search_fields = ("character__name", "token")
    autocomplete_fields = ("character",)
