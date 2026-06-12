"""Доменные операции над персонажами, переиспользуемые между приложениями."""

from .models import Character, CharacterTrait


def duplicate_character(source, owner, name=None):
    """Независимая копия персонажа (с трейтами, меритами и флоу) для owner."""
    clone = Character.objects.get(pk=source.pk)
    clone.pk = None
    clone.owner = owner
    clone.name = name or f"{source.name} (копия)"
    clone.is_public = False
    clone.save()
    CharacterTrait.objects.bulk_create(
        CharacterTrait(
            character=clone,
            trait=ct.trait,
            rating=ct.rating,
            specialty=ct.specialty,
            notes=ct.notes,
        )
        for ct in source.traits.all()
    )
    for relation in (source.merits, source.flaws):
        for item in relation.all():
            item.pk = None
            item.character = clone
            item.save()
    return clone
