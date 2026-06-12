from rest_framework import serializers

from .models import Archetype, Clan, GameLine, Trait


class GameLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameLine
        fields = ("code", "name", "edition", "is_active")


class TraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trait
        fields = (
            "code",
            "name",
            "category",
            "subgroup",
            "min_rating",
            "max_rating",
            "requires_specialty_at",
            "summary",
            "order",
        )


class ClanSerializer(serializers.ModelSerializer):
    disciplines = serializers.SlugRelatedField(slug_field="code", many=True, read_only=True)

    class Meta:
        model = Clan
        fields = ("code", "name", "default_sect", "disciplines", "weakness_summary", "is_bloodline")


class ArchetypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archetype
        fields = ("code", "name", "summary")
