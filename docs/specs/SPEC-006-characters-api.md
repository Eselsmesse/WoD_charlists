# SPEC-006: API персонажей (CRUD + трейты)

> Статус: TODO · Фаза: 2 · Зависит от: SPEC-003, SPEC-004, SPEC-005

## Цель

REST-API для персонажей: CRUD, вложенные трейты, bulk-апсейв точек, права владельца,
плюс read-only выдача справочника `rules` для построения UI.

## Контекст / ссылки

- [04-api-spec.md](../04-api-spec.md) — эндпоинты и примеры payload.
- [03-data-model.md](../03-data-model.md).

## Скоуп

**В работе:**
- `rules` read-only API: `lines`, `traits` (фильтр `category`/`subgroup`),
  `clans`, `archetypes`, `creation-rules` (числа создания из данных).
- `characters` CRUD: list (лёгкий сериализатор) / detail (с вложенными
  traits+tags) / create / patch / delete.
- `PUT /characters/{id}/traits/` — bulk-апсерт `CharacterTrait` по `code` трейта
  (для автосейва листа): создаёт/обновляет/может обнулять.
- `POST /characters/{id}/copy/` — дубликат себе.
- Права `IsOwner`: пользователь видит/меняет только свои; чужой id → 404 (не 403,
  чтобы не раскрывать существование).
- Фильтры списка: `?line=`, `?tag=`, `?group=`, `?search=`; пагинация.

**Не трогаем:**
- Теги/группы как отдельные ресурсы (SPEC-007) — здесь только фильтрация по ним
  и вложенное чтение.
- Шеринг (SPEC-008), квента (фаза 4).
- Жёсткая валидация лимитов создания — бэклог (сейчас принимаем любые валидные
  по диапазону рейтинги).

## Критерии приёмки

- [ ] CRUD персонажа работает; `owner` проставляется из запроса, не из тела.
- [ ] Список — лёгкий (без всех трейтов), detail — полный.
- [ ] Bulk-апсейв трейтов: повторный вызов обновляет рейтинги, не плодит строки;
      неизвестный `code` трейта → 400 с понятным сообщением.
- [ ] Доступ к чужому персонажу → 404.
- [ ] `rules` эндпоинты доступны без авторизации, только чтение.
- [ ] `creation-rules` отдаёт 7/5/3, 13/9/5, freebie, поколения из данных.

## Заметки по реализации

- Разделить `CharacterListSerializer` / `CharacterDetailSerializer`.
- Bulk-трейты — отдельный сериализатор/вьюха; адресация по `trait.code` в рамках
  `character.line` (валидировать принадлежность трейта линейке персонажа и
  диапазон `rating` по `Trait.min/max`).
- Оптимизация запросов: `select_related`/`prefetch_related` для detail и списков
  (избегать N+1 по traits/tags).
- `perform_create` выставляет `owner=request.user`.

## Затрагиваемые файлы (ориентир)

- `rules/serializers.py`, `rules/views.py`, `rules/urls.py`
- `characters/serializers.py`, `characters/views.py`, `characters/urls.py`
- `characters/permissions.py` (`IsOwner`)

## Тесты

- `APITestCase`: CRUD; изоляция по владельцу (404 на чужого); bulk-апсейв
  (идемпотентность, валидация code/диапазона); фильтры; `rules` read-only.

## Definition of Done

Весь CRUD + трейты + справочник работают, права изолируют владельцев, N+1 нет,
покрыто тестами.
