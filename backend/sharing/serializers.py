from rest_framework import serializers

from characters.models import Character
from characters.serializers import CharacterTraitSerializer

from .models import ShareLink


class ShareLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareLink
        fields = ("token", "can_copy", "expires_at", "created_at")
        read_only_fields = ("token", "created_at")


class PublicCharacterSerializer(serializers.ModelSerializer):
    """Публичный чарник: белый список игровых полей, без приватного.

    Намеренно не переиспользует owner-detail сериализатор: ни owner/email,
    ни player, ни теги/группы, ни внутренние id наружу не отдаются.
    """

    line = serializers.SlugRelatedField(slug_field="code", read_only=True)
    clan = serializers.SlugRelatedField(slug_field="code", read_only=True)
    nature = serializers.SlugRelatedField(slug_field="code", read_only=True)
    demeanor = serializers.SlugRelatedField(slug_field="code", read_only=True)
    traits = CharacterTraitSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = (
            "line",
            "name",
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
            "traits",
        )
        read_only_fields = fields
