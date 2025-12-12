from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional
from loguru import logger

from database.avito_sqlite import AvitoSQLite

class AvitoProcessor:
    def __init__(self, db: AvitoSQLite) -> None:
        """Инициализация процессора (извлечение + сохранение в SQLite)"""
        self.db = db

    async def process_html(self, html: str, original_url: str) -> Optional[Dict[str, int]]:
        """Обработка HTML страницы и извлечение данных"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Поиск всех объявлений на странице
            items = soup.find_all('div', class_='iva-item-content-fRmzq')
            if not items:
                logger.warning("Не найдены объявления на странице")
                return None
            
            results: List[Dict[str, Any]] = []
            
            for item in items:
                try:
                    # Извлечение данных из каждого объявления
                    link_elem = item.find('a', {'itemProp': 'url'}) or item.find('a', class_='iva-item-sliderLink-kra4e')
                    
                    if not link_elem:
                        continue
                        
                    link = 'https://www.avito.ru' + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                    
                    # Ищем заголовок - приоритет data-marker="item-title"
                    title_link = item.find('a', {'data-marker': 'item-title'})
                    if title_link:
                        title = self._get_text(title_link)
                    else:
                        # Если не найден, ищем в других местах
                        title_elem = (item.find('h3', {'itemprop': 'name'}) or 
                                     item.find('h3') or
                                     item.find('div', class_='iva-item-titleStep'))
                        title = self._get_text(title_elem)
                    
                    price_elem = item.find('span', {'data-marker': 'item-price'})
                    
                    # Находим блок с описанием
                    desc_elem = item.find('div', {'class': 'iva-item-descriptionStep'})
                    
                    # Находим блок с адресом  
                    address_elem = (item.find('div', {'class': 'geo-root'}) or 
                                  item.find('span', {'class': 'geo-address'}) or
                                  item.find('div', class_='geo-georeferences'))
                    
                    # Находим блок с ценой
                    price_block = (item.find('div', {'class': 'price-root'}) or 
                                 item.find('span', {'data-marker': 'item-price'}) or
                                 item.find('div', class_='price-price'))
                    
                    # Получаем изображения и конвертируем в строку
                    images_list = self._get_images(item)
                    images_str = ', '.join(images_list) if images_list else ''
                    
                    data = {
                        'title': title,
                        'price': self._get_text(price_elem) or self._get_text(price_block),
                        'bail': self._get_text(item.find(text=lambda t: t and 'Залог' in t)),
                        'tax': self._get_text(item.find(text=lambda t: t and 'Комиссия' in t)),
                        'services': self._get_services(item),
                        'address': self._get_text(address_elem),
                        'description': self._get_text(desc_elem),
                        'images': images_str,
                        'images_list': images_list,
                        'link': link
                    }
                    
                    # Проверяем, что получили минимум данных
                    if not data['title'] and not data['price']:
                        continue
                    
                    results.append(data)
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке объявления: {e}")
                    continue
            added_count = await self.db.save_apartments(results)
            
            # Возвращаем статистику
            return {
                'total_listings': len(results),
                'added_to_db': added_count,
                'duplicates_skipped': len(results) - added_count
            }
            
        except Exception as e:
            logger.error(f"Ошибка при обработке HTML: {e}")
            return None
            
    def _get_text(self, element: Any) -> str:
        """Безопасное извлечение текста из элемента"""
        if element:
            # BeautifulSoup Tag
            if hasattr(element, "get_text"):
                return ' '.join(element.get_text(strip=True).split())
            # NavigableString / text node
            return ' '.join(str(element).strip().split())
        return ''
        
    def _get_services(self, soup: Any) -> str:
        """Извлечение информации о коммунальных услугах"""
        services = []
        services_block = soup.find(text=lambda t: t and 'ЖКУ' in t)
        if services_block:
            parent = services_block.parent
            if parent:
                services.append(parent.get_text(strip=True))
        return ', '.join(services)
        
    def _get_images(self, item: Any) -> List[str]:
        """Извлечение ссылок на изображения товара максимального размера"""
        images = []
        
        # Множественные варианты поиска контейнера изображений
        slider_container = (
            item.find('div', {'data-marker': 'item-photo'}) or
            item.find('div', class_='photo-slider-root-jZ0en') or
            item.find('div', class_='iva-item-slider-BOsti') or
            item.find('a', class_='iva-item-sliderLink-kra4e')
        )
        
        if slider_container:
            # Множественные варианты поиска списка изображений
            slider_list = (
                slider_container.find('ul', class_='photo-slider-list') or
                slider_container.find('ul') or
                slider_container
            )
            
            if slider_list:
                # Ищем элементы списка с изображениями (разные варианты классов)
                slider_items = (
                    slider_list.find_all('li', class_='photo-slider-list-item-r2YDC') or
                    slider_list.find_all('li', class_='photo-slider-list-item') or
                    slider_list.find_all('li') or
                    [slider_list]  # Если нет li, используем сам контейнер
                )
                
                for li_item in slider_items:
                    # Множественные варианты поиска изображений
                    imgs = (
                        li_item.find_all('img', class_='photo-slider-image-cD891') or
                        li_item.find_all('img', class_='photo-slider-image') or
                        li_item.find_all('img', {'itemprop': 'image'}) or
                        li_item.find_all('img')
                    )
                    
                    for img in imgs:
                        # Исключаем логотипы продавцов и системные изображения
                        img_classes = img.get('class', [])
                        if any(cls in img_classes for cls in ['style-sellerLogoImageRedesign', 'seller-logo']):
                            continue
                            
                        # Исключаем по src
                        src = img.get('src', '')
                        if any(exclude in src.lower() for exclude in ['logo', 'avatar', 'seller']):
                            continue
                            
                        srcset = img.get('srcset', '')
                        if srcset:
                            # Извлекаем самое большое изображение из srcset
                            largest_image = self._get_largest_image_from_srcset(srcset)
                            if largest_image and largest_image not in images:
                                images.append(largest_image)
                        elif src and src not in images:
                            images.append(src)
                            
                        # Ограничиваем до 3 изображений на объявление
                        if len(images) >= 3:
                            break
                    
                    if len(images) >= 3:
                        break
                        
        # Если не нашли в карусели, ищем любые изображения товара
        if not images:
            all_imgs = item.find_all('img')
            for img in all_imgs:
                # Исключаем системные изображения
                img_classes = img.get('class', [])
                src = img.get('src', '')
                
                # Пропускаем логотипы и системные изображения
                if (any(cls in img_classes for cls in ['style-sellerLogoImageRedesign', 'seller-logo']) or
                    any(exclude in src.lower() for exclude in ['logo', 'avatar', 'seller', 'icon'])):
                    continue
                
                # Берем изображения с itemprop="image" или большие изображения
                if img.get('itemprop') == 'image' or 'avito.st/image' in src:
                    srcset = img.get('srcset', '')
                    if srcset:
                        largest_image = self._get_largest_image_from_srcset(srcset)
                        if largest_image and largest_image not in images:
                            images.append(largest_image)
                    elif src and src not in images:
                        images.append(src)
                        
                    if len(images) >= 3:
                        break
                    
        return images
    
    def _get_largest_image_from_srcset(self, srcset: str) -> str:
        """Извлекает ссылку на самое большое изображение из srcset"""
        if not srcset:
            return ""
            
        # Парсим srcset: "url1 100w, url2 200w, url3 300w"
        sources = []
        for source in srcset.split(','):
            source = source.strip()
            if ' ' in source:
                url, size = source.rsplit(' ', 1)
                # Извлекаем число из размера (например, "636w" -> 636)
                try:
                    width = int(size.replace('w', ''))
                    sources.append((url.strip(), width))
                except ValueError:
                    continue
        
        # Возвращаем URL с максимальной шириной
        if sources:
            largest = max(sources, key=lambda x: x[1])
            return largest[0]
        
        return ""
        
    # Сохранение в БД вынесено в `database.avito_sqlite.AvitoSQLite`
