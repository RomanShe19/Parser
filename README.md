# Parser + Telegram Bot

Проект-портфолио: **асинхронный парсер сайта объявлений** (обход антибот-защиты через `curl-cffi`/`playwright`) + **Telegram-бот** для управления парсингом и просмотра результатов (журнал/поиск/статистика).

> Важно: используйте проект в рамках правил Avito и законодательства вашей страны.


## Стек

- **Python 3.11**
- **Парсинг/антибот**: `playwright`, `curl-cffi`, `beautifulsoup4`
- **Telegram**: `aiogram 3.x`
- **БД**: SQLite (`aiosqlite`)
- **Логи**: `loguru`
- **Docker**: Dockerfile + docker-compose

## Структура проекта (кратко)

```
config/
  settings.py            # единый Settings через env/.env
core/
  antidetect_parser.py   # получение HTML (playwright/curl-cffi)
  processor.py           # извлечение объявлений + сохранение в БД
database/
  avito_sqlite.py        # async-репозиторий SQLite
telegram_bot/
  main.py                # aiogram entrypoint
  handlers.py            # handlers/router
  keyboards.py           # клавиатуры
  services/              # сервисы (запуск парсера)
  filters.py             # AdminOnly фильтр
utils/
  helpers.py             # утилиты (тесты)
main.py                  # запуск парсера
```

## Быстрый старт (локально)

### 1) Установка

```bash
python -m venv .venv
```

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2) Конфигурация (.env)

Из-за ограничений среды в репозитории лежит файл `env.example`.
Скопируйте его в `.env` и заполните:

```bash
cp env.example .env
```

### 3) Запуск парсера

```bash
python main.py
```

### 4) Запуск Telegram-бота

```bash
python telegram_bot/main.py
```

## Запуск через Docker

См. `README-Docker.md`.

## Тесты

```bash
pytest -q
```

## Безопасность

- Секреты **не хардкодятся** — используйте `.env`.
- Файлы данных (`database/*.db`, `cookies.json`, `logs/`, `trash/`) исключены через `.gitignore`.
