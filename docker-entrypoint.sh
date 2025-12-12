#!/bin/bash
set -e

# Функция для логирования
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Запуск Avito Parser..."

# Проверяем наличие файла .env
if [ ! -f "/app/.env" ]; then
    log "ВНИМАНИЕ: Файл .env не найден. Создаем из примера..."
    if [ -f "/app/.env.example" ]; then
        cp /app/.env.example /app/.env
        log "Файл .env создан из .env.example"
    elif [ -f "/app/env.example" ]; then
        cp /app/env.example /app/.env
        log "Файл .env создан из env.example"
    else
        log "ОШИБКА: Файл env.example/.env.example не найден"
        exit 1
    fi
fi

# Проверяем переменную TARGET_URL
if [ -z "${TARGET_URL}" ]; then
    log "ВНИМАНИЕ: Переменная TARGET_URL не установлена"
fi

# Создаем необходимые директории
mkdir -p /app/database /app/logs /app/trash

# Проверяем доступность базы данных
log "Проверка доступности базы данных..."
python -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('/app/database/avito.db')
    conn.execute('SELECT 1')
    conn.close()
    print('База данных доступна')
except Exception as e:
    print(f'Ошибка подключения к базе данных: {e}')
    sys.exit(1)
"

# Запускаем основное приложение
log "Запуск парсера..."
exec python main.py

