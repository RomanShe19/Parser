import asyncio
from datetime import datetime
from pathlib import Path

import aiofiles
from core.antidetect_parser import AntiDetectParser
from core.processor import AvitoProcessor
from loguru import logger
from config.settings import Settings
from database.avito_sqlite import AvitoSQLite

async def process_content(content: str) -> None:
    """
    Обработка полученного контента и сохранение в БД
    """
    logger.info("Получен контент со страницы")
    
    # Сохраняем исходный HTML для отладки
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trash_dir = Path("trash")
    trash_dir.mkdir(parents=True, exist_ok=True)
    filename = trash_dir / f"page_{timestamp}.html"
    async with aiofiles.open(filename, "w", encoding="utf-8") as f:
        await f.write(content)
    logger.debug(f"Исходный HTML сохранен в: {filename}")
    
    # Обрабатываем HTML и сохраняем в БД
    settings = Settings()
    db = AvitoSQLite(settings.db_path)
    processor = AvitoProcessor(db=db)
    result = await processor.process_html(content, settings.target_url)
    
    if result:
        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)
        print(f"Найдено объявлений: {result['total_listings']}")
        print(f"Добавлено в БД: {result['added_to_db']}")
        print(f"Пропущено дублей: {result['duplicates_skipped']}")
        print("=" * 60)
    else:
        logger.error("Не удалось обработать страницу")
    
async def main() -> None:
    settings = Settings()
    
    logger.info(f"Начинаем парсинг URL: {settings.target_url}")
    
    # Инициализация парсера
    parser = AntiDetectParser(settings.target_url)
    
    try:
        # Получение контента
        content = await parser.parse()
        if content:
            # Обработка контента
            await process_content(content)
        else:
            logger.error("Не удалось получить контент")
    except Exception as e:
        logger.error(f"Произошла ошибка при парсинге: {e}")

if __name__ == "__main__":
    # Настройка логгера
    logger.add("logs/parser.log", rotation="1 day")
    asyncio.run(main())
