#!/usr/bin/env python3
"""
Zero-Cost Anti-Scraping System

Complete anti-scraping bypass solution without external dependencies or costs.
Includes TOR rotation, local CAPTCHA solving, and advanced browser fingerprinting.
"""

import asyncio
import base64
import hashlib
import json
import logging
import random
import re
import requests
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Optional imports with fallbacks
try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False
    socks = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Computer vision for CAPTCHA solving
try:
    import pytesseract
    import cv2
    CAPTCHA_SOLVING_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVING_AVAILABLE = False
    pytesseract = None
    cv2 = None

# Lightweight browser automation
try:
    import pyppeteer
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False

# TOR integration
try:
    import stem
    from stem import Signal
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False

# Requests HTML for JavaScript execution
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False


@dataclass
class ZeroCostFingerprint:
    """Zero-cost browser fingerprint"""
    user_agent: str
    platform: str
    viewport: Tuple[int, int]
    screen_resolution: Tuple[int, int]
    timezone: str
    language: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    plugins: List[str]
    fonts: List[str]


class LocalCaptchaSolver:
    """Local CAPTCHA solving using computer vision"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def solve_image_captcha(self, image_url: str) -> Optional[str]:
        """Solve image CAPTCHA using local OCR"""
        if not CAPTCHA_SOLVING_AVAILABLE or not PIL_AVAILABLE:
            self.logger.warning("CAPTCHA solving not available - install opencv-python, pytesseract, and Pillow")
            return None
            
        try:
            import pytesseract
            import cv2
            
            # Download CAPTCHA image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return None
                
            # Load image
            if PIL_AVAILABLE and Image:
                image = Image.open(BytesIO(response.content))
            else:
                return None
            
            # Preprocess image for OCR
            processed_image = self._preprocess_captcha_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                processed_image,
                config='--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            )
            
            return text.strip().upper()
            
        except Exception as e:
            self.logger.debug(f"Local CAPTCHA solving failed: {e}")
            return None
    
    def _preprocess_captcha_image(self, image):
        """Preprocess CAPTCHA image for better OCR"""
        try:
            if not CAPTCHA_SOLVING_AVAILABLE or not NUMPY_AVAILABLE:
                return None
                
            import cv2
            import numpy as np
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Apply threshold to create binary image
            _, binary = cv2.threshold(img_array, 128, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Resize for better OCR
            height, width = cleaned.shape
            if height < 40:
                scale_factor = 40 / height
                new_width = int(width * scale_factor)
                cleaned = cv2.resize(cleaned, (new_width, 40), interpolation=cv2.INTER_CUBIC)
            
            return cleaned
            
        except Exception as e:
            self.logger.debug(f"Image preprocessing failed: {e}")
            if NUMPY_AVAILABLE:
                import numpy as np
                return np.array(image)
            return None


class TorRotationManager:
    """TOR-based IP rotation for free proxy functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tor_port = 9050
        self.control_port = 9051
        self.tor_password = None
        self.session = None
        self._setup_tor_session()
    
    def _setup_tor_session(self):
        """Set up TOR session for requests"""
        try:
            if not TOR_AVAILABLE:
                self.logger.warning("TOR not available - install stem for IP rotation")
                self.session = requests.Session()  # Use regular session
                return
            
            # Test if TOR is actually running
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            tor_running = test_socket.connect_ex(('127.0.0.1', self.tor_port)) == 0
            test_socket.close()
            
            if not tor_running:
                self.logger.warning("TOR not running - using regular session")
                self.session = requests.Session()
                return
            
            # Create session with TOR proxy
            self.session = requests.Session()
            self.session.proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            
            # DON'T set global socket proxy - this breaks other libraries
            # Only use proxy for this specific session
            
            self.logger.info("TOR session configured successfully")
            
        except Exception as e:
            self.logger.debug(f"TOR setup failed: {e}")
            self.session = requests.Session()  # Fallback to regular session
    
    def get_new_ip(self) -> bool:
        """Request new IP address through TOR"""
        try:
            if not TOR_AVAILABLE:
                return False
                
            with Controller.from_port(port=self.control_port) as controller:
                if self.tor_password:
                    controller.authenticate(password=self.tor_password)
                else:
                    controller.authenticate()
                
                controller.signal(Signal.NEWNYM)
                time.sleep(2)  # Wait for new circuit
                
            self.logger.debug("Successfully rotated to new IP")
            return True
            
        except Exception as e:
            self.logger.debug(f"IP rotation failed: {e}")
            return False
    
    def get_current_ip(self) -> Optional[str]:
        """Get current external IP address"""
        try:
            if self.session:
                response = self.session.get('https://httpbin.org/ip', timeout=10)
                if response.status_code == 200:
                    return response.json().get('origin')
            return None
        except Exception as e:
            self.logger.debug(f"IP check failed: {e}")
            return None


class ZeroCostFingerprintGenerator:
    """Generate realistic browser fingerprints without external services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fingerprint_database = self._load_fingerprint_database()
    
    def _load_fingerprint_database(self) -> Dict:
        """Load realistic fingerprint patterns"""
        return {
            'user_agents': [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
            ],
            'platforms': ['MacIntel', 'Win32', 'Linux x86_64'],
            'screen_resolutions': [
                (1920, 1080), (2560, 1440), (1366, 768), (1440, 900), (1536, 864)
            ],
            'viewports': [
                (1920, 1080), (1440, 900), (1366, 768), (1280, 720), (1024, 768)
            ],
            'timezones': [
                'America/New_York', 'America/Chicago', 'America/Denver', 
                'America/Los_Angeles', 'America/Phoenix'
            ],
            'languages': [
                'en-US,en;q=0.9', 'en-US,en;q=0.8,es;q=0.7', 'en-US,en;q=0.9,fr;q=0.8'
            ],
            'webgl_vendors': ['Intel Inc.', 'NVIDIA Corporation', 'AMD'],
            'webgl_renderers': [
                'Intel Iris Pro OpenGL Engine',
                'NVIDIA GeForce GTX 1060 6GB/PCIe/SSE2',
                'AMD Radeon RX 580 Series'
            ],
            'plugins': [
                ['Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client'],
                ['PDF Plugin', 'Chrome PDF Viewer', 'WebKit built-in PDF'],
                ['Chromium PDF Plugin', 'Chromium PDF Viewer', 'Native Client']
            ],
            'fonts': [
                ['Arial', 'Times New Roman', 'Courier New', 'Helvetica', 'Georgia'],
                ['Segoe UI', 'Tahoma', 'Verdana', 'Calibri', 'Cambria'],
                ['San Francisco', 'Helvetica Neue', 'Lucida Grande', 'Monaco']
            ]
        }
    
    def generate_fingerprint(self) -> ZeroCostFingerprint:
        """Generate a realistic browser fingerprint"""
        db = self.fingerprint_database
        
        # Select consistent combination
        user_agent = random.choice(db['user_agents'])
        
        # Determine platform from user agent
        if 'Macintosh' in user_agent:
            platform = 'MacIntel'
            fonts = db['fonts'][2]  # Mac fonts
        elif 'Windows' in user_agent:
            platform = 'Win32'
            fonts = db['fonts'][1]  # Windows fonts
        else:
            platform = 'Linux x86_64'
            fonts = db['fonts'][0]  # Linux fonts
        
        screen_res = random.choice(db['screen_resolutions'])
        viewport = random.choice([res for res in db['viewports'] if res[0] <= screen_res[0]])
        
        return ZeroCostFingerprint(
            user_agent=user_agent,
            platform=platform,
            viewport=viewport,
            screen_resolution=screen_res,
            timezone=random.choice(db['timezones']),
            language=random.choice(db['languages']),
            webgl_vendor=random.choice(db['webgl_vendors']),
            webgl_renderer=random.choice(db['webgl_renderers']),
            canvas_fingerprint=self._generate_canvas_fingerprint(),
            plugins=random.choice(db['plugins']),
            fonts=fonts
        )
    
    def _generate_canvas_fingerprint(self) -> str:
        """Generate unique canvas fingerprint"""
        # Create deterministic but unique fingerprint
        timestamp = str(int(time.time()))
        random_data = f"{random.randint(1000, 9999)}{timestamp}"
        return hashlib.md5(random_data.encode()).hexdigest()[:16]


class LightweightBrowserManager:
    """Lightweight browser automation without Selenium"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fingerprint_gen = ZeroCostFingerprintGenerator()
    
    async def execute_javascript_pyppeteer(self, url: str, fingerprint: ZeroCostFingerprint) -> Optional[str]:
        """Execute JavaScript using Pyppeteer"""
        if not PYPPETEER_AVAILABLE:
            self.logger.warning("Pyppeteer not available for JavaScript execution")
            return None
        
        browser = None
        try:
            # Launch browser with stealth options
            browser = await launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    f'--window-size={fingerprint.viewport[0]},{fingerprint.viewport[1]}',
                    f'--user-agent={fingerprint.user_agent}'
                ]
            )
            
            page = await browser.newPage()
            
            # Set viewport
            await page.setViewport({
                'width': fingerprint.viewport[0],
                'height': fingerprint.viewport[1]
            })
            
            # Override fingerprinting
            await self._apply_stealth_techniques(page, fingerprint)
            
            # Navigate to page
            await page.goto(url, waitUntil='networkidle2', timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Get page content
            content = await page.content()
            
            return content
            
        except Exception as e:
            self.logger.debug(f"Pyppeteer execution failed: {e}")
            return None
        finally:
            if browser:
                await browser.close()
    
    async def _apply_stealth_techniques(self, page, fingerprint: ZeroCostFingerprint):
        """Apply stealth techniques to bypass detection"""
        try:
            # Override navigator properties
            await page.evaluateOnNewDocument(f'''
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined,
                }});
                
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint.platform}',
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['{fingerprint.language.split(',')[0]}'],
                }});
                
                Object.defineProperty(screen, 'width', {{
                    get: () => {fingerprint.screen_resolution[0]},
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: () => {fingerprint.screen_resolution[1]},
                }});
                
                // Override canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {{
                    if (type === 'image/png') {{
                        return 'data:image/png;base64,{fingerprint.canvas_fingerprint}';
                    }}
                    return originalToDataURL.apply(this, arguments);
                }};
                
                // Override WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return '{fingerprint.webgl_vendor}';
                    }}
                    if (parameter === 37446) {{
                        return '{fingerprint.webgl_renderer}';
                    }}
                    return getParameter.call(this, parameter);
                }};
            ''')
            
        except Exception as e:
            self.logger.debug(f"Stealth technique application failed: {e}")
    
    def execute_javascript_requests_html(self, url: str) -> Optional[str]:
        """Execute JavaScript using requests-html"""
        if not REQUESTS_HTML_AVAILABLE:
            return None
        
        try:
            session = HTMLSession()
            response = session.get(url)
            response.html.render(timeout=20, wait=3)
            return response.html.html
            
        except Exception as e:
            self.logger.debug(f"Requests-HTML execution failed: {e}")
            return None


class ZeroCostAntiScrapingSystem:
    """Complete zero-cost anti-scraping system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tor_manager = TorRotationManager()
        self.captcha_solver = LocalCaptchaSolver()
        self.fingerprint_gen = ZeroCostFingerprintGenerator()
        self.browser_manager = LightweightBrowserManager()
        self.session_pool = {}
        
    def create_stealth_session(self, carrier: str) -> requests.Session:
        """Create stealth session with anti-detection measures"""
        fingerprint = self.fingerprint_gen.generate_fingerprint()
        
        # Use TOR session if available, otherwise regular session
        if self.tor_manager.session:
            session = self.tor_manager.session
        else:
            session = requests.Session()
        
        # Configure headers based on fingerprint
        session.headers.update({
            'User-Agent': fingerprint.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': fingerprint.language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # Store session for reuse
        self.session_pool[f"{carrier}_{fingerprint.user_agent[:20]}"] = session
        
        return session
    
    def rotate_ip(self) -> bool:
        """Rotate IP address using TOR"""
        return self.tor_manager.get_new_ip()
    
    def solve_captcha(self, captcha_url: str) -> Optional[str]:
        """Solve CAPTCHA using local computer vision"""
        return self.captcha_solver.solve_image_captcha(captcha_url)
    
    async def render_javascript_page(self, url: str) -> Optional[str]:
        """Render JavaScript page using lightweight browser"""
        fingerprint = self.fingerprint_gen.generate_fingerprint()
        
        # Try Pyppeteer first
        content = await self.browser_manager.execute_javascript_pyppeteer(url, fingerprint)
        if content:
            return content
        
        # Fallback to requests-html
        return self.browser_manager.execute_javascript_requests_html(url)
    
    def simulate_human_behavior(self, min_delay: float = 1.0, max_delay: float = 5.0):
        """Simulate human browsing behavior"""
        # Random delay to simulate reading time
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def warm_session(self, session: requests.Session, domain: str) -> bool:
        """Warm up session by visiting related pages"""
        try:
            # Visit homepage
            homepage = f"https://{domain}"
            response = session.get(homepage, timeout=10)
            
            if response.status_code != 200:
                return False
            
            self.simulate_human_behavior(1, 3)
            
            # Visit common pages
            common_paths = ['/about', '/services', '/contact']
            for path in random.sample(common_paths, 2):
                try:
                    url = urljoin(homepage, path)
                    session.get(url, timeout=10)
                    self.simulate_human_behavior(0.5, 2)
                except:
                    continue
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Session warming failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            for session in self.session_pool.values():
                session.close()
            self.session_pool.clear()
        except Exception as e:
            self.logger.debug(f"Cleanup failed: {e}") 