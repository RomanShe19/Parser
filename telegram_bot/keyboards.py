from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота (reply keyboard)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Запустить парсер"), KeyboardButton(text="📋 Журнал")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def get_journal_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура для журнала с пагинацией."""
    nav_buttons: list[InlineKeyboardButton] = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⏮️", callback_data="page:0"))
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page:{page - 1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="page:current"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page:{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(text="⏭️", callback_data=f"page:{total_pages - 1}"))

    keyboard: list[list[InlineKeyboardButton]] = [
        nav_buttons,
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="journal:refresh"),
            InlineKeyboardButton(text="🔍 Поиск", callback_data="search:start"),
        ],
        [
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Элементов на странице", callback_data="settings:items_per_page"),
                InlineKeyboardButton(text="🗑️ Очистить БД", callback_data="settings:clear_db"),
            ],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")],
        ]
    )


def get_items_per_page_keyboard(max_items: int = 10) -> InlineKeyboardMarkup:
    """Клавиатура выбора количества элементов на странице."""
    max_items = max(1, min(20, int(max_items)))
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"settings:set_items:{i}") for i in range(1, max_items + 1)
    ]

    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(buttons), 3):
        rows.append(buttons[i : i + 3])
    rows.append([InlineKeyboardButton(text="🔙 Настройки", callback_data="menu:settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_search_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа поиска."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 По названию", callback_data="search:type:title"),
                InlineKeyboardButton(text="📍 По локации", callback_data="search:type:location"),
            ],
            [
                InlineKeyboardButton(text="💰 По цене", callback_data="search:type:price"),
                InlineKeyboardButton(text="📐 По площади", callback_data="search:type:area"),
            ],
            [InlineKeyboardButton(text="🔙 Журнал", callback_data="menu:journal")],
        ]
    )


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="confirm:cancel"),
            ]
        ]
    )
