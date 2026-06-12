from django.db import models

class SystemDefinition(models.Model):
    """Таблица для хранения игровых систем (линеек WoD)."""
    SYSTEM_CHOICES = [
        (-1, 'Vampire: The Masquerade'),
        (-2, 'Werewolf: The Apocalypse'),
        (-3, 'Mage: The Ascension'),
        (-4, 'Hunter: The Reckoning'),
        (-5, 'Changeling: The Dreaming'),
    ]

    system_id = models.IntegerField(
        primary_key=True,
        choices=SYSTEM_CHOICES,
        default=-1,
        verbose_name="ID системы"
    )
    system_name = models.CharField(
        max_length=100,
        verbose_name="Название системы"
    )

    class Meta:
        verbose_name = "Система"
        verbose_name_plural = "Системы"

    def __str__(self):
        return self.system_name


class Character(models.Model):
    """Модель для хранения данных персонажа."""

    system_name = models.ForeignKey(
        SystemDefinition,
        on_delete=models.CASCADE,
        verbose_name="Игровая система"
    )
    character_name = models.CharField(
        max_length=100,
        verbose_name="Имя персонажа"
    )
    attributes = models.JSONField(
        verbose_name="Атрибуты",
        help_text="JSON с характеристиками (Сила, Ловкость, Харизма и т.д.)"
    )
    background = models.TextField(
        verbose_name="Предыстория",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"

    def __str__(self):
        return f"{self.character_name} ({self.system_name})"