import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone


class ShareLinkQuerySet(models.QuerySet):
    def active(self):
        """Действующие ссылки: без срока или с непросроченным expires_at."""
        return self.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))


class ShareLink(models.Model):
    character = models.ForeignKey(
        "characters.Character",
        on_delete=models.CASCADE,
        related_name="share_links",
        verbose_name="Персонаж",
    )
    token = models.UUIDField("Токен", default=uuid.uuid4, unique=True, editable=False)
    can_copy = models.BooleanField("Можно копировать", default=True)
    expires_at = models.DateTimeField("Истекает", null=True, blank=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    objects = ShareLinkQuerySet.as_manager()

    class Meta:
        verbose_name = "Публичная ссылка"
        verbose_name_plural = "Публичные ссылки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.character} · {self.token}"
