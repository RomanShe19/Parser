from __future__ import annotations

from datetime import datetime

from utils.helpers import clean_text, format_date, parse_price


def test_clean_text_basic() -> None:
    assert clean_text("  test  text  ") == "test text"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_parse_price_ru_format() -> None:
    assert parse_price("1 234,56 ₽") == 1234.56
    assert parse_price("12 345 ₽") == 12345.0


def test_parse_price_us_format() -> None:
    assert parse_price("1,234.56") == 1234.56
    assert parse_price("$9,001.00") == 9001.0


def test_parse_price_invalid() -> None:
    assert parse_price("invalid") is None
    assert parse_price("") is None


def test_format_date_default_format() -> None:
    assert format_date("2025-12-12") == datetime(2025, 12, 12)


def test_format_date_custom_format() -> None:
    assert format_date("12.12.2025", input_format="%d.%m.%Y") == datetime(2025, 12, 12)
    assert format_date("not-a-date", input_format="%d.%m.%Y") is None


