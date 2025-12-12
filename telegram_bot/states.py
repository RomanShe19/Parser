from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    search_query = State()
    search_type = State()


