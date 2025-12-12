# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры для Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Копируем исходный код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p database logs trash

# Устанавливаем права на выполнение
RUN chmod +x main.py

# Создаем пользователя для запуска приложения (безопасность)
RUN useradd -m -u 1000 parser && chown -R parser:parser /app
USER parser

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Команда по умолчанию
CMD ["python", "main.py"]

