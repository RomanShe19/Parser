from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiosqlite


ApartmentDict = Dict[str, Any]


@dataclass(frozen=True)
class Stats:
    total_items: int
    today_items: int
    week_items: int


class AvitoSQLite:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def ensure_schema(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS apartments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    price TEXT,
                    bail TEXT,
                    tax TEXT,
                    services TEXT,
                    address TEXT,
                    description TEXT,
                    images TEXT,
                    link TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apartment_id INTEGER,
                    image_url TEXT,
                    FOREIGN KEY (apartment_id) REFERENCES apartments (id)
                )
                """
            )
            await db.commit()

    async def clear_all_items(self) -> None:
        await self.ensure_schema()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM apartments")
            await db.execute("DELETE FROM images")
            await db.commit()

    async def save_apartments(self, apartments: List[ApartmentDict]) -> int:
        """
        Сохраняет объявления в БД.

        Возвращает количество добавленных записей (INSERTed).
        """
        await self.ensure_schema()
        inserted = 0
        async with aiosqlite.connect(self.db_path) as db:
            for a in apartments:
                cur = await db.execute(
                    """
                    INSERT OR IGNORE INTO apartments
                    (title, price, bail, tax, services, address, description, images, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        a.get("title", ""),
                        a.get("price", ""),
                        a.get("bail", ""),
                        a.get("tax", ""),
                        a.get("services", ""),
                        a.get("address", ""),
                        a.get("description", ""),
                        a.get("images", ""),
                        a.get("link", ""),
                    ),
                )

                if cur.rowcount and cur.rowcount > 0:
                    inserted += 1
                    apartment_id = cur.lastrowid
                else:
                    # запись уже существовала — достаем id по link
                    row = await db.execute_fetchone(
                        "SELECT id FROM apartments WHERE link = ?",
                        (a.get("link", ""),),
                    )
                    apartment_id = int(row[0]) if row else None

                images_list = a.get("images_list") or []
                if apartment_id and images_list:
                    for img_url in images_list:
                        await db.execute(
                            """
                            INSERT OR IGNORE INTO images (apartment_id, image_url)
                            VALUES (?, ?)
                            """,
                            (apartment_id, img_url),
                        )

            await db.commit()
        return inserted

    async def get_total_items(self) -> int:
        await self.ensure_schema()
        async with aiosqlite.connect(self.db_path) as db:
            row = await db.execute_fetchone("SELECT COUNT(*) FROM apartments")
            return int(row[0]) if row else 0

    async def get_latest_items(self, limit: int = 10, offset: int = 0) -> List[ApartmentDict]:
        await self.ensure_schema()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT * FROM apartments
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def search_items(self, query: str, limit: int = 10) -> List[ApartmentDict]:
        await self.ensure_schema()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT * FROM apartments
                WHERE title LIKE ? OR description LIKE ? OR address LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def get_statistics(self) -> Stats:
        await self.ensure_schema()
        async with aiosqlite.connect(self.db_path) as db:
            total_row = await db.execute_fetchone("SELECT COUNT(*) FROM apartments")
            today_row = await db.execute_fetchone(
                """
                SELECT COUNT(*) FROM apartments
                WHERE DATE(created_at) = DATE('now')
                """
            )
            week_row = await db.execute_fetchone(
                """
                SELECT COUNT(*) FROM apartments
                WHERE created_at >= datetime('now', '-7 days')
                """
            )
            return Stats(
                total_items=int(total_row[0]) if total_row else 0,
                today_items=int(today_row[0]) if today_row else 0,
                week_items=int(week_row[0]) if week_row else 0,
            )

    @staticmethod
    def format_item_message(item: ApartmentDict) -> str:
        title = item.get("title") or ""
        message = f"🏠 *{title}*\n\n"

        price = item.get("price")
        if price:
            message += f"💰 Цена: {price}\n"

        address = item.get("address")
        if address:
            message += f"📍 Адрес: {address}\n"

        bail = item.get("bail")
        if bail:
            message += f"💳 Залог: {bail}\n"

        tax = item.get("tax")
        if tax:
            message += f"📊 Комиссия: {tax}\n"

        services = item.get("services")
        if services:
            message += f"🔧 Услуги: {services}\n"

        description = item.get("description")
        if description:
            desc = description[:200] + "..." if len(description) > 200 else description
            message += f"\n📝 Описание: {desc}\n"

        images = item.get("images") or ""
        if images:
            images_count = len([x for x in images.split(",") if x.strip()])
            if images_count > 0:
                message += f"📸 Изображений: {images_count}\n"

        link = item.get("link")
        if link:
            message += f"\n🔗 [Ссылка на объявление]({link})\n"

        created_at = item.get("created_at")
        if created_at:
            try:
                created_dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                message += f"\n⏰ Спаршено: {created_dt.strftime('%d.%m.%Y %H:%M')}"
            except Exception:
                message += f"\n⏰ Спаршено: {created_at}"

        return message


