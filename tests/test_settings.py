from __future__ import annotations

import os

import pytest

from config.settings import Settings


def test_settings_admin_ids_parsing_from_str(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TARGET_URL", "https://example.com")
    monkeypatch.setenv("ADMIN_IDS", "1, 2,3")
    s = Settings(_env_file=None)
    assert s.admin_ids == [1, 2, 3]


def test_settings_admin_ids_parsing_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TARGET_URL", "https://example.com")
    monkeypatch.delenv("ADMIN_IDS", raising=False)
    s = Settings(_env_file=None)
    assert s.admin_ids == []


