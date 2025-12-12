import random
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DeviceProfile:
    user_agent: str
    viewport: Dict[str, int]
    platform: str
    mobile: bool
    touch: bool

class UserAgentRotator:
    def __init__(self) -> None:
        self.desktop_profiles = [
            DeviceProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                platform="Win32",
                mobile=False,
                touch=False
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                platform="Win32",
                mobile=False,
                touch=False
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                platform="MacIntel",
                mobile=False,
                touch=False
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                platform="Linux x86_64",
                mobile=False,
                touch=False
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                viewport={"width": 1920, "height": 1080},
                platform="Win32",
                mobile=False,
                touch=False
            ),
        ]
        
        self.mobile_profiles = [
            DeviceProfile(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                viewport={"width": 375, "height": 667},
                platform="iPhone",
                mobile=True,
                touch=True
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
                viewport={"width": 360, "height": 640},
                platform="Linux armv7l",
                mobile=True,
                touch=True
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
                viewport={"width": 393, "height": 851},
                platform="Linux armv7l",
                mobile=True,
                touch=True
            ),
        ]
        
        self.tablet_profiles = [
            DeviceProfile(
                user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                viewport={"width": 768, "height": 1024},
                platform="MacIntel",
                mobile=False,
                touch=True
            ),
            DeviceProfile(
                user_agent="Mozilla/5.0 (Linux; Android 12; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                viewport={"width": 1024, "height": 768},
                platform="Linux armv7l",
                mobile=False,
                touch=True
            ),
        ]
    
    def get_random_profile(self, device_type: str = "desktop") -> DeviceProfile:
        """Получить случайный профиль устройства"""
        if device_type == "mobile":
            return random.choice(self.mobile_profiles)
        elif device_type == "tablet":
            return random.choice(self.tablet_profiles)
        else:
            return random.choice(self.desktop_profiles)
    
    def get_headers(self, device_type: str = "desktop") -> Dict[str, str]:
        """Получить заголовки для определенного типа устройства"""
        profile = self.get_random_profile(device_type)
        
        base_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': profile.user_agent
        }
        
        if device_type == "mobile":
            base_headers.update({
                'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': f'"{profile.platform}"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
            })
        else:
            base_headers.update({
                'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': f'"{profile.platform}"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
            })
        
        return base_headers
    
    def get_browser_context_params(self, device_type: str = "desktop") -> Dict[str, object]:
        """Получить параметры для контекста браузера"""
        profile = self.get_random_profile(device_type)
        
        return {
            'viewport': profile.viewport,
            'user_agent': profile.user_agent,
            'is_mobile': profile.mobile,
            'has_touch': profile.touch,
            'device_scale_factor': 1 if device_type == "desktop" else random.choice([1, 2, 3]),
        }
    
    def get_browser_args(self, device_type: str = "desktop") -> List[str]:
        """Получить аргументы запуска браузера для определенного типа устройства"""
        profile = self.get_random_profile(device_type)
        
        base_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-features=BlockInsecurePrivateNetworkRequests',
            '--disable-features=CrossSiteDocumentBlockingIfIsolating',
            '--disable-features=CrossSiteDocumentBlockingAlways',
            '--disable-gpu',
            '--hide-scrollbars',
            '--mute-audio',
            '--disable-infobars',
            '--no-default-browser-check',
            '--disable-notifications',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-save-password-bubble',
            '--disable-translate',
            '--disable-extensions',
            f'--user-agent={profile.user_agent}',
            f'--window-size={profile.viewport["width"]},{profile.viewport["height"]}'
        ]
        
        if device_type == "mobile":
            base_args.extend([
                '--touch-events=enabled',
                '--enable-touch-drag-drop',
                '--enable-pinch',
            ])
        
        return base_args

