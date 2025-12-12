import re
from typing import Optional
from datetime import datetime

def clean_text(text: Optional[str]) -> str:
    """
    Очистка текста от лишних пробелов и специальных символов
    Args:
        text (str): Исходный текст
    Returns:
        str: Очищенный текст
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())

def parse_price(price_str: str) -> Optional[float]:
    """
    Преобразование строки с ценой в число
    Args:
        price_str (str): Строка с ценой
    Returns:
        Optional[float]: Цена в виде числа или None, если преобразование невозможно
    """
    try:
        # Удаляем все нечисловые символы, кроме точки и запятой
        clean_price = re.sub(r"[^\d.,]", "", price_str).strip()
        if not clean_price:
            return None

        # Если есть и запятая, и точка — считаем запятую разделителем тысяч (1,234.56)
        if "," in clean_price and "." in clean_price:
            clean_price = clean_price.replace(",", "")
        else:
            # Иначе запятая — десятичный разделитель (1234,56)
            clean_price = clean_price.replace(",", ".")

        return float(clean_price)
    except (ValueError, TypeError):
        return None

def format_date(date_str: str, input_format: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Преобразование строки с датой в объект datetime
    Args:
        date_str (str): Строка с датой
        input_format (str): Формат входной даты
    Returns:
        Optional[datetime]: Объект datetime или None, если преобразование невозможно
    """
    try:
        return datetime.strptime(date_str, input_format)
    except (ValueError, TypeError):
        return None

