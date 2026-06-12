from django.contrib import admin

from .models import (
    Archetype,
    Clan,
    CreationRule,
    Flaw,
    GameLine,
    GenerationStat,
    Merit,
    Trait,
)


@admin.register(GameLine)
class GameLineAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "edition", "is_active")
    list_filter = ("edition", "is_active")
    search_fields = ("code", "name")
    prepopulated_fields = {"code": ("name",)}


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "subgroup", "line", "max_rating", "order", "origin")
    list_filter = ("line", "category", "subgroup", "origin")
    list_editable = ("origin",)
    search_fields = ("code", "name")
    ordering = ("line", "category", "order")


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "line", "default_sect", "is_bloodline", "origin")
    list_filter = ("line", "is_bloodline", "default_sect", "origin")
    list_editable = ("origin",)
    search_fields = ("code", "name")
    filter_horizontal = ("disciplines",)


@admin.register(Archetype)
class ArchetypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "line", "origin")
    list_filter = ("line", "origin")
    list_editable = ("origin",)
    search_fields = ("code", "name")


@admin.register(GenerationStat)
class GenerationStatAdmin(admin.ModelAdmin):
    list_display = (
        "generation",
        "line",
        "max_blood_pool",
        "blood_per_turn",
        "max_trait_rating",
        "origin",
    )
    list_filter = ("line", "origin")
    list_editable = ("origin",)
    ordering = ("line", "-generation")


@admin.register(Merit)
class MeritAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "cost", "line", "origin")
    list_filter = ("line", "category", "origin")
    search_fields = ("code", "name")


@admin.register(Flaw)
class FlawAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "bonus", "line", "origin")
    list_filter = ("line", "category", "origin")
    search_fields = ("code", "name")


@admin.register(CreationRule)
class CreationRuleAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description", "line", "origin")
    list_filter = ("line", "origin")
    list_editable = ("origin",)
    search_fields = ("key", "description")
