from rest_framework import serializers

from rules.models import Archetype, Clan, GameLine, Trait

from .models import Character, CharacterTrait, Tag


class TagBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color")


class CharacterTraitSerializer(serializers.ModelSerializer):
    trait = serializers.SlugRelatedField(slug_field="code", read_only=True)
    name = serializers.CharField(source="trait.name", read_only=True)
    category = serializers.CharField(source="trait.category", read_only=True)

    class Meta:
        model = CharacterTrait
        fields = ("trait", "name", "category", "rating", "specialty", "notes")


class CharacterListSerializer(serializers.ModelSerializer):
    """Лёгкий сериализатор для списка — без вложенных трейтов."""

    line = serializers.SlugRelatedField(slug_field="code", read_only=True)
    clan = serializers.SlugRelatedField(slug_field="code", read_only=True)
    tags = TagBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = (
            "id",
            "line",
            "name",
            "clan",
            "generation",
            "concept",
            "chronicle",
            "is_public",
            "updated_at",
            "tags",
        )


class CharacterDetailSerializer(serializers.ModelSerializer):
    """Полный чарник: ядро + вложенные трейты и теги.

    Связи со справочником адресуются по `code` (стабильнее, чем PK).
    """

    line = serializers.SlugRelatedField(slug_field="code", queryset=GameLine.objects.all())
    clan = serializers.SlugRelatedField(
        slug_field="code", queryset=Clan.objects.all(), required=False, allow_null=True
    )
    nature = serializers.SlugRelatedField(
        slug_field="code", queryset=Archetype.objects.all(), required=False, allow_null=True
    )
    demeanor = serializers.SlugRelatedField(
        slug_field="code", queryset=Archetype.objects.all(), required=False, allow_null=True
    )
    traits = CharacterTraitSerializer(many=True, read_only=True)
    tags = TagBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = (
            "id",
            "line",
            "name",
            "player",
            "chronicle",
            "concept",
            "clan",
            "nature",
            "demeanor",
            "generation",
            "sect",
            "sire",
            "willpower_permanent",
            "willpower_current",
            "humanity",
            "path_name",
            "blood_pool_current",
            "health",
            "descriptors",
            "history",
            "is_public",
            "created_at",
            "updated_at",
            "traits",
            "tags",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        """Клан и архетипы должны принадлежать линейке персонажа."""
        line = attrs.get("line") or (self.instance.line if self.instance else None)
        for field in ("clan", "nature", "demeanor"):
            value = attrs.get(field)
            if value is not None and value.line_id != line.id:
                raise serializers.ValidationError(
                    {field: f"«{value.code}» не принадлежит линейке {line.code}."}
                )
        return attrs


class TraitUpsertItemSerializer(serializers.Serializer):
    trait = serializers.SlugField()
    rating = serializers.IntegerField(min_value=0)
    specialty = serializers.CharField(required=False, allow_blank=True, max_length=100)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=200)


class CharacterTraitsBulkSerializer(serializers.Serializer):
    """Bulk-апсерт точек трейтов (автосейв листа): upsert по code трейта."""

    traits = TraitUpsertItemSerializer(many=True)

    def validate(self, attrs):
        character = self.context["character"]
        codes = [item["trait"] for item in attrs["traits"]]
        traits_by_code = {
            trait.code: trait
            for trait in Trait.objects.filter(line=character.line, code__in=codes)
        }
        unknown = sorted(set(codes) - set(traits_by_code))
        if unknown:
            raise serializers.ValidationError(
                {"traits": f"Неизвестные коды трейтов линейки {character.line.code}: {unknown}"}
            )
        for item in attrs["traits"]:
            trait = traits_by_code[item["trait"]]
            if item["rating"] > trait.max_rating:
                raise serializers.ValidationError(
                    {
                        "traits": (
                            f"{trait.code}: рейтинг {item['rating']} "
                            f"превышает максимум {trait.max_rating}."
                        )
                    }
                )
            item["trait_obj"] = trait
        return attrs

    def save(self):
        character = self.context["character"]
        for item in self.validated_data["traits"]:
            CharacterTrait.objects.update_or_create(
                character=character,
                trait=item["trait_obj"],
                defaults={
                    "rating": item["rating"],
                    "specialty": item.get("specialty", ""),
                    "notes": item.get("notes", ""),
                },
            )
        return character
