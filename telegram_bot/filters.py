from __future__ import annotations

from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class AdminOnly(BaseFilter):
    def __init__(self, admin_ids: set[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, event: Message | CallbackQuery, **data: Any) -> bool:
        user = getattr(event, "from_user", None)
        if user is None:
            return False
        return int(user.id) in self.admin_ids


