import pytest
from core.parser import AvitoParser
from utils.helpers import clean_text, parse_price

def test_clean_text() -> None:
    """Тест функции очистки текста"""
    assert clean_text("  test  text  ") == "test text"
    assert clean_text("") == ""
    assert clean_text(None) == ""

def test_parse_price() -> None:
    """Тест функции парсинга цены"""
    assert parse_price("1 234,56 ₽") == 1234.56
    assert parse_price("1,234.56") == 1234.56
    assert parse_price("invalid") is None

@pytest.fixture
def parser() -> AvitoParser:
    """Фикстура для создания экземпляра парсера"""
    return AvitoParser()

def test_parser_validation(parser: AvitoParser) -> None:
    """Тест валидации данных парсера"""
    valid_data = {
        'title': 'Test Item',
        'price': 1000.0,
        'url': 'https://example.com'
    }
    assert parser.validate_data(valid_data) is True
    
    invalid_data = {
        'title': 'Test Item',
        'price': 1000.0
        # url отсутствует
    }
    assert parser.validate_data(invalid_data) is False

