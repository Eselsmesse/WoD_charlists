from django.contrib import admin

from .models import Archetype, Clan, Flaw, GameLine, GenerationStat, Merit, Trait


@admin.register(GameLine)
class GameLineAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "edition", "is_active")
    list_filter = ("edition", "is_active")
    search_fields = ("code", "name")
    prepopulated_fields = {"code": ("name",)}


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "subgroup", "line", "max_rating", "order")
    list_filter = ("line", "category", "subgroup")
    search_fields = ("code", "name")
    ordering = ("line", "category", "order")


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "line", "default_sect", "is_bloodline")
    list_filter = ("line", "is_bloodline", "default_sect")
    search_fields = ("code", "name")
    filter_horizontal = ("disciplines",)


@admin.register(Archetype)
class ArchetypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "line")
    list_filter = ("line",)
    search_fields = ("code", "name")


@admin.register(GenerationStat)
class GenerationStatAdmin(admin.ModelAdmin):
    list_display = ("generation", "line", "max_blood_pool", "blood_per_turn", "max_trait_rating")
    list_filter = ("line",)
    ordering = ("line", "-generation")


@admin.register(Merit)
class MeritAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "cost", "line")
    list_filter = ("line", "category")
    search_fields = ("code", "name")


@admin.register(Flaw)
class FlawAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "bonus", "line")
    list_filter = ("line", "category")
    search_fields = ("code", "name")
