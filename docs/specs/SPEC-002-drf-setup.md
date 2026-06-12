# SPEC-002: Каркас DRF + JWT + модель пользователя

> Статус: DONE · Фаза: 0 · Зависит от: SPEC-001

## Цель

Поставить и сконфигурировать Django REST Framework, JWT-аутентификацию, CORS и
кастомную модель пользователя; завести версионированный API-роутинг `/api/v1/`.

## Контекст / ссылки

- [01-architecture.md](../01-architecture.md) (ADR-0002, 0003), [04-api-spec.md](../04-api-spec.md).

## Скоуп

**В работе:**
- Зависимости: `djangorestframework`, `djangorestframework-simplejwt`,
  `django-cors-headers`.
- Приложение `accounts` с **кастомной моделью пользователя** (наследник
  `AbstractUser`, вход по email — на ваше усмотрение, но завести СРАЗУ, пока БД
  пустая). `AUTH_USER_MODEL = "accounts.User"`.
- Настроить `REST_FRAMEWORK` (дефолтная аутентификация — JWT, пагинация, права
  по умолчанию `IsAuthenticated`).
- Роутинг: `config/urls.py` → `path("api/v1/", include(...))`; заглушечный
  health-эндпоинт `GET /api/v1/health/` → `{"status": "ok"}`.
- CORS для dev-origin SPA (localhost:5173 и т.п.) из env.

**Не трогаем:**
- Реальные эндпоинты auth/персонажей (SPEC-005/006) — здесь только каркас и health.
- Доменные модели (SPEC-003).

## Критерии приёмки

- [x] `GET /api/v1/health/` возвращает 200 `{"status": "ok"}`.
- [x] `AUTH_USER_MODEL` указывает на кастомную модель; миграции применяются с нуля.
- [x] DRF browsable API доступен в dev; JWT-классы подключены глобально.
- [x] CORS разрешает dev-origin фронта из настроек env.
- [x] `python manage.py check` и существующие тесты зелёные.

## Заметки по реализации

- **Кастомного пользователя обязательно завести до первых данных** — менять
  `AUTH_USER_MODEL` после миграций крайне болезненно.
- Менеджер пользователя — при входе по email переопределить `create_user`/
  `create_superuser`.
- Время жизни access-токена — короткое; refresh — длиннее; значения из env.

## Затрагиваемые файлы (ориентир)

- `accounts/` (новое приложение: `models.py`, `admin.py`, `apps.py`, `managers.py`)
- `config/settings/base.py` (INSTALLED_APPS, REST_FRAMEWORK, SIMPLE_JWT, CORS, AUTH_USER_MODEL)
- `config/urls.py`

## Тесты

- `APITestCase`: health 200; создание пользователя; получение JWT-пары для тестового юзера.

## Definition of Done

Каркас API работает, пользователь кастомный, JWT и CORS настроены, тесты зелёные.

## Итоги реализации (2026-06-12)

- Приложение `accounts`: `User(AbstractUser)` без `username`, вход по `email`
  (`USERNAME_FIELD = "email"`), свой `UserManager`, админка на базе `UserAdmin`;
  миграция `accounts.0001_initial`.
- `REST_FRAMEWORK`: JWT-аутентификация по умолчанию, права `IsAuthenticated`,
  пагинация `PageNumberPagination` (20). `SIMPLE_JWT`: access 15 мин / refresh
  7 дней, настраивается env (`JWT_ACCESS_LIFETIME_MINUTES`, `JWT_REFRESH_LIFETIME_DAYS`).
- CORS: `CORS_ALLOWED_ORIGINS` из env; dev-дефолт `localhost:5173` (Vite).
- `GET /api/v1/health/` (`AllowAny`) → `{"status": "ok"}`; вью в `config/views.py`.
- Тесты: 6 шт. (health, создание user/superuser, обязательность email, JWT-пара).
- Устаревший локальный `db.sqlite3` старого скелета удалён (несовместим с новым
  `AUTH_USER_MODEL`); миграции проверены с нуля.
