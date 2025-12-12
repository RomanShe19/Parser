from __future__ import annotations

from typing import Optional

from core.antidetect_parser import AntiDetectParser
from core.processor import AvitoProcessor
from database.avito_sqlite import AvitoSQLite


async def run_parse_and_store(target_url: str, db: AvitoSQLite) -> Optional[dict[str, int]]:
    """
    Запускает парсер, извлекает HTML и сохраняет результаты в БД.
    Возвращает статистику добавления.
    """
    parser = AntiDetectParser(target_url)
    content = await parser.parse()
    if not content:
        return None

    processor = AvitoProcessor(db=db)
    return await processor.process_html(content, target_url)


