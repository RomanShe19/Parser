from __future__ import annotations

from aiogram import Bot


async def send_markdown_chunks(
    bot: Bot,
    chat_id: int,
    text: str,
    *,
    chunk_size: int = 4000,
    disable_web_page_preview: bool = True,
) -> None:
    if len(text) <= chunk_size:
        await bot.send_message(
            chat_id,
            text,
            disable_web_page_preview=disable_web_page_preview,
        )
        return

    for i in range(0, len(text), chunk_size):
        await bot.send_message(
            chat_id,
            text[i : i + chunk_size],
            disable_web_page_preview=disable_web_page_preview,
        )


