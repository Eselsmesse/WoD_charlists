# SPEC-005: API аутентификации

> Статус: DONE · Фаза: 2 · Зависит от: SPEC-002

## Цель

Реализовать эндпоинты регистрации и выдачи/обновления JWT, плюс `me`.

## Контекст / ссылки

- [04-api-spec.md](../04-api-spec.md#аутентификация-accounts).

## Скоуп

**В работе:**
- `POST /api/v1/auth/register/` — создание пользователя (email + password,
  валидация пароля Django), без авто-логина (или с выдачей пары — на усмотрение).
- `POST /api/v1/auth/token/` и `/token/refresh/` — simplejwt вьюхи.
- `GET /api/v1/auth/me/` — данные текущего пользователя (`IsAuthenticated`).

**Не трогаем:**
- Сброс пароля по email, верификация email, соц-логин — бэклог.

## Критерии приёмки

- [x] Регистрация с валидным email/паролем → 201; дубль email → 400.
- [x] Слабый пароль отклоняется валидаторами Django.
- [x] `token` отдаёт access+refresh; `refresh` обновляет access.
- [x] `me` без токена → 401; с токеном → данные юзера (без пароля/хэша).

## Заметки по реализации

- Пароль — только на запись (`write_only`), никогда не в ответе.
- Не раскрывать, существует ли email, сверх необходимого.

## Затрагиваемые файлы (ориентир)

- `accounts/serializers.py`, `accounts/views.py`, `accounts/urls.py`

## Тесты

- `APITestCase`: регистрация (успех/дубль/слабый пароль), получение и refresh
  токена, `me` с/без токена.

## Definition of Done

Полный auth-флоу работает и покрыт тестами.

## Итоги реализации (2026-06-12)

- `POST /api/v1/auth/register/` — `RegisterSerializer` (email + password,
  `validate_password` Django, пароль write-only), 201 без авто-логина.
- `POST /api/v1/auth/token/` и `/token/refresh/` — стандартные вьюхи simplejwt
  (вход по email — `USERNAME_FIELD`).
- `GET /api/v1/auth/me/` — `UserSerializer` (id, email, имя, дата регистрации),
  только `IsAuthenticated` (глобальный дефолт DRF).
- Тесты: 8 новых (успех/дубль/слабый пароль, пара токенов, неверный пароль 401,
  refresh, me 401/200) — всего 23, OK.
