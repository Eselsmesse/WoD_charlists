from django.contrib import admin
from .models import GoogleUser

@admin.register(GoogleUser)
class GoogleUserAdmin(admin.ModelAdmin):
    list_display = ("email", "google_id", "created_at")
    search_fields = ("email", "google_id")
