import asyncio
import aiohttp
import random
from typing import List, Optional, Set
from dataclasses import dataclass
from loguru import logger
import time

@dataclass
class ProxyInfo:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    success_count: int = 0
    fail_count: int = 0
    last_used: float = 0
    response_time: float = 0
    
    @property
    def url(self) -> str:
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0
    
    def mark_success(self, response_time: float = 0) -> None:
        self.success_count += 1
        self.last_used = time.time()
        self.response_time = response_time
    
    def mark_failure(self) -> None:
        self.fail_count += 1
        self.last_used = time.time()

class ProxyRotator:
    def __init__(self) -> None:
        self.proxies: List[ProxyInfo] = []
        self.current_index = 0
        self.failed_proxies: Set[str] = set()
        self.test_url = "http://httpbin.org/ip"
        
    def add_proxy(
        self,
        host: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        protocol: str = "http",
    ) -> None:
        """Добавить прокси в пул"""
        proxy = ProxyInfo(host, port, username, password, protocol)
        self.proxies.append(proxy)
        logger.info(f"Добавлен прокси: {proxy.url}")
    
    def add_free_proxies(self) -> None:
        """Добавить бесплатные прокси (для тестирования)"""
        # Это пример - в реальном проекте используйте проверенные прокси
        free_proxies = [
            ("proxy-server.com", 8080),
            ("free-proxy.cz", 3128),
            ("proxy.example.com", 8888),
        ]
        
        for host, port in free_proxies:
            self.add_proxy(host, port)
    
    async def test_proxy(self, proxy: ProxyInfo) -> bool:
        """Тестирование прокси на работоспособность"""
        try:
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    self.test_url,
                    proxy=proxy.url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                ) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        proxy.mark_success(response_time)
                        logger.info(f"Прокси {proxy.host}:{proxy.port} работает (время ответа: {response_time:.2f}с)")
                        return True
                    else:
                        proxy.mark_failure()
                        return False
        except Exception as e:
            logger.warning(f"Прокси {proxy.host}:{proxy.port} не работает: {e}")
            proxy.mark_failure()
            return False
    
    async def validate_proxies(self) -> None:
        """Проверить все прокси на работоспособность"""
        logger.info("Проверка прокси на работоспособность...")
        
        tasks = [self.test_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        working_proxies = []
        for proxy, result in zip(self.proxies, results):
            if result is True:
                working_proxies.append(proxy)
            else:
                self.failed_proxies.add(f"{proxy.host}:{proxy.port}")
        
        self.proxies = working_proxies
        logger.info(f"Работающих прокси: {len(self.proxies)}")
    
    def get_best_proxy(self) -> Optional[ProxyInfo]:
        """Получить лучший прокси по критериям успешности и времени отклика"""
        if not self.proxies:
            return None
        
        # Фильтруем недавно использованные прокси
        now = time.time()
        available_proxies = [
            p for p in self.proxies 
            if f"{p.host}:{p.port}" not in self.failed_proxies and (now - p.last_used) > 30
        ]
        
        if not available_proxies:
            available_proxies = [p for p in self.proxies if f"{p.host}:{p.port}" not in self.failed_proxies]
        
        if not available_proxies:
            # Если все прокси в черном списке, очищаем его
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        # Сортируем по успешности и времени отклика
        available_proxies.sort(
            key=lambda p: (p.success_rate, -p.response_time), 
            reverse=True
        )
        
        return available_proxies[0] if available_proxies else None
    
    def get_random_proxy(self) -> Optional[ProxyInfo]:
        """Получить случайный прокси"""
        if not self.proxies:
            return None
        
        available_proxies = [p for p in self.proxies if f"{p.host}:{p.port}" not in self.failed_proxies]
        if not available_proxies:
            self.failed_proxies.clear()
            available_proxies = self.proxies
        
        return random.choice(available_proxies) if available_proxies else None
    
    def mark_proxy_failed(self, proxy: ProxyInfo) -> None:
        """Отметить прокси как неработающий"""
        proxy.mark_failure()
        # Используем строковое представление для добавления в set
        proxy_key = f"{proxy.host}:{proxy.port}"
        self.failed_proxies.add(proxy_key)
        logger.warning(f"Прокси {proxy.host}:{proxy.port} помечен как неработающий")
    
    def mark_proxy_success(self, proxy: ProxyInfo, response_time: float = 0) -> None:
        """Отметить прокси как успешный"""
        proxy.mark_success(response_time)
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key in self.failed_proxies:
            self.failed_proxies.remove(proxy_key)

class ProxyConfig:
    """Конфигурация для различных типов прокси"""
    
    # Платные надежные прокси (примеры)
    DATACENTER_PROXIES = [
        # Добавьте ваши платные прокси здесь
        # ("proxy1.provider.com", 8080, "username", "password"),
    ]
    
    # Residential прокси (более дорогие, но лучше обходят блокировки)
    RESIDENTIAL_PROXIES = [
        # Добавьте residential прокси здесь
    ]
    
    # Бесплатные прокси (менее надежные)
    FREE_PROXIES = [
        # Список бесплатных прокси для тестирования
    ]

async def get_configured_proxy_rotator() -> ProxyRotator:
    """Создать и настроить ротатор прокси"""
    rotator = ProxyRotator()
    
    # Добавляем платные прокси
    for host, port, username, password in ProxyConfig.DATACENTER_PROXIES:
        rotator.add_proxy(host, port, username, password)
    
    # Добавляем residential прокси
    for host, port, username, password in ProxyConfig.RESIDENTIAL_PROXIES:
        rotator.add_proxy(host, port, username, password)
    
    # Если нет платных прокси, добавляем бесплатные для тестирования
    if not rotator.proxies:
        logger.warning("Не найдены платные прокси, используем бесплатные для тестирования")
        rotator.add_free_proxies()
    
    # Проверяем все прокси
    await rotator.validate_proxies()
    
    return rotator