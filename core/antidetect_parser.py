import asyncio
from typing import Any, Dict, Optional
from curl_cffi import requests
from playwright.async_api import async_playwright
import json
from pathlib import Path
from loguru import logger
import random
import time
from services.user_agent_rotator import UserAgentRotator

class AntiDetectParser:
    def __init__(self, url: str) -> None:
        self.url = url
        self.cookies_file = Path("cookies.json")
        self.ua_rotator = UserAgentRotator()
        self.current_device_type = "desktop"
        self.retry_count = 0
        self.max_retries = 5
        self.failed_attempts = 0
        
    def _load_cookies_sync(self) -> Dict[str, str]:
        """Загрузка сохраненных cookies"""
        if self.cookies_file.exists():
            return json.loads(self.cookies_file.read_text(encoding="utf-8"))
        return {}
        
    def _save_cookies_sync(self, cookies: Dict[str, str]) -> None:
        """Сохранение cookies в файл"""
        self.cookies_file.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
    
    def _rotate_settings(self) -> None:
        """Ротация настроек парсера"""
        # Меняем тип устройства при неудачах
        if self.failed_attempts > 2:
            device_types = ["desktop", "mobile", "tablet"]
            weights = [0.6, 0.3, 0.1] if self.failed_attempts < 5 else [0.3, 0.5, 0.2]
            self.current_device_type = random.choices(device_types, weights=weights)[0]
            logger.info(f"Переключение на тип устройства: {self.current_device_type}")
        
        # Очищаем cookies при множественных неудачах
        if self.failed_attempts > 3:
            logger.info("Очистка cookies...")
            if self.cookies_file.exists():
                self.cookies_file.unlink()
    
    def _adapt_to_failure(self, error_msg: str) -> str:
        """Адаптация стратегии в зависимости от типа ошибки"""
        self.failed_attempts += 1
        
        if "timeout" in error_msg.lower():
            logger.info("Обнаружен таймаут - увеличиваем задержки")
            return "increase_delays"
        elif "captcha" in error_msg.lower() or "доступ ограничен" in error_msg.lower():
            logger.info("Обнаружена капча - меняем стратегию")
            return "change_strategy"
        elif "connection" in error_msg.lower():
            logger.info("Проблемы с соединением - меняем настройки")
            return "change_settings"
        else:
            return "default"

    async def _get_with_curl(self) -> Optional[str]:
        """Попытка получить страницу через curl-cffi"""
        def _do_request() -> Optional[str]:
            # Получаем динамические заголовки
            headers = self.ua_rotator.get_headers(self.current_device_type)

            request_params: Dict[str, Any] = {
                "url": self.url,
                "headers": headers,
                "cookies": self._load_cookies_sync(),
                "impersonate": "chrome110",
                "timeout": 30 + (self.failed_attempts * 5),  # увеличиваем таймаут при неудачах
            }

            start_time = time.time()
            response = requests.get(**request_params)
            response_time = time.time() - start_time

            if response.status_code == 200:
                # Сохраняем cookies если запрос успешный
                self._save_cookies_sync(dict(response.cookies))
                logger.info(f"curl-cffi успешно получил страницу (время: {response_time:.2f}с)")
                return response.text

            logger.warning(f"curl-cffi вернул статус {response.status_code}")
            return None

        try:
            return await asyncio.to_thread(_do_request)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка при запросе через curl-cffi: {error_msg}")
            self._adapt_to_failure(error_msg)
            return None

    async def _emulate_human_behavior(self, page: Any) -> None:
        """Эмуляция человеческого поведения"""
        # Случайные движения мыши
        for _ in range(random.randint(3, 6)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

        # Случайные скроллы
        for _ in range(random.randint(2, 4)):
            await page.evaluate(f"window.scrollBy(0, {random.randint(300, 700)})")
            await asyncio.sleep(random.uniform(0.5, 1.5))

        # Иногда делаем скролл наверх
        if random.random() > 0.7:
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(random.uniform(0.3, 0.7))

    async def _get_with_playwright(self) -> Optional[str]:
        """Получение страницы через playwright с обходом защиты"""
        try:
            # Получаем динамические настройки
            headers = self.ua_rotator.get_headers(self.current_device_type)
            browser_args = self.ua_rotator.get_browser_args(self.current_device_type)
            context_params = self.ua_rotator.get_browser_context_params(self.current_device_type)
            
            async with async_playwright() as p:
                # Запускаем браузер с динамическими параметрами
                browser = await p.chromium.launch(
                    headless=True,
                    args=browser_args
                )
                
                # Создаем контекст с динамическими параметрами
                context_config = {
                    **context_params,
                    'java_script_enabled': True,
                    'ignore_https_errors': True,
                    'locale': 'ru-RU',
                    'timezone_id': 'Europe/Moscow',
                    'geolocation': {'latitude': 55.7558, 'longitude': 37.6173},
                    'permissions': ['geolocation']
                }
                
                context = await browser.new_context(**context_config)

                # Переопределяем некоторые свойства браузера для обхода обнаружения
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});
                """)
                
                # Загружаем сохраненные cookies (не блокируем event loop)
                cookies = await asyncio.to_thread(self._load_cookies_sync)
                if cookies:
                    await context.add_cookies([
                        {"name": k, "value": v, "domain": ".avito.ru", "path": "/"}
                        for k, v in cookies.items()
                    ])
                
                # Открываем страницу
                page = await context.new_page()
                
                # Устанавливаем перехватчики для блокировки ненужных ресурсов
                async def _route_handler(route: Any) -> None:
                    url = route.request.url.lower()
                    if any(ext in url for ext in (".png", ".jpg", ".jpeg", ".gif", ".css", ".woff", ".woff2")):
                        await route.abort()
                        return
                    await route.continue_()

                await page.route("**/*", _route_handler)
                
                # Эмулируем действия пользователя
                await page.set_extra_http_headers(headers)
                
                # Добавляем случайную задержку перед загрузкой
                await asyncio.sleep(random.uniform(1, 3))
                
                await page.goto(self.url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(2, 4))  # Случайная пауза
                
                # Эмулируем поведение человека
                await self._emulate_human_behavior(page)
                
                # Проверяем наличие капчи
                if await page.locator("text=Доступ ограничен").count() > 0:
                    logger.warning("Обнаружена капча")
                    # Делаем более длительную паузу
                    await asyncio.sleep(random.uniform(3, 5))
                    # Пробуем обойти
                    await page.reload(wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(2, 4))
                    # Снова эмулируем поведение человека
                    await self._emulate_human_behavior(page)
                
                # Ждем появления контента с увеличенным таймаутом
                content_selectors = [
                    'div[data-marker="item"]',
                    'div[class*="items-items"]',
                    'div[class*="items-list"]',
                    'div[data-marker="catalog-serp"]'
                ]
                
                content_found = False
                for selector in content_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=30000)
                        content_found = True
                        logger.info(f"Найден контент по селектору: {selector}")
                        break
                    except:
                        continue

                if not content_found:
                    logger.warning("Не найдены объявления по стандартным селекторам")
                    # Делаем дополнительную попытку после паузы
                    await asyncio.sleep(random.uniform(3, 5))
                    await self._emulate_human_behavior(page)
                    
                    # Проверяем наличие любого контента на странице
                    page_content = await page.content()
                    if "item-title" in page_content or "items-items" in page_content:
                        content_found = True
                        logger.info("Найден контент в HTML")
                    
                if not content_found:
                    raise Exception("Не удалось найти контент на странице")
                
                # Сохраняем cookies
                new_cookies = await context.cookies()
                await asyncio.to_thread(
                    self._save_cookies_sync,
                    {c["name"]: c["value"] for c in new_cookies},
                )
                
                # Получаем контент
                content = await page.content()
                
                await browser.close()
                return content
                
        except Exception as e:
            logger.error(f"Ошибка при запросе через playwright: {e}")
            return None

    async def parse(self) -> Optional[str]:
        """
        Основной метод парсинга с умной логикой повторных попыток
        и динамической адаптацией стратегии
        """
        self.retry_count = 0
        self.failed_attempts = 0
        
        while self.retry_count < self.max_retries:
            try:
                logger.info(f"Попытка парсинга {self.retry_count + 1}/{self.max_retries}")
                
                # Ротация настроек при неудачах
                if self.retry_count > 0:
                    self._rotate_settings()
                    # Увеличиваем задержку между попытками
                    delay = random.uniform(3, 8) + (self.retry_count * 2)
                    logger.info(f"Задержка перед попыткой: {delay:.1f}с")
                    await asyncio.sleep(delay)
                
                # Стратегия выбора метода парсинга
                use_playwright_first = (
                    self.retry_count > 1 or 
                    self.current_device_type == "mobile" or
                    self.failed_attempts > 3
                )
                
                content = None
                
                if use_playwright_first:
                    logger.info("Начинаем с Playwright")
                    content = await self._get_with_playwright()
                    
                    if not content or "Доступ ограничен" in content:
                        logger.info("Playwright не сработал, пробуем curl-cffi")
                        content = await self._get_with_curl()
                else:
                    logger.info("Начинаем с curl-cffi")
                    content = await self._get_with_curl()
                    
                    if not content or "Доступ ограничен" in content:
                        logger.info("curl-cffi не сработал, пробуем Playwright")
                        content = await self._get_with_playwright()
                
                # Проверяем успешность
                if content and "Доступ ограничен" not in content and len(content) > 1000:
                    logger.info("Парсинг успешно завершен!")
                    return content
                else:
                    logger.warning(f"Попытка {self.retry_count + 1} неудачна")
                    self.failed_attempts += 1
                
            except Exception as e:
                logger.error(f"Ошибка в попытке {self.retry_count + 1}: {e}")
                self._adapt_to_failure(str(e))
            
            self.retry_count += 1
        
        logger.error(f"Все {self.max_retries} попыток парсинга исчерпаны")
        return None