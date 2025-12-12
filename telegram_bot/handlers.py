from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.settings import Settings
from database.avito_sqlite import AvitoSQLite
from telegram_bot.filters import AdminOnly
from telegram_bot.keyboards import (
    get_confirmation_keyboard,
    get_items_per_page_keyboard,
    get_journal_keyboard,
    get_main_keyboard,
    get_search_keyboard,
    get_settings_keyboard,
)
from telegram_bot.services.parser_service import run_parse_and_store
from telegram_bot.states import SearchStates
from telegram_bot.utils import send_markdown_chunks


def build_router(settings: Settings) -> Router:
    router = Router(name="main")
    admin_filter = AdminOnly(set(settings.admin_ids))

    @router.message(F.text == "/start", admin_filter)
    async def start_handler(message: Message) -> None:
        welcome_text = (
            "🤖 *Добро пожаловать в бот управления парсером!*\n\n"
            "Выберите действие из меню ниже:"
        )
        await message.answer(welcome_text, reply_markup=get_main_keyboard())

    @router.message(F.text == "/start")
    async def start_denied(message: Message) -> None:
        await message.answer("⛔️ У вас нет доступа к этому боту.")

    @router.message(F.text == "ℹ️ Помощь", admin_filter)
    async def help_handler(message: Message) -> None:
        help_text = (
            "🤖 *Помощь*\n\n"
            "• 🔄 *Запустить парсер* — запуск парсинга\n"
            "• 📋 *Журнал* — последние объекты (с пагинацией)\n"
            "• 📊 *Статистика* — статистика БД\n"
            "• ⚙️ *Настройки* — настройки бота\n"
        )
        await message.answer(help_text, reply_markup=get_main_keyboard())

    @router.message(F.text == "📊 Статистика", admin_filter)
    async def stats_handler(message: Message, db: AvitoSQLite) -> None:
        stats = await db.get_statistics()
        stats_text = (
            "📊 *Статистика парсинга*\n\n"
            f"• Всего объектов: {stats.total_items}\n"
            f"• Добавлено сегодня: {stats.today_items}\n"
            f"• За последние 7 дней: {stats.week_items}\n\n"
            f"🕐 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        await message.answer(stats_text, reply_markup=get_main_keyboard())

    @router.message(F.text == "⚙️ Настройки", admin_filter)
    async def settings_handler(message: Message, runtime: dict[str, Any]) -> None:
        items_per_page = int(runtime["items_per_page"])
        settings_text = (
            "⚙️ *Настройки бота*\n\n"
            f"📊 Элементов на странице: {items_per_page}\n\n"
            "Выберите настройку:"
        )
        await message.answer(settings_text, reply_markup=get_settings_keyboard())

    async def show_journal_page(bot: Bot, chat_id: int, page: int, *, db: AvitoSQLite, runtime: dict[str, Any]) -> None:
        items_per_page = int(runtime["items_per_page"])
        total_items = await db.get_total_items()
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        if total_items == 0:
            await bot.send_message(chat_id, "📭 *Журнал пуст*\n\nЗапустите парсер для получения данных.")
            return

        items = await db.get_latest_items(limit=items_per_page, offset=page * items_per_page)
        page_info = f"📋 *Страница {page + 1} из {total_pages}*\n📊 Показано {len(items)} из {total_items} объектов\n"

        await bot.send_message(chat_id, page_info, reply_markup=get_journal_keyboard(page, total_pages))

        for i, item in enumerate(items, 1):
            item_text = f"*{page * items_per_page + i}.* " + db.format_item_message(item)
            await send_markdown_chunks(bot, chat_id, item_text)

    @router.message(F.text == "📋 Журнал", admin_filter)
    async def journal_handler(message: Message, db: AvitoSQLite, runtime: dict[str, Any]) -> None:
        await show_journal_page(message.bot, message.chat.id, page=0, db=db, runtime=runtime)

    @router.callback_query(F.data.startswith("page:"), admin_filter)
    async def pagination_handler(call: CallbackQuery, db: AvitoSQLite, runtime: dict[str, Any]) -> None:
        if not call.data:
            return
        if call.data == "page:current":
            await call.answer("Текущая страница")
            return

        try:
            page = int(call.data.split(":", 1)[1])
        except ValueError:
            await call.answer("Некорректная страница")
            return

        await call.message.delete()
        await show_journal_page(call.bot, call.message.chat.id, page=page, db=db, runtime=runtime)
        await call.answer()

    @router.callback_query(F.data == "journal:refresh", admin_filter)
    async def refresh_journal(call: CallbackQuery, db: AvitoSQLite, runtime: dict[str, Any]) -> None:
        await call.message.delete()
        await show_journal_page(call.bot, call.message.chat.id, page=0, db=db, runtime=runtime)
        await call.answer("Журнал обновлен")

    @router.callback_query(F.data == "menu:main", admin_filter)
    async def menu_main(call: CallbackQuery) -> None:
        await call.message.delete()
        await call.message.answer("🏠 *Главное меню*\n\nВыберите действие:", reply_markup=get_main_keyboard())
        await call.answer()

    @router.callback_query(F.data == "menu:settings", admin_filter)
    async def menu_settings(call: CallbackQuery, runtime: dict[str, Any]) -> None:
        items_per_page = int(runtime["items_per_page"])
        await call.message.edit_text(
            f"⚙️ *Настройки бота*\n\n📊 Элементов на странице: {items_per_page}\n\nВыберите настройку:",
            reply_markup=get_settings_keyboard(),
        )
        await call.answer()

    @router.callback_query(F.data == "menu:journal", admin_filter)
    async def menu_journal(call: CallbackQuery, db: AvitoSQLite, runtime: dict[str, Any]) -> None:
        await call.message.delete()
        await show_journal_page(call.bot, call.message.chat.id, page=0, db=db, runtime=runtime)
        await call.answer()

    @router.callback_query(F.data == "settings:items_per_page", admin_filter)
    async def settings_items_per_page(call: CallbackQuery, settings: Settings) -> None:
        await call.message.edit_text(
            "📊 *Настройка количества элементов на странице*\n\nВыберите новое значение:",
            reply_markup=get_items_per_page_keyboard(max_items=settings.max_items_per_page),
        )
        await call.answer()

    @router.callback_query(F.data.startswith("settings:set_items:"), admin_filter)
    async def set_items_per_page(call: CallbackQuery, runtime: dict[str, Any]) -> None:
        try:
            items_count = int(call.data.split(":")[-1])  # type: ignore[union-attr]
        except ValueError:
            await call.answer("Некорректное значение")
            return
        runtime["items_per_page"] = items_count
        await call.message.edit_text(
            f"✅ *Настройка сохранена!*\n\nКоличество элементов на странице: {items_count}",
            reply_markup=get_settings_keyboard(),
        )
        await call.answer(f"Установлено: {items_count}")

    @router.callback_query(F.data == "settings:clear_db", admin_filter)
    async def clear_db_confirm(call: CallbackQuery) -> None:
        await call.message.edit_text(
            "⚠️ *ВНИМАНИЕ!*\n\nВы собираетесь очистить всю базу данных.\nЭто действие нельзя отменить!\n\nВы уверены?",
            reply_markup=get_confirmation_keyboard("clear_db"),
        )
        await call.answer()

    @router.callback_query(F.data == "confirm:clear_db", admin_filter)
    async def clear_db(call: CallbackQuery, db: AvitoSQLite) -> None:
        await db.clear_all_items()
        await call.message.edit_text(
            "✅ *База данных очищена!*\n\nВсе данные удалены.",
            reply_markup=get_settings_keyboard(),
        )
        await call.answer("База данных очищена")

    @router.callback_query(F.data == "confirm:cancel", admin_filter)
    async def cancel_action(call: CallbackQuery) -> None:
        await call.message.edit_text("❌ *Действие отменено*", reply_markup=get_settings_keyboard())
        await call.answer("Отменено")

    @router.callback_query(F.data == "search:start", admin_filter)
    async def start_search(call: CallbackQuery) -> None:
        await call.message.edit_text("🔍 *Поиск объектов*\n\nВыберите тип поиска:", reply_markup=get_search_keyboard())
        await call.answer()

    @router.callback_query(F.data.startswith("search:type:"), admin_filter)
    async def choose_search_type(call: CallbackQuery, state: FSMContext) -> None:
        search_type = call.data.split(":")[-1]  # type: ignore[union-attr]
        await state.update_data(search_type=search_type)
        await state.set_state(SearchStates.search_query)

        prompts = {
            "title": "Введите название для поиска:",
            "location": "Введите локацию для поиска:",
            "price": "Введите цену для поиска:",
            "area": "Введите площадь для поиска:",
        }
        await call.message.edit_text(f"🔍 *Поиск*\n\n{prompts.get(search_type, 'Введите запрос:')}")
        await call.answer()

    @router.message(SearchStates.search_query, admin_filter)
    async def handle_search_query(message: Message, state: FSMContext, db: AvitoSQLite) -> None:
        query = (message.text or "").strip()
        if not query:
            await message.answer("Введите непустой запрос.")
            return

        results = await db.search_items(query, limit=10)
        if not results:
            await message.answer(f"❌ По запросу '{query}' ничего не найдено.", reply_markup=get_main_keyboard())
            await state.clear()
            return

        await message.answer(
            f"🔍 *Результаты поиска по запросу: '{query}'*\n\nНайдено: {len(results)} объектов\n"
        )
        for i, item in enumerate(results, 1):
            item_text = f"*{i}.* " + db.format_item_message(item)
            await send_markdown_chunks(message.bot, message.chat.id, item_text)

        await state.clear()

    @router.message(F.text == "🔄 Запустить парсер", admin_filter)
    async def start_parser(message: Message, db: AvitoSQLite, settings: Settings) -> None:
        status = await message.answer("🔄 Запускаю парсер...\n⏳ Это может занять несколько минут.")

        async def _job() -> None:
            try:
                result = await run_parse_and_store(settings.target_url, db=db)
                stats_after = await db.get_statistics()

                if not result:
                    await status.edit_text(
                        "❌ *Ошибка при парсинге!*\n\n"
                        "Не удалось получить данные с сайта.\n"
                        "Возможные причины:\n"
                        "• Проблемы с интернет-соединением\n"
                        "• Блокировка IP адреса\n"
                        "• Изменения в структуре сайта"
                    )
                    return

                await status.edit_text(
                    "✅ *Парсинг успешно завершен!*\n\n"
                    f"📊 *Результаты парсинга:*\n"
                    f"• Найдено объявлений: {result.get('total_listings', 0)}\n"
                    f"• Добавлено в БД: {result.get('added_to_db', 0)}\n"
                    f"• Пропущено дублей: {result.get('duplicates_skipped', 0)}\n\n"
                    f"📈 *Общая статистика:*\n"
                    f"• Всего объектов: {stats_after.total_items}\n"
                    f"• Добавлено сегодня: {stats_after.today_items}\n"
                    f"• За последние 7 дней: {stats_after.week_items}\n\n"
                    "Используйте кнопку '📋 Журнал' для просмотра результатов."
                )
            except Exception as e:
                await status.edit_text(f"❌ *Ошибка при запуске парсера!*\n\nОшибка: {e}")

        asyncio.create_task(_job())

    @router.message(admin_filter)
    async def unknown(message: Message) -> None:
        await message.answer("❓ Неизвестная команда. Используйте меню для навигации.", reply_markup=get_main_keyboard())

    return router


