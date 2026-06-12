from django.contrib import admin

from .models import (
    Character,
    CharacterFlaw,
    CharacterGroup,
    CharacterMerit,
    CharacterTrait,
    Tag,
)


class CharacterTraitInline(admin.TabularInline):
    model = CharacterTrait
    extra = 1
    autocomplete_fields = ("trait",)


class CharacterMeritInline(admin.TabularInline):
    model = CharacterMerit
    extra = 0
    autocomplete_fields = ("merit",)


class CharacterFlawInline(admin.TabularInline):
    model = CharacterFlaw
    extra = 0
    autocomplete_fields = ("flaw",)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "line", "clan", "generation", "is_public", "updated_at")
    list_filter = ("line", "clan", "is_public")
    search_fields = ("name", "player", "chronicle", "concept")
    autocomplete_fields = ("owner", "clan", "nature", "demeanor")
    inlines = (CharacterTraitInline, CharacterMeritInline, CharacterFlawInline)
    fieldsets = (
        (None, {"fields": ("owner", "line", "name", "player", "chronicle", "concept")}),
        ("Вампир", {"fields": ("clan", "nature", "demeanor", "generation", "sect", "sire")}),
        (
            "Трекинг",
            {
                "fields": (
                    "willpower_permanent",
                    "willpower_current",
                    "humanity",
                    "path_name",
                    "blood_pool_current",
                    "health",
                )
            },
        ),
        ("Описание", {"fields": ("descriptors", "history")}),
        ("Служебное", {"fields": ("is_public",)}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "color")
    search_fields = ("name",)
    autocomplete_fields = ("owner",)
    filter_horizontal = ("characters",)


@admin.register(CharacterGroup)
class CharacterGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name",)
    autocomplete_fields = ("owner",)
    filter_horizontal = ("members",)
