# Docker деплой Avito Parser

## Предварительные требования

### Установка Docker на Windows

1. **Скачайте Docker Desktop:**
   - Перейдите на https://www.docker.com/products/docker-desktop/
   - Скачайте Docker Desktop for Windows

2. **Установите Docker Desktop:**
   - Запустите установщик
   - Следуйте инструкциям мастера установки
   - Перезагрузите компьютер при необходимости

3. **Проверьте установку:**
```powershell
docker --version
docker-compose --version
```

### Альтернативные способы запуска (без Docker)

Если Docker недоступен, используйте обычный Python:

1. **Активируйте виртуальное окружение:**
```powershell
.\.venv\Scripts\Activate.ps1
```

2. **Создайте .env файл:**
```powershell
echo "TARGET_URL=https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok" > .env
```

3. **Запустите парсер:**
```powershell
python main.py
```

## Быстрый запуск с Docker

1. **Создайте файл .env с настройками:**
```bash
TARGET_URL=https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
LOG_LEVEL=INFO
TELEGRAM_BOT_TOKEN=PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE
ADMIN_IDS=123456789,987654321
```

2. **Соберите и запустите контейнер:**
```bash
docker-compose up --build
```

3. **Запуск в фоновом режиме:**
```bash
docker-compose up -d --build
```

## Управление контейнером

### Просмотр логов
```bash
docker-compose logs -f avito-parser
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Вход в контейнер для отладки
```bash
docker-compose exec avito-parser bash
```

## Структура томов

- `./database` - База данных SQLite (сохраняется между перезапусками)
- `./logs` - Логи приложения
- `./trash` - Временные HTML файлы
- `./.env` - Переменные окружения

## Мониторинг

### Проверка статуса контейнера
```bash
docker-compose ps
```

### Проверка использования ресурсов
```bash
docker stats avito-parser
```

### Проверка здоровья
```bash
docker-compose exec avito-parser python -c "import sqlite3; print('DB OK')"
```

## Настройка переменных окружения

Создайте файл `.env` со следующими переменными:

```env
# Обязательные
TARGET_URL=https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok
TELEGRAM_BOT_TOKEN=PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE
ADMIN_IDS=123456789,987654321

# Опциональные
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
LOG_LEVEL=INFO
PARSER_DELAY=2
DB_PATH=database/avito.db
ITEMS_PER_PAGE=5
```

## Решение проблем

### Контейнер не запускается
```bash
docker-compose logs avito-parser
```

### База данных недоступна
```bash
# Проверьте права доступа к папке database
ls -la database/
```

### Высокое потребление памяти
```bash
# Настройте лимиты в docker-compose.yml
```

## Обновление

1. Остановите контейнер:
```bash
docker-compose down
```

2. Обновите код и пересоберите:
```bash
git pull
docker-compose build --no-cache
```

3. Запустите:
```bash
docker-compose up -d
```
