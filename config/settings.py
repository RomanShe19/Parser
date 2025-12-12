from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Единый конфиг проекта (парсер + Telegram-бот).

    Читается из переменных окружения и (опционально) из .env файла в корне проекта.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Parser
    target_url: str = Field(..., alias="TARGET_URL")

    # Storage
    db_path: str = Field(default="database/avito.db", alias="DB_PATH")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Telegram bot
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    # Важно: pydantic-settings пытается парсить List[...] из ENV как JSON.
    # Чтобы поддерживать привычный формат "1,2,3", держим сырой CSV-строкой и парсим сами.
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")
    items_per_page: int = Field(default=5, alias="ITEMS_PER_PAGE")
    max_items_per_page: int = Field(default=20, alias="MAX_ITEMS_PER_PAGE")

    @property
    def admin_ids(self) -> List[int]:
        raw = (self.admin_ids_raw or "").strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        ids: List[int] = []
        for p in parts:
            try:
                ids.append(int(p))
            except ValueError:
                continue
        return ids


