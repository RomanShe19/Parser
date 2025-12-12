from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseParser(ABC):
    """Базовый класс для парсера"""
    
    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """
        Основной метод парсинга
        Returns:
            List[Dict[str, Any]]: Список спарсенных данных
        """
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Валидация полученных данных
        Args:
            data (Dict[str, Any]): Данные для валидации
        Returns:
            bool: Результат валидации
        """
        pass

class AvitoParser(BaseParser):
    """Парсер для Avito"""
    
    def __init__(self) -> None:
        self.base_url = "https://www.avito.ru"
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        Реализация парсинга для Avito
        Returns:
            List[Dict[str, Any]]: Список спарсенных данных
        """
        # TODO: Реализовать логику парсинга
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Валидация данных с Avito
        Args:
            data (Dict[str, Any]): Данные для валидации
        Returns:
            bool: Результат валидации
        """
        required_fields = ['title', 'price', 'url']
        return all(field in data for field in required_fields)

