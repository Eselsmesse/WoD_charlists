"""Справочник правил V20: общие факты, не пользовательский контент (ADR-0006).

Числовые правила создания (7/5/3, 13/9/5, freebie) приходят данными
(фикстуры, SPEC-004), а не логикой в коде.
"""

from django.db import models


class SourcedModel(models.Model):
    """Происхождение записи справочника: спарсено или проверено владельцем.

    Все записи каталога создаются пайплайном как «спарсено» (SPEC-004);
    владелец валидирует данные вручную и переводит в «проверено».
    """

    class Origin(models.TextChoices):
        PARSED = "parsed", "Спарсено"
        VERIFIED = "verified", "Проверено"

    origin = models.CharField(
        "Происхождение", max_length=10, choices=Origin.choices, default=Origin.PARSED
    )
    source = models.CharField("Источник", max_length=200, blank=True)

    class Meta:
        abstract = True


class GameLine(models.Model):
    """Линейка WoD: Vampire, Werewolf и т.д."""

    code = models.SlugField("Код", unique=True)  # "vampire"
    name = models.CharField("Название", max_length=100)  # "Vampire: The Masquerade"
    edition = models.CharField("Редакция", max_length=20, default="V20")
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Линейка"
        verbose_name_plural = "Линейки"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.edition})"


class Trait(SourcedModel):
    """Любой точечный трейт: атрибут, способность, дисциплина, бэкграунд, добродетель."""

    class Category(models.TextChoices):
        ATTRIBUTE = "attribute", "Атрибут"
        TALENT = "talent", "Талант"
        SKILL = "skill", "Навык"
        KNOWLEDGE = "knowledge", "Знание"
        DISCIPLINE = "discipline", "Дисциплина"
        BACKGROUND = "background", "Бэкграунд"
        VIRTUE = "virtue", "Добродетель"

    line = models.ForeignKey(
        GameLine, on_delete=models.CASCADE, related_name="traits", verbose_name="Линейка"
    )
    category = models.CharField("Категория", max_length=20, choices=Category.choices)
    code = models.SlugField("Код")  # "strength", "celerity"
    name = models.CharField("Название", max_length=100)
    # physical/social/mental для атрибутов и групп способностей
    subgroup = models.CharField("Подгруппа", max_length=20, blank=True)
    min_rating = models.PositiveSmallIntegerField("Мин. рейтинг", default=0)
    max_rating = models.PositiveSmallIntegerField("Макс. рейтинг", default=5)
    requires_specialty_at = models.PositiveSmallIntegerField(
        "Специализация с", null=True, blank=True
    )
    # Оригинальное краткое описание своими словами, не копия книги (Dark Pack)
    summary = models.TextField("Описание", blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Трейт"
        verbose_name_plural = "Трейты"
        unique_together = [("line", "category", "code")]
        ordering = ["line", "category", "order", "code"]

    def __str__(self):
        return f"{self.name} [{self.get_category_display()}]"


class Clan(SourcedModel):
    line = models.ForeignKey(
        GameLine, on_delete=models.CASCADE, related_name="clans", verbose_name="Линейка"
    )
    code = models.SlugField("Код")
    name = models.CharField("Название", max_length=100)
    default_sect = models.CharField("Секта по умолчанию", max_length=30, blank=True)
    disciplines = models.ManyToManyField(
        Trait,
        blank=True,
        limit_choices_to={"category": Trait.Category.DISCIPLINE},
        related_name="clans",
        verbose_name="Клановые дисциплины",
    )
    # Слабость клана своими словами, не копия книги (Dark Pack)
    weakness_summary = models.TextField("Слабость", blank=True)
    is_bloodline = models.BooleanField("Блудлайн", default=False)

    class Meta:
        verbose_name = "Клан"
        verbose_name_plural = "Кланы"
        unique_together = [("line", "code")]
        ordering = ["line", "code"]

    def __str__(self):
        return self.name


class Archetype(SourcedModel):
    """Архетип личности: Nature / Demeanor."""

    line = models.ForeignKey(
        GameLine, on_delete=models.CASCADE, related_name="archetypes", verbose_name="Линейка"
    )
    code = models.SlugField("Код")
    name = models.CharField("Название", max_length=100)
    summary = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Архетип"
        verbose_name_plural = "Архетипы"
        unique_together = [("line", "code")]
        ordering = ["line", "code"]

    def __str__(self):
        return self.name


class GenerationStat(SourcedModel):
    """Параметры поколения вампира (таблица §5.3 домена)."""

    line = models.ForeignKey(
        GameLine, on_delete=models.CASCADE, related_name="generation_stats", verbose_name="Линейка"
    )
    generation = models.PositiveSmallIntegerField("Поколение")  # 13, 12, ...
    max_blood_pool = models.PositiveSmallIntegerField("Макс. запас крови")
    blood_per_turn = models.PositiveSmallIntegerField("Крови за ход")
    max_trait_rating = models.PositiveSmallIntegerField("Макс. рейтинг трейта", default=5)

    class Meta:
        verbose_name = "Параметры поколения"
        verbose_name_plural = "Параметры поколений"
        unique_together = [("line", "generation")]
        ordering = ["line", "-generation"]

    def __str__(self):
        return f"Поколение {self.generation}"


class MeritFlawBase(SourcedModel):
    """Общее для меритов и флоу: категория, стоимость в очках, описание."""

    class Category(models.TextChoices):
        PHYSICAL = "physical", "Физическая"
        MENTAL = "mental", "Ментальная"
        SOCIAL = "social", "Социальная"
        SUPERNATURAL = "supernatural", "Сверхъестественная"

    line = models.ForeignKey(GameLine, on_delete=models.CASCADE, verbose_name="Линейка")
    category = models.CharField("Категория", max_length=20, choices=Category.choices)
    code = models.SlugField("Код")
    name = models.CharField("Название", max_length=100)
    summary = models.TextField("Описание", blank=True)

    class Meta:
        abstract = True
        unique_together = [("line", "code")]
        ordering = ["line", "category", "code"]

    def __str__(self):
        return self.name


class Merit(MeritFlawBase):
    cost = models.PositiveSmallIntegerField("Стоимость (очки)", default=1)

    class Meta(MeritFlawBase.Meta):
        verbose_name = "Мерит"
        verbose_name_plural = "Мериты"


class Flaw(MeritFlawBase):
    bonus = models.PositiveSmallIntegerField("Бонус (очки)", default=1)

    class Meta(MeritFlawBase.Meta):
        verbose_name = "Флоу"
        verbose_name_plural = "Флоу"


class CreationRule(SourcedModel):
    """Числовое правило создания персонажа как данные (не логика в коде).

    Формат key/value: например key="attribute_priorities", value=[7, 5, 3];
    key="freebie_costs", value={"attribute": 5, "ability": 2, ...}.
    """

    line = models.ForeignKey(
        GameLine, on_delete=models.CASCADE, related_name="creation_rules", verbose_name="Линейка"
    )
    key = models.SlugField("Ключ")  # "attribute_priorities", "freebie_points", ...
    value = models.JSONField("Значение")
    description = models.CharField("Описание", max_length=200, blank=True)

    class Meta:
        verbose_name = "Правило создания"
        verbose_name_plural = "Правила создания"
        unique_together = [("line", "key")]
        ordering = ["line", "key"]

    def __str__(self):
        return f"{self.key} = {self.value}"
