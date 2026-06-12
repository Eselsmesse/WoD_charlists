# 04. API (DRF)

REST, JSON, версионирование префиксом `/api/v1/`. Аутентификация — JWT
(`Authorization: Bearer <access>`). Ответы об ошибках — стандартный формат DRF.

## Аутентификация (`accounts`)

| Метод | Путь | Назначение | Auth |
|-------|------|-----------|------|
| POST | `/api/v1/auth/register/` | Регистрация (email + password) | нет |
| POST | `/api/v1/auth/token/` | Получить access+refresh | нет |
| POST | `/api/v1/auth/token/refresh/` | Обновить access | refresh |
| GET | `/api/v1/auth/me/` | Текущий пользователь | да |

## Справочник правил (`rules`, read-only)

| Метод | Путь | Назначение |
|-------|------|-----------|
| GET | `/api/v1/lines/` | Список линеек (пока только vampire) |
| GET | `/api/v1/lines/{code}/` | Линейка |
| GET | `/api/v1/lines/{code}/traits/?category=discipline` | Трейты линейки (фильтр по категории/подгруппе) |
| GET | `/api/v1/lines/{code}/clans/` | Кланы + их клановые дисциплины |
| GET | `/api/v1/lines/{code}/archetypes/` | Архетипы (nature/demeanor) |
| GET | `/api/v1/lines/{code}/creation-rules/` | Числа создания: 7/5/3, 13/9/5, freebie, поколения |

> `creation-rules` отдаёт данные из `rules` (а не из кода) — фронт строит UI
> создания на их основе.

## Персонажи (`characters`, owner-only)

| Метод | Путь | Назначение |
|-------|------|-----------|
| GET | `/api/v1/characters/` | Список персонажей пользователя (фильтры: `?tag=`, `?line=`, `?group=`, `?search=`) |
| POST | `/api/v1/characters/` | Создать персонажа |
| GET | `/api/v1/characters/{id}/` | Полный чарник (вложенно: traits, tags) |
| PATCH | `/api/v1/characters/{id}/` | Частичное обновление (ядро) |
| DELETE | `/api/v1/characters/{id}/` | Удалить |
| PUT | `/api/v1/characters/{id}/traits/` | Bulk-апсерт точек трейтов (для автосейва листа) |
| POST | `/api/v1/characters/{id}/copy/` | Дублировать себе |

### Теги и группы

| Метод | Путь |
|-------|------|
| GET / POST | `/api/v1/tags/` |
| PATCH / DELETE | `/api/v1/tags/{id}/` |
| POST | `/api/v1/characters/{id}/tags/` (присвоить/снять) |
| GET / POST | `/api/v1/groups/` (партии/coterie) |

## Шеринг (`sharing`)

| Метод | Путь | Auth | Назначение |
|-------|------|------|-----------|
| POST | `/api/v1/characters/{id}/share/` | owner | Создать публичную ссылку (вернёт `token`) |
| DELETE | `/api/v1/characters/{id}/share/{token}/` | owner | Отозвать ссылку |
| GET | `/api/v1/shared/{token}/` | нет | Read-only чарник по токену |
| POST | `/api/v1/shared/{token}/copy/` | да | Сохранить копию себе (если `can_copy`) |

## Квента / ИИ (`quenta`) — детали в [05](05-ai-quenta-spec.md)

| Метод | Путь | Назначение |
|-------|------|-----------|
| POST | `/api/v1/characters/{id}/quenta/generate/` | Сгенерировать квенту (тело: тон, длина, язык, city, акценты) |
| GET | `/api/v1/characters/{id}/narratives/` | История версий квенты |
| POST | `/api/v1/characters/{id}/narratives/{nid}/promote/` | Сделать версию текущей `history` |
| GET / POST | `/api/v1/cities/` | Сеттинги городов для контекста |

## Пример: создание персонажа (запрос)

```json
POST /api/v1/characters/
{
  "line": "vampire",
  "name": "Мариус",
  "clan": "ventrue",
  "generation": 13,
  "nature": "director",
  "demeanor": "bon-vivant",
  "concept": "Бывший боксёр, ставший принцем подполья"
}
```

## Пример: bulk-апсерт трейтов (автосейв)

```json
PUT /api/v1/characters/42/traits/
{
  "traits": [
    {"trait": "strength", "rating": 4, "specialty": "Удар"},
    {"trait": "brawl", "rating": 3},
    {"trait": "potence", "rating": 2}
  ]
}
```

## Соглашения

- Трейты адресуются по `code` трейта в рамках линейки (стабильнее, чем PK).
- Все списки — пагинация DRF (`page`/`page_size`).
- Права: `IsOwner` для `characters`/`tags`/`groups`; `rules` — `AllowAny` read-only;
  `shared/{token}` — `AllowAny` read-only по валидному токену.
- Сериализаторы: отдельные `*ListSerializer` (лёгкий) и `*DetailSerializer`
  (с вложенными traits/tags), чтобы список персонажей был дешёвым.
