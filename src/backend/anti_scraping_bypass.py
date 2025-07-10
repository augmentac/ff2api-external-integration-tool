#!/usr/bin/env python3
"""
Advanced Anti-Scraping Bypass System for LTL Carrier Tracking

This module implements sophisticated techniques to bypass anti-scraping measures
including browser fingerprinting, session management, proxy rotation, and more.
"""

import asyncio
import random
import time
import json
import base64
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Advanced imports for anti-detection
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from webdriver_manager.chrome import ChromeDriverManager
    
    # Advanced stealth imports
    try:
        from selenium_stealth import stealth
        STEALTH_AVAILABLE = True
    except ImportError:
        STEALTH_AVAILABLE = False
        
    try:
        from undetected_chromedriver import Chrome as UndetectedChrome
        UNDETECTED_AVAILABLE = True
    except ImportError:
        UNDETECTED_AVAILABLE = False
        
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    STEALTH_AVAILABLE = False
    UNDETECTED_AVAILABLE = False

# CAPTCHA solving imports
try:
    import twocaptcha
    CAPTCHA_SOLVING_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVING_AVAILABLE = False

# Proxy rotation imports
try:
    import itertools
    from concurrent.futures import ThreadPoolExecutor
    PROXY_ROTATION_AVAILABLE = True
except ImportError:
    PROXY_ROTATION_AVAILABLE = False


class BypassStrategy(Enum):
    """Different bypass strategies for different carriers"""
    STEALTH_BROWSER = "stealth_browser"
    API_REVERSE_ENGINEERING = "api_reverse_engineering"
    SESSION_WARMING = "session_warming"
    PROXY_ROTATION = "proxy_rotation"
    CAPTCHA_SOLVING = "captcha_solving"
    MOBILE_SIMULATION = "mobile_simulation"
    DISTRIBUTED_REQUESTS = "distributed_requests"


@dataclass
class BrowserFingerprint:
    """Browser fingerprint configuration"""
    user_agent: str
    viewport: Tuple[int, int]
    screen_resolution: Tuple[int, int]
    timezone: str
    language: str
    platform: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    webrtc_ip: str


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"
    country: Optional[str] = None
    city: Optional[str] = None


class AntiScrapingBypass:
    """
    Advanced anti-scraping bypass system for LTL carriers
    """
    
    def __init__(self, captcha_api_key: Optional[str] = None):
        """
        Initialize the anti-scraping bypass system
        
        Args:
            captcha_api_key: API key for CAPTCHA solving service
        """
        self.logger = logging.getLogger(__name__)
        self.captcha_api_key = captcha_api_key
        self.session_pool = {}
        self.proxy_pool = []
        self.browser_fingerprints = self._generate_browser_fingerprints()
        self.active_sessions = {}
        
        # Initialize CAPTCHA solver
        if CAPTCHA_SOLVING_AVAILABLE and captcha_api_key:
            self.captcha_solver = twocaptcha.TwoCaptcha(captcha_api_key)
        else:
            self.captcha_solver = None
            
        # Initialize proxy rotation
        self.proxy_iterator = None
        self.current_proxy = None
        
    def _generate_browser_fingerprints(self) -> List[BrowserFingerprint]:
        """Generate realistic browser fingerprints"""
        fingerprints = []
        
        # Common user agents with realistic fingerprints
        user_agents = [
            {
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'platform': 'MacIntel',
                'viewport': (1440, 900),
                'screen_resolution': (2560, 1440),
                'webgl_vendor': 'Intel Inc.',
                'webgl_renderer': 'Intel Iris Pro OpenGL Engine'
            },
            {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'platform': 'Win32',
                'viewport': (1920, 1080),
                'screen_resolution': (1920, 1080),
                'webgl_vendor': 'Google Inc. (NVIDIA)',
                'webgl_renderer': 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11)'
            },
            {
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'platform': 'Linux x86_64',
                'viewport': (1366, 768),
                'screen_resolution': (1366, 768),
                'webgl_vendor': 'Mesa',
                'webgl_renderer': 'Mesa DRI Intel(R) UHD Graphics 620 (WHL GT2)'
            }
        ]
        
        timezones = ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles', 'America/Phoenix']
        languages = ['en-US,en;q=0.9', 'en-US,en;q=0.8,es;q=0.7', 'en-US,en;q=0.9,fr;q=0.8']
        
        for ua_config in user_agents:
            for timezone in timezones:
                for language in languages:
                    fingerprint = BrowserFingerprint(
                        user_agent=ua_config['user_agent'],
                        viewport=ua_config['viewport'],
                        screen_resolution=ua_config['screen_resolution'],
                        timezone=timezone,
                        language=language,
                        platform=ua_config['platform'],
                        webgl_vendor=ua_config['webgl_vendor'],
                        webgl_renderer=ua_config['webgl_renderer'],
                        canvas_fingerprint=self._generate_canvas_fingerprint(),
                        webrtc_ip=self._generate_webrtc_ip()
                    )
                    fingerprints.append(fingerprint)
                    
        return fingerprints
    
    def _generate_canvas_fingerprint(self) -> str:
        """Generate a unique canvas fingerprint"""
        # Create a deterministic but unique canvas fingerprint
        random_data = f"{random.randint(1000, 9999)}{time.time()}"
        return hashlib.md5(random_data.encode()).hexdigest()[:16]
    
    def _generate_webrtc_ip(self) -> str:
        """Generate a realistic WebRTC IP address"""
        # Generate a private IP address
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def add_proxy(self, proxy: ProxyConfig):
        """Add a proxy to the rotation pool"""
        self.proxy_pool.append(proxy)
        self.proxy_iterator = itertools.cycle(self.proxy_pool)
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get the next proxy in rotation"""
        if self.proxy_iterator:
            return next(self.proxy_iterator)
        return None
    
    def create_stealth_session(self, carrier: str, fingerprint: Optional[BrowserFingerprint] = None) -> requests.Session:
        """
        Create a stealth session with advanced anti-detection measures
        
        Args:
            carrier: Carrier name for session customization
            fingerprint: Browser fingerprint to use
            
        Returns:
            Configured requests session
        """
        if not fingerprint:
            fingerprint = random.choice(self.browser_fingerprints)
        
        session = requests.Session()
        
        # Configure session with realistic headers
        session.headers.update({
            'User-Agent': fingerprint.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': fingerprint.language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{fingerprint.platform}"',
            'Cache-Control': 'max-age=0'
        })
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Configure proxy if available
        if self.proxy_pool:
            proxy = self.get_next_proxy()
            if proxy:
                proxy_url = f"{proxy.proxy_type}://"
                if proxy.username and proxy.password:
                    proxy_url += f"{proxy.username}:{proxy.password}@"
                proxy_url += f"{proxy.host}:{proxy.port}"
                
                session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
        
        # Store session for reuse
        session_key = f"{carrier}_{fingerprint.user_agent[:20]}"
        self.session_pool[session_key] = session
        
        return session
    
    def create_stealth_browser(self, carrier: str, fingerprint: Optional[BrowserFingerprint] = None) -> Optional[webdriver.Chrome]:
        """
        Create a stealth browser with advanced anti-detection
        
        Args:
            carrier: Carrier name for browser customization
            fingerprint: Browser fingerprint to use
            
        Returns:
            Configured Chrome WebDriver or None if failed
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium not available for stealth browser creation")
            return None
        
        if not fingerprint:
            fingerprint = random.choice(self.browser_fingerprints)
        
        try:
            # Use undetected-chromedriver if available
            if UNDETECTED_AVAILABLE:
                options = webdriver.ChromeOptions()
            else:
                options = Options()
            
            # Configure stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument(f'--window-size={fingerprint.viewport[0]},{fingerprint.viewport[1]}')
            options.add_argument(f'--user-agent={fingerprint.user_agent}')
            
            # Add proxy if available
            if self.proxy_pool:
                proxy = self.get_next_proxy()
                if proxy:
                    options.add_argument(f'--proxy-server={proxy.proxy_type}://{proxy.host}:{proxy.port}')
            
            # Disable automation indicators
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Add realistic preferences
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                }
            }
            options.add_experimental_option("prefs", prefs)
            
            # Create driver
            if UNDETECTED_AVAILABLE:
                driver = UndetectedChrome(options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            # Apply stealth techniques
            if STEALTH_AVAILABLE:
                stealth(driver,
                    languages=[fingerprint.language.split(',')[0]],
                    vendor="Google Inc.",
                    platform=fingerprint.platform,
                    webgl_vendor=fingerprint.webgl_vendor,
                    renderer=fingerprint.webgl_renderer,
                    fix_hairline=True,
                )
            
            # Execute additional stealth scripts
            self._execute_stealth_scripts(driver, fingerprint)
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create stealth browser: {e}")
            return None
    
    def _execute_stealth_scripts(self, driver: webdriver.Chrome, fingerprint: BrowserFingerprint):
        """Execute JavaScript to enhance stealth capabilities"""
        try:
            # Override navigator properties
            stealth_script = f"""
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined,
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => ['{fingerprint.language.split(',')[0]}'],
            }});
            
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{fingerprint.platform}',
            }});
            
            Object.defineProperty(screen, 'width', {{
                get: () => {fingerprint.screen_resolution[0]},
            }});
            
            Object.defineProperty(screen, 'height', {{
                get: () => {fingerprint.screen_resolution[1]},
            }});
            
            // Override WebRTC
            const getWebRTC = () => {{
                const rtc = new RTCPeerConnection({{iceServers: [{{urls: "stun:stun.l.google.com:19302"}}]}});
                rtc.createDataChannel("");
                return rtc;
            }};
            
            // Override canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {{
                if (type === 'image/png') {{
                    return 'data:image/png;base64,{fingerprint.canvas_fingerprint}';
                }}
                return originalToDataURL.apply(this, arguments);
            }};
            
            // Override timezone
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                return {{
                    timeZone: '{fingerprint.timezone}',
                    locale: '{fingerprint.language.split(',')[0]}'
                }};
            }};
            """
            
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })
            
        except Exception as e:
            self.logger.debug(f"Failed to execute stealth scripts: {e}")
    
    def warm_session(self, session: requests.Session, carrier_domain: str) -> bool:
        """
        Warm up a session by visiting related pages to establish legitimacy
        
        Args:
            session: Session to warm up
            carrier_domain: Domain of the carrier website
            
        Returns:
            True if warming successful, False otherwise
        """
        try:
            # Visit homepage first
            homepage_url = f"https://{carrier_domain}"
            response = session.get(homepage_url, timeout=10)
            
            if response.status_code != 200:
                return False
            
            # Add realistic delay
            time.sleep(random.uniform(1, 3))
            
            # Visit common pages to establish browsing pattern
            common_paths = ['/about', '/services', '/contact', '/tracking']
            
            for path in common_paths[:2]:  # Visit 2 random pages
                try:
                    url = urljoin(homepage_url, path)
                    response = session.get(url, timeout=10)
                    time.sleep(random.uniform(0.5, 2))
                except:
                    continue
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Session warming failed: {e}")
            return False
    
    def solve_captcha(self, captcha_image_url: str, captcha_type: str = "image") -> Optional[str]:
        """
        Solve CAPTCHA using external service
        
        Args:
            captcha_image_url: URL of CAPTCHA image
            captcha_type: Type of CAPTCHA (image, recaptcha, etc.)
            
        Returns:
            CAPTCHA solution or None if failed
        """
        if not self.captcha_solver:
            self.logger.warning("CAPTCHA solver not available")
            return None
        
        try:
            if captcha_type == "image":
                result = self.captcha_solver.normal(captcha_image_url)
                return result.get('code')
            elif captcha_type == "recaptcha":
                # Handle reCAPTCHA
                result = self.captcha_solver.recaptcha(
                    sitekey=captcha_image_url,  # In this case, sitekey
                    url=captcha_image_url
                )
                return result.get('code')
            
        except Exception as e:
            self.logger.error(f"CAPTCHA solving failed: {e}")
            return None
    
    def simulate_human_behavior(self, driver: webdriver.Chrome, delay_range: Tuple[float, float] = (0.5, 2.0)):
        """
        Simulate human-like behavior in browser
        
        Args:
            driver: WebDriver instance
            delay_range: Range for random delays
        """
        try:
            # Random scroll
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
            time.sleep(random.uniform(*delay_range))
            
            # Random mouse movement
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
            actions.perform()
            
            time.sleep(random.uniform(*delay_range))
            
        except Exception as e:
            self.logger.debug(f"Human behavior simulation failed: {e}")
    
    def detect_and_handle_challenges(self, driver: webdriver.Chrome, url: str) -> bool:
        """
        Detect and handle various anti-bot challenges
        
        Args:
            driver: WebDriver instance
            url: Current URL being accessed
            
        Returns:
            True if challenges handled successfully, False otherwise
        """
        try:
            # Check for common challenge indicators
            page_source = driver.page_source.lower()
            
            # Cloudflare challenge
            if 'cloudflare' in page_source and 'checking your browser' in page_source:
                self.logger.info("Detected Cloudflare challenge")
                return self._handle_cloudflare_challenge(driver)
            
            # reCAPTCHA
            if 'recaptcha' in page_source or 'g-recaptcha' in page_source:
                self.logger.info("Detected reCAPTCHA")
                return self._handle_recaptcha(driver)
            
            # Generic CAPTCHA
            captcha_selectors = ['img[src*="captcha"]', '.captcha', '#captcha']
            for selector in captcha_selectors:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    self.logger.info("Detected image CAPTCHA")
                    return self._handle_image_captcha(driver, selector)
            
            # JavaScript challenge
            if 'please enable javascript' in page_source:
                self.logger.info("Detected JavaScript requirement")
                return self._handle_javascript_challenge(driver)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Challenge detection failed: {e}")
            return False
    
    def _handle_cloudflare_challenge(self, driver: webdriver.Chrome) -> bool:
        """Handle Cloudflare challenge"""
        try:
            # Wait for Cloudflare to complete
            WebDriverWait(driver, 30).until(
                lambda d: 'cloudflare' not in d.page_source.lower() or 
                         'checking your browser' not in d.page_source.lower()
            )
            return True
        except TimeoutException:
            return False
    
    def _handle_recaptcha(self, driver: webdriver.Chrome) -> bool:
        """Handle reCAPTCHA challenge"""
        try:
            # Find reCAPTCHA sitekey
            recaptcha_element = driver.find_element(By.CSS_SELECTOR, '[data-sitekey]')
            sitekey = recaptcha_element.get_attribute('data-sitekey')
            
            if self.captcha_solver and sitekey:
                solution = self.solve_captcha(sitekey, "recaptcha")
                if solution:
                    # Inject solution
                    driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{solution}';")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"reCAPTCHA handling failed: {e}")
            return False
    
    def _handle_image_captcha(self, driver: webdriver.Chrome, selector: str) -> bool:
        """Handle image CAPTCHA"""
        try:
            captcha_img = driver.find_element(By.CSS_SELECTOR, selector)
            captcha_url = captcha_img.get_attribute('src')
            
            if self.captcha_solver and captcha_url:
                solution = self.solve_captcha(captcha_url, "image")
                if solution:
                    # Find input field and enter solution
                    input_field = driver.find_element(By.CSS_SELECTOR, 'input[name*="captcha"], input[id*="captcha"]')
                    input_field.send_keys(solution)
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Image CAPTCHA handling failed: {e}")
            return False
    
    def _handle_javascript_challenge(self, driver: webdriver.Chrome) -> bool:
        """Handle JavaScript challenge"""
        try:
            # Enable JavaScript and wait
            driver.execute_script("return true;")
            time.sleep(5)
            
            # Check if challenge resolved
            if 'please enable javascript' not in driver.page_source.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"JavaScript challenge handling failed: {e}")
            return False
    
    def get_carrier_specific_strategy(self, carrier: str) -> List[BypassStrategy]:
        """
        Get recommended bypass strategies for specific carrier
        
        Args:
            carrier: Carrier name
            
        Returns:
            List of recommended strategies in order of preference
        """
        strategies = {
            'peninsula': [
                BypassStrategy.API_REVERSE_ENGINEERING,
                BypassStrategy.STEALTH_BROWSER,
                BypassStrategy.SESSION_WARMING,
                BypassStrategy.MOBILE_SIMULATION
            ],
            'fedex': [
                BypassStrategy.MOBILE_SIMULATION,
                BypassStrategy.API_REVERSE_ENGINEERING,
                BypassStrategy.STEALTH_BROWSER,
                BypassStrategy.PROXY_ROTATION
            ],
            'estes': [
                BypassStrategy.STEALTH_BROWSER,
                BypassStrategy.SESSION_WARMING,
                BypassStrategy.CAPTCHA_SOLVING,
                BypassStrategy.DISTRIBUTED_REQUESTS
            ]
        }
        
        return strategies.get(carrier.lower(), [BypassStrategy.STEALTH_BROWSER])
    
    def cleanup_resources(self):
        """Clean up resources and close sessions"""
        try:
            # Close all sessions
            for session in self.session_pool.values():
                session.close()
            
            # Clear pools
            self.session_pool.clear()
            self.active_sessions.clear()
            
        except Exception as e:
            self.logger.debug(f"Resource cleanup failed: {e}") 