# SPEC-001: Гигиена проекта и настройки

> Статус: DONE · Фаза: 0 · Зависит от: —

## Цель

Привести стартовый Django-скелет к рабочему состоянию: безопасные настройки из
окружения, разделение dev/prod, чистый гит, зафиксированные зависимости.

## Контекст / ссылки

- [01-architecture.md](../01-architecture.md) — конфигурация и окружение.
- Сейчас: `wod_charlists/wod_charlists/settings.py` с хардкодом `SECRET_KEY`,
  `DEBUG=True`; в гите затрекан `db.sqlite3` и `__pycache__/*.pyc`; `.gitignore`
  содержит лишь `.venv/` и `cursor/`.

## Скоуп

**В работе:**
- Разнести настройки на `config/settings/{base,dev,prod}.py` (или эквивалент в
  текущем пакете `wod_charlists/`), `DJANGO_SETTINGS_MODULE` по умолчанию — dev.
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, БД — из переменных окружения
  (`django-environ` или `os.environ`). Добавить `.env.example`, `.env` — в `.gitignore`.
- Зависимости: `requirements/base.txt`, `dev.txt`, `prod.txt` (или один
  `requirements.txt` + `pyproject`/`uv`). Зафиксировать Django 5.2.
- `.gitignore`: добавить `*.sqlite3`, `__pycache__/`, `*.pyc`, `.env`, `staticfiles/`,
  `*.log`. **Убрать из индекса** уже затреканные `db.sqlite3` и `__pycache__`
  (`git rm --cached`).
- Обновить README: команды запуска через env-настройки.

**Не трогаем:**
- Доменные модели (SPEC-003), DRF (SPEC-002).
- Физический перенос папок `wod_charlists/ → backend/` — опционально; если делать,
  то здесь и аккуратно, иначе отложить и зафиксировать решение в этой спеке.

## Критерии приёмки

- [x] `python manage.py runserver` поднимается с настройками из `.env`
      (dev), без хардкода секрета.
- [x] При отсутствии `SECRET_KEY` в окружении prod-настройки падают явной ошибкой
      (не используют небезопасный дефолт).
- [x] `git status` чист; `db.sqlite3` и `__pycache__` больше не отслеживаются.
- [x] `.env.example` описывает все нужные переменные; `.env` игнорируется.
- [x] README актуален.

## Заметки по реализации

- Структура settings: `base.py` (общее) → `dev.py`/`prod.py` импортируют base.
- Не коммитить реальные секреты. Сгенерировать новый `SECRET_KEY` (старый уже
  утёк в гит-историю — для учебного проекта достаточно заменить и не использовать
  его в prod).
- На Windows активация venv — `./.venv/Scripts/Activate.ps1`.

## Затрагиваемые файлы (ориентир)

- `wod_charlists/wod_charlists/settings.py` → `settings/{base,dev,prod}.py`
- `.gitignore`, `.env.example`, `requirements/*.txt`, `README.md`

## Тесты

- Ручной: запуск с dev и (симулированными) prod env; проверка `git status`.
- `python manage.py check` без ошибок.

## Definition of Done

Критерии приёмки выполнены, гит чист, секреты не в коде.

## Итоги реализации (2026-06-12)

- **Принято решение о физическом переносе**: `wod_charlists/` → `backend/`,
  внутренний пакет `wod_charlists/` → `config/` (целевая структура из
  [01-architecture.md](../01-architecture.md)). Сделано здесь, пока кода мало.
- Настройки: `backend/config/settings/{base,dev,prod}.py`; env читается через
  `os.environ` + минимальный загрузчик `.env` без внешних зависимостей
  (по умолчанию `config.settings.dev`; wsgi/asgi по умолчанию — prod).
- Зависимости: `backend/requirements/{base,dev,prod}.txt`, Django зафиксирован
  `>=5.2,<5.3`.
- `db.sqlite3` и `__pycache__` убраны из индекса; `.gitignore` дополнен.
- Проверено: `manage.py check` (dev и prod с env) и `manage.py test` зелёные;
  prod без `DJANGO_SECRET_KEY`/`DJANGO_ALLOWED_HOSTS` падает `ImproperlyConfigured`.
