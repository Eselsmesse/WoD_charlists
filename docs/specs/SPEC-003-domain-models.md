# SPEC-003: Доменные модели `rules` и `characters`

> Статус: TODO · Фаза: 1 · Зависит от: SPEC-002

## Цель

Реализовать модель данных V20 по [03-data-model.md](../03-data-model.md):
справочник `rules` и пользовательский `characters`, с миграциями и админкой.
Упразднить временное приложение `storage`.

## Контекст / ссылки

- [03-data-model.md](../03-data-model.md) — схема и поля.
- [02-domain-v20.md](../02-domain-v20.md) — смысл трейтов и категорий.
- Сейчас: `storage/models.py` (`SystemDefinition` с отрицательными PK,
  `Character` без owner). Данных в БД нет — мигрируем «с чистого листа».

## Скоуп

**В работе:**
- Приложение `rules`: `GameLine`, `Trait` (с `Category`), `Clan`
  (M2M `disciplines` к `Trait`), `Archetype`, `GenerationStat`, `Merit`, `Flaw`.
- Приложение `characters`: `Character` (owner FK, ядро в колонках),
  `CharacterTrait` (unique по `character+trait`), `Tag`, `CharacterGroup`.
  (Merits/Flaws персонажа — модель завести, наполнение опционально.)
- Миграции с нуля; зарегистрировать всё в админке (inline `CharacterTrait` в
  `Character`, фильтры по линейке/категории).
- Удалить приложение `storage` (или переименовать-переиспользовать), убрать из
  `INSTALLED_APPS` и `urls`.

**Не трогаем:**
- API/сериализаторы (SPEC-006).
- Наполнение каталога данными (SPEC-004) — здесь только пустые таблицы + ручной
  ввод в админке для проверки.
- Жёсткий валидатор лимитов создания (бэклог).

## Критерии приёмки

- [ ] `makemigrations` + `migrate` проходят с нуля без ошибок.
- [ ] В админке можно завести `GameLine=vampire`, пару `Trait`, `Clan`, и
      создать `Character` с несколькими `CharacterTrait` (inline).
- [ ] `unique_together` работает: нельзя добавить один трейт персонажу дважды.
- [ ] `Character.owner` обязателен; теги уникальны в рамках владельца.
- [ ] `storage` удалён, проект поднимается, `check` зелёный.

## Заметки по реализации

- `Trait.code` уникален в рамках `(line, category)`, адресация в API — по `code`.
- `on_delete`: `line` у Character — `PROTECT` (не терять персонажей при чистке
  справочника); `clan/nature/demeanor` — `SET_NULL`.
- `health`/`descriptors` — `JSONField(default=dict)`; не забыть `default=`, не
  `null` для JSON-структур.
- Числа создания (7/5/3 и т.п.) — НЕ в этих моделях как логика; они придут
  данными в SPEC-004 (`GenerationStat` + отдельная таблица/фикстура правил
  создания, формат согласовать здесь).

## Затрагиваемые файлы (ориентир)

- `rules/` (новое), `characters/` (новое), их `models.py`/`admin.py`/`migrations`
- `config/settings/base.py` (INSTALLED_APPS), `config/urls.py`
- удаление `storage/`

## Тесты

- Юнит: создание `Character` + `CharacterTrait`, нарушение `unique_together`
  даёт ошибку; каскады/`PROTECT` ведут себя как заявлено.

## Definition of Done

Схема из [03](../03-data-model.md) в коде, миграции с нуля, админка пригодна для
ручной проверки, `storage` убран.
