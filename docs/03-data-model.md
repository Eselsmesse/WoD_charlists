# 03. Модель данных

Принцип (ADR-0006/0007): **`rules` = факты правил (общие)**, **`characters` =
контент пользователя**. Ядро персонажа — в колонках (запрашиваемо, валидируемо),
гибкие точечные трейты — в связной таблице `CharacterTrait`.

## ERD (упрощённо)

```
accounts.User (или стандартный) ──1───┐
                                       │ owner
                                       ▼
rules.GameLine ──1──< rules.Clan       characters.Character >──M2M── characters.Tag
      │                   │  \              │   │   │
      │                   │   \M2M          │   │   └──< characters.CharacterTrait >── rules.Trait
      ├──< rules.Trait ───┘    disciplines  │   │
      ├──< rules.Archetype                  │   └──1──< sharing.ShareLink
      ├──< rules.Merit / rules.Flaw         │
      └──< rules.GenerationStat             └──1──< quenta.Narrative (версии)
                                                      │
quenta.CitySetting   quenta.LoreDocument ──< quenta.LoreChunk   quenta.GenerationRequest
```

## Приложение `rules` (справочник, read-only через API)

```python
class GameLine(models.Model):
    code = models.SlugField(unique=True)        # "vampire"
    name = models.CharField(max_length=100)     # "Vampire: The Masquerade"
    edition = models.CharField(max_length=20, default="V20")
    is_active = models.BooleanField(default=True)

class Trait(models.Model):
    """Любой точечный трейт: атрибут, способность, дисциплина, бэкграунд, добродетель."""
    class Category(models.TextChoices):
        ATTRIBUTE = "attribute"
        TALENT = "talent"
        SKILL = "skill"
        KNOWLEDGE = "knowledge"
        DISCIPLINE = "discipline"
        BACKGROUND = "background"
        VIRTUE = "virtue"
    line = models.ForeignKey(GameLine, on_delete=models.CASCADE, related_name="traits")
    category = models.CharField(max_length=20, choices=Category.choices)
    code = models.SlugField()                   # "strength", "celerity"
    name = models.CharField(max_length=100)
    subgroup = models.CharField(max_length=20, blank=True)  # physical/social/mental для атрибутов
    min_rating = models.PositiveSmallIntegerField(default=0)
    max_rating = models.PositiveSmallIntegerField(default=5)
    requires_specialty_at = models.PositiveSmallIntegerField(null=True, blank=True)
    summary = models.TextField(blank=True)      # ОРИГИНАЛЬНОЕ краткое, не копия книги
    order = models.PositiveSmallIntegerField(default=0)
    class Meta:
        unique_together = [("line", "category", "code")]

class Clan(models.Model):
    line = models.ForeignKey(GameLine, on_delete=models.CASCADE, related_name="clans")
    code = models.SlugField()
    name = models.CharField(max_length=100)
    default_sect = models.CharField(max_length=30, blank=True)
    disciplines = models.ManyToManyField(Trait, blank=True,
        limit_choices_to={"category": Trait.Category.DISCIPLINE})
    weakness_summary = models.TextField(blank=True)  # своими словами
    is_bloodline = models.BooleanField(default=False)

class Archetype(models.Model):           # Nature / Demeanor
    line = models.ForeignKey(GameLine, on_delete=models.CASCADE)
    code = models.SlugField()
    name = models.CharField(max_length=100)
    summary = models.TextField(blank=True)

class GenerationStat(models.Model):      # таблица §5.3 домена
    line = models.ForeignKey(GameLine, on_delete=models.CASCADE)
    generation = models.PositiveSmallIntegerField()  # 13, 12, ...
    max_blood_pool = models.PositiveSmallIntegerField()
    blood_per_turn = models.PositiveSmallIntegerField()
    max_trait_rating = models.PositiveSmallIntegerField(default=5)

class Merit(models.Model): ...           # category, name, cost, summary
class Flaw(models.Model): ...            # category, name, bonus, summary
# (Опционально, не для MVP) DisciplinePower: discipline FK, level 1..5, name, summary
```

## Приложение `characters` (контент пользователя)

```python
class Character(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="characters")
    line = models.ForeignKey("rules.GameLine", on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    player = models.CharField(max_length=120, blank=True)
    chronicle = models.CharField(max_length=120, blank=True)
    concept = models.CharField(max_length=200, blank=True)

    clan = models.ForeignKey("rules.Clan", null=True, blank=True, on_delete=models.SET_NULL)
    nature = models.ForeignKey("rules.Archetype", null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="+")
    demeanor = models.ForeignKey("rules.Archetype", null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="+")
    generation = models.PositiveSmallIntegerField(default=13)
    sect = models.CharField(max_length=30, blank=True)
    sire = models.CharField(max_length=120, blank=True)

    # производные/трекинг
    willpower_permanent = models.PositiveSmallIntegerField(default=1)
    willpower_current = models.PositiveSmallIntegerField(default=1)
    humanity = models.PositiveSmallIntegerField(default=7)
    path_name = models.CharField(max_length=120, blank=True)   # если не Humanity
    blood_pool_current = models.PositiveSmallIntegerField(default=10)
    health = models.JSONField(default=dict, blank=True)        # состояние 7 уровней

    # описательная часть (вход для квенты)
    descriptors = models.JSONField(default=dict, blank=True)   # age, hair, eyes, height...
    history = models.TextField(blank=True)                     # текущая квента

    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CharacterTrait(models.Model):
    """Привязка персонажа к трейту с рейтингом (точки)."""
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="traits")
    trait = models.ForeignKey("rules.Trait", on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField(default=0)
    specialty = models.CharField(max_length=100, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    class Meta:
        unique_together = [("character", "trait")]

class CharacterMerit(models.Model):   # M2M через таблицу к rules.Merit/Flaw, опционально для MVP
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    merit = models.ForeignKey("rules.Merit", on_delete=models.PROTECT)

class Tag(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True)        # #RRGGBB
    characters = models.ManyToManyField(Character, blank=True, related_name="tags")
    class Meta:
        unique_together = [("owner", "name")]

class CharacterGroup(models.Model):    # "партия"/coterie/хроника
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Character, blank=True, related_name="groups")
```

## Приложение `sharing`

```python
class ShareLink(models.Model):
    character = models.ForeignKey("characters.Character", on_delete=models.CASCADE,
                                  related_name="share_links")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    can_copy = models.BooleanField(default=True)      # разрешить «сохранить себе»
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Публичный read-only просмотр — по `token`; права проверяются в `sharing`, не
раскрывая `owner`-данные.

## Приложение `quenta` — см. [05-ai-quenta-spec.md](05-ai-quenta-spec.md)

```python
class Narrative(models.Model):          # версия сгенерированной квенты
    character = models.ForeignKey("characters.Character", on_delete=models.CASCADE,
                                  related_name="narratives")
    text = models.TextField()
    params = models.JSONField(default=dict)     # тон, длина, язык, акценты
    provider = models.CharField(max_length=50)  # какой LLM
    model = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

class CitySetting(models.Model):        # контекст города/хроники для RAG
    name = models.CharField(max_length=120)
    summary = models.TextField()
    dominant_sects = models.JSONField(default=list)
    tone = models.CharField(max_length=120, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL)   # общий или личный

class LoreDocument(models.Model): ...   # источник лора
class LoreChunk(models.Model): ...      # чанк + embedding (pgvector) для RAG
class GenerationRequest(models.Model):  # лог запроса: статус, токены, стоимость, ошибки
    ...
```

## План миграции с текущих моделей

Сейчас в `storage/models.py` есть `SystemDefinition` (PK — отрицательные choices,
антипаттерн) и `Character` (без `owner`, attributes в одном JSONField).

1. `SystemDefinition` → `rules.GameLine` (нормальный автоинкремент PK + `code`).
2. `storage.Character` → `characters.Character` + `CharacterTrait` (распарсить JSON
   `attributes` в строки трейтов).
3. Данных в БД ещё нет (dev), поэтому проще **переписать модели заново**, чем
   писать data-migration. `db.sqlite3` пересоздаётся. (Подтвердить в SPEC-003.)
4. Приложение `storage` упраздняется (расщепляется на `rules` + `characters`),
   `main` — позже, при переезде на SPA.

> Все числовые правила создания (7/5/3, 13/9/5, freebie, поколения) — НЕ в коде,
> а в `rules` как данные/фикстуры.
