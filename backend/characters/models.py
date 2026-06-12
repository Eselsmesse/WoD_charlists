"""Контент пользователя: персонажи, их трейты, теги и группы (ADR-0006/0007).

Ядро персонажа — в колонках (запрашиваемо, валидируемо), гибкие точечные
трейты — в связной таблице CharacterTrait.
"""

from django.conf import settings
from django.db import models


class Character(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
        verbose_name="Владелец",
    )
    # PROTECT: не терять персонажей при чистке справочника
    line = models.ForeignKey("rules.GameLine", on_delete=models.PROTECT, verbose_name="Линейка")
    name = models.CharField("Имя", max_length=120)
    player = models.CharField("Игрок", max_length=120, blank=True)
    chronicle = models.CharField("Хроника", max_length=120, blank=True)
    concept = models.CharField("Концепция", max_length=200, blank=True)

    clan = models.ForeignKey(
        "rules.Clan", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Клан"
    )
    nature = models.ForeignKey(
        "rules.Archetype",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Натура",
    )
    demeanor = models.ForeignKey(
        "rules.Archetype",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Маска",
    )
    generation = models.PositiveSmallIntegerField("Поколение", default=13)
    sect = models.CharField("Секта", max_length=30, blank=True)
    sire = models.CharField("Сир", max_length=120, blank=True)

    # производные/трекинг
    willpower_permanent = models.PositiveSmallIntegerField("Сила воли (пост.)", default=1)
    willpower_current = models.PositiveSmallIntegerField("Сила воли (тек.)", default=1)
    humanity = models.PositiveSmallIntegerField("Человечность", default=7)
    path_name = models.CharField("Путь (если не Человечность)", max_length=120, blank=True)
    blood_pool_current = models.PositiveSmallIntegerField("Запас крови (тек.)", default=10)
    health = models.JSONField("Здоровье", default=dict, blank=True)  # состояние 7 уровней

    # описательная часть (вход для квенты)
    descriptors = models.JSONField("Дескрипторы", default=dict, blank=True)  # age, hair, eyes...
    history = models.TextField("Квента", blank=True)

    is_public = models.BooleanField("Публичный", default=False)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class CharacterTrait(models.Model):
    """Привязка персонажа к трейту с рейтингом (точки)."""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="traits", verbose_name="Персонаж"
    )
    trait = models.ForeignKey("rules.Trait", on_delete=models.PROTECT, verbose_name="Трейт")
    rating = models.PositiveSmallIntegerField("Рейтинг", default=0)
    specialty = models.CharField("Специализация", max_length=100, blank=True)
    notes = models.CharField("Заметки", max_length=200, blank=True)

    class Meta:
        verbose_name = "Трейт персонажа"
        verbose_name_plural = "Трейты персонажа"
        unique_together = [("character", "trait")]

    def __str__(self):
        return f"{self.trait}: {self.rating}"


class CharacterMerit(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="merits", verbose_name="Персонаж"
    )
    merit = models.ForeignKey("rules.Merit", on_delete=models.PROTECT, verbose_name="Мерит")
    notes = models.CharField("Заметки", max_length=200, blank=True)

    class Meta:
        verbose_name = "Мерит персонажа"
        verbose_name_plural = "Мериты персонажа"
        unique_together = [("character", "merit")]

    def __str__(self):
        return str(self.merit)


class CharacterFlaw(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="flaws", verbose_name="Персонаж"
    )
    flaw = models.ForeignKey("rules.Flaw", on_delete=models.PROTECT, verbose_name="Флоу")
    notes = models.CharField("Заметки", max_length=200, blank=True)

    class Meta:
        verbose_name = "Флоу персонажа"
        verbose_name_plural = "Флоу персонажа"
        unique_together = [("character", "flaw")]

    def __str__(self):
        return str(self.flaw)


class Tag(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
        verbose_name="Владелец",
    )
    name = models.CharField("Название", max_length=50)
    color = models.CharField("Цвет", max_length=7, blank=True)  # #RRGGBB
    characters = models.ManyToManyField(
        Character, blank=True, related_name="tags", verbose_name="Персонажи"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        unique_together = [("owner", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class CharacterGroup(models.Model):
    """Группа персонажей: партия/coterie/хроника."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="character_groups",
        verbose_name="Владелец",
    )
    name = models.CharField("Название", max_length=100)
    members = models.ManyToManyField(
        Character, blank=True, related_name="groups", verbose_name="Участники"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        ordering = ["name"]

    def __str__(self):
        return self.name
