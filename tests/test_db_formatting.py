from __future__ import annotations

from database.avito_sqlite import AvitoSQLite


def test_format_item_message_minimal() -> None:
    msg = AvitoSQLite.format_item_message({"title": "Test"})
    assert "🏠 *Test*" in msg


def test_format_item_message_includes_fields() -> None:
    msg = AvitoSQLite.format_item_message(
        {
            "title": "Apt",
            "price": "100",
            "address": "Moscow",
            "bail": "10",
            "tax": "5",
            "services": "ЖКУ",
            "description": "x" * 300,
            "images": "a,b,c",
            "link": "https://example.com",
            "created_at": "2025-12-12T10:11:12+00:00",
        }
    )
    assert "💰 Цена: 100" in msg
    assert "📍 Адрес: Moscow" in msg
    assert "💳 Залог: 10" in msg
    assert "📊 Комиссия: 5" in msg
    assert "🔧 Услуги: ЖКУ" in msg
    assert "📝 Описание:" in msg
    assert "📸 Изображений: 3" in msg
    assert "[Ссылка на объявление](https://example.com)" in msg
    assert "⏰ Спаршено:" in msg


