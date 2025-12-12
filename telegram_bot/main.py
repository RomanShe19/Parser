from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import Settings
from database.avito_sqlite import AvitoSQLite
from telegram_bot.handlers import build_router


async def main() -> None:
    settings = Settings()
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен (см. env.example)")
    if not settings.admin_ids:
        raise ValueError("ADMIN_IDS не установлен (см. env.example)")

    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher(storage=MemoryStorage())

    db = AvitoSQLite(settings.db_path)
    runtime = {"items_per_page": settings.items_per_page}

    # Dependency injection для хендлеров (по именам параметров)
    dp["db"] = db
    dp["settings"] = settings
    dp["runtime"] = runtime

    dp.include_router(build_router(settings))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
