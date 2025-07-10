"""
Apple Silicon Compatible Estes Express Tracking Client
Solves the ARM64 CPU architecture barrier with proper ChromeDriver management
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class AppleSiliconEstesClient:
    """
    Apple Silicon compatible Estes Express tracking client
    Uses webdriver-manager for ARM64 ChromeDriver compatibility
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.base_urls = [
            "https://www.estes-express.com/",
            "https://www.estes-express.com/myestes/",
            "https://m.estes-express.com/",
            "https://mobile.estes-express.com/"
        ]
        self.tracking_endpoints = [
            "https://www.estes-express.com/myestes/shipment-tracking/",
            "https://www.estes-express.com/myestes/shipment-tracking/track-shipment",
            "https://www.estes-express.com/tools/track-shipment",
            "https://api.estes-express.com/v1/tracking/",
            "https://mobile.estes-express.com/track/"
        ]
        self.setup_session()
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def get_apple_silicon_chrome_driver(self) -> webdriver.Chrome:
        """
        Get Apple Silicon compatible ChromeDriver using webdriver-manager
        Solves the ARM64 CPU architecture barrier
        """
        try:
            # Use webdriver-manager to get ARM64 compatible ChromeDriver
            chrome_driver_path = ChromeDriverManager().install()
            logger.info(f"Using ChromeDriver: {chrome_driver_path}")
            
            chrome_options = Options()
            
            # Stealth options for Apple Silicon
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--ignore-certificate-errors-spki-list')
            
            # User agent rotation
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Window size randomization
            chrome_options.add_argument(f'--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}')
            
            # Create service with managed ChromeDriver
            service = Service(chrome_driver_path)
            
            # Create driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Apply stealth JavaScript
            self.apply_stealth_javascript(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create Apple Silicon ChromeDriver: {e}")
            raise
    
    def apply_stealth_javascript(self, driver):
        """Apply advanced stealth JavaScript to bypass detection"""
        stealth_scripts = [
            # Override webdriver property
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """,
            
            # Override plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            """,
            
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            return window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Override chrome runtime
            """
            if (!window.chrome) {
                window.chrome = {};
            }
            if (!window.chrome.runtime) {
                window.chrome.runtime = {};
            }
            """,
            
            # Override connection rtt
            """
            if (navigator.connection) {
                Object.defineProperty(navigator.connection, 'rtt', {
                    get: () => 100,
                });
            }
            """
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_script(script)
            except Exception as e:
                logger.warning(f"Failed to execute stealth script: {e}")
    
    async def track_with_playwright(self, tracking_number: str) -> Dict:
        """Track using Playwright (ARM64 compatible) with Angular Material form handling"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,  # Show browser for debugging
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Navigate to tracking page
                logger.info("🌐 Navigating to Estes tracking page...")
                await page.goto('https://www.estes-express.com/myestes/shipment-tracking/')
                
                # Wait for Angular app to load
                logger.info("⏳ Waiting for Angular app to load...")
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(5000)  # Additional wait for Angular
                
                # Look for the Angular Material form
                logger.info("🔍 Looking for Angular Material tracking form...")
                
                # Try to find the form container first
                form_container = await page.query_selector('#shipmentTrackingFormContainer')
                if not form_container:
                    logger.warning("❌ Form container not found")
                    await browser.close()
                    return {'success': False, 'error': 'Angular form container not found'}
                
                logger.info("✅ Found form container")
                
                # Look for the textarea within the Angular Material form
                textarea_selectors = [
                    'textarea[placeholder*="track"]',
                    'textarea[placeholder*="number"]',
                    'textarea[name*="track"]',
                    'textarea[id*="track"]',
                    'textarea',  # Fallback to any textarea
                    'mat-form-field textarea',
                    '.mat-mdc-form-field textarea'
                ]
                
                tracking_textarea = None
                for selector in textarea_selectors:
                    try:
                        tracking_textarea = await page.query_selector(selector)
                        if tracking_textarea and await tracking_textarea.is_visible():
                            logger.info(f"✅ Found tracking textarea with selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                if not tracking_textarea:
                    logger.warning("❌ No tracking textarea found")
                    await browser.close()
                    return {'success': False, 'error': 'Tracking textarea not found in Angular form'}
                
                # Enter the tracking number
                logger.info(f"📝 Entering tracking number: {tracking_number}")
                await tracking_textarea.click()
                await tracking_textarea.fill(tracking_number)
                
                # Look for the submit button
                logger.info("🔍 Looking for submit button...")
                submit_button = await page.query_selector('#shipmentTrackingSubmitButton')
                if not submit_button:
                    # Try alternative selectors
                    submit_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Search")',
                        'button:has-text("Track")',
                        '.btn-primary'
                    ]
                    for selector in submit_selectors:
                        submit_button = await page.query_selector(selector)
                        if submit_button:
                            logger.info(f"✅ Found submit button with selector: {selector}")
                            break
                
                if not submit_button:
                    logger.warning("❌ Submit button not found")
                    await browser.close()
                    return {'success': False, 'error': 'Submit button not found'}
                
                # Click the submit button
                logger.info("🚀 Clicking submit button...")
                await submit_button.click()
                
                # Wait for results to load
                logger.info("⏳ Waiting for tracking results...")
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(5000)  # Wait for Angular to process
                
                # Parse results
                content = await page.content()
                await browser.close()
                
                return self.parse_tracking_results(content, tracking_number)
                
        except Exception as e:
            logger.error(f"Playwright tracking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_with_selenium(self, tracking_number: str) -> Dict:
        """Track using Selenium with Apple Silicon ChromeDriver and Angular Material form handling"""
        driver = None
        try:
            driver = self.get_apple_silicon_chrome_driver()
            
            # Navigate to tracking page
            logger.info("🌐 Navigating to Estes tracking page...")
            driver.get('https://www.estes-express.com/myestes/shipment-tracking/')
            
            # Wait for Angular app to load
            logger.info("⏳ Waiting for Angular app to load...")
            time.sleep(8)  # Give Angular time to initialize
            
            # Look for the Angular Material form
            logger.info("🔍 Looking for Angular Material tracking form...")
            
            # Try to find the form container first
            try:
                form_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'shipmentTrackingFormContainer'))
                )
                logger.info("✅ Found form container")
            except:
                logger.warning("❌ Form container not found")
                return {'success': False, 'error': 'Angular form container not found'}
            
            # Look for the textarea within the Angular Material form
            textarea_selectors = [
                (By.CSS_SELECTOR, 'textarea[placeholder*="track"]'),
                (By.CSS_SELECTOR, 'textarea[placeholder*="number"]'),
                (By.CSS_SELECTOR, 'textarea[name*="track"]'),
                (By.CSS_SELECTOR, 'textarea[id*="track"]'),
                (By.TAG_NAME, 'textarea'),  # Fallback to any textarea
                (By.CSS_SELECTOR, 'mat-form-field textarea'),
                (By.CSS_SELECTOR, '.mat-mdc-form-field textarea')
            ]
            
            tracking_textarea = None
            for by_method, selector in textarea_selectors:
                try:
                    tracking_textarea = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    if tracking_textarea.is_displayed():
                        logger.info(f"✅ Found tracking textarea with selector: {selector}")
                        break
                except:
                    continue
            
            if not tracking_textarea:
                logger.warning("❌ No tracking textarea found")
                return {'success': False, 'error': 'Tracking textarea not found in Angular form'}
            
            # Enter the tracking number
            logger.info(f"📝 Entering tracking number: {tracking_number}")
            tracking_textarea.click()
            tracking_textarea.clear()
            tracking_textarea.send_keys(tracking_number)
            
            # Look for the submit button
            logger.info("🔍 Looking for submit button...")
            submit_button = None
            try:
                submit_button = driver.find_element(By.ID, 'shipmentTrackingSubmitButton')
                logger.info("✅ Found submit button by ID")
            except:
                # Try alternative selectors
                submit_selectors = [
                    (By.CSS_SELECTOR, 'button[type="submit"]'),
                    (By.XPATH, '//button[contains(text(), "Search")]'),
                    (By.XPATH, '//button[contains(text(), "Track")]'),
                    (By.CSS_SELECTOR, '.btn-primary')
                ]
                for by_method, selector in submit_selectors:
                    try:
                        submit_button = driver.find_element(by_method, selector)
                        logger.info(f"✅ Found submit button with selector: {selector}")
                        break
                    except:
                        continue
            
            if not submit_button:
                logger.warning("❌ Submit button not found")
                return {'success': False, 'error': 'Submit button not found'}
            
            # Click the submit button
            logger.info("🚀 Clicking submit button...")
            submit_button.click()
            
            # Wait for results to load
            logger.info("⏳ Waiting for tracking results...")
            time.sleep(8)  # Wait for Angular to process
            
            # Parse results
            page_source = driver.page_source
            return self.parse_tracking_results(page_source, tracking_number)
            
        except Exception as e:
            logger.error(f"Selenium tracking failed: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def track_with_mobile_api(self, tracking_number: str) -> Dict:
        """Track using mobile API endpoints"""
        try:
            mobile_endpoints = [
                f"https://mobile.estes-express.com/api/track/{tracking_number}",
                f"https://m.estes-express.com/api/tracking/{tracking_number}",
                f"https://api.estes-express.com/v1/tracking/{tracking_number}",
                f"https://www.estes-express.com/api/shipment-tracking/{tracking_number}"
            ]
            
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://mobile.estes-express.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            for endpoint in mobile_endpoints:
                try:
                    response = self.session.get(endpoint, headers=mobile_headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data and 'tracking' in str(data).lower():
                                return self.parse_api_response(data, tracking_number)
                        except:
                            # Try parsing HTML response
                            return self.parse_tracking_results(response.text, tracking_number)
                except Exception as e:
                    logger.warning(f"Mobile API endpoint {endpoint} failed: {e}")
                    continue
            
            return {'success': False, 'error': 'All mobile API endpoints failed'}
            
        except Exception as e:
            logger.error(f"Mobile API tracking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def parse_tracking_results(self, html_content: str, tracking_number: str) -> Dict:
        """Parse tracking results from HTML content"""
        try:
            # Look for tracking information patterns
            tracking_patterns = [
                r'delivered|delivery|out for delivery|in transit|picked up|origin|destination',
                r'status.*?:.*?([^<\n]+)',
                r'location.*?:.*?([^<\n]+)',
                r'date.*?:.*?([^<\n]+)',
                r'time.*?:.*?([^<\n]+)'
            ]
            
            import re
            results = []
            for pattern in tracking_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                results.extend(matches)
            
            if results:
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'carrier': 'Estes Express',
                    'status': results[0] if results else 'Unknown',
                    'details': results,
                    'raw_data': html_content[:1000]  # First 1000 chars for debugging
                }
            
            # Check for error messages
            error_patterns = [
                r'not found|invalid|error|unable to track',
                r'no.*?information.*?available',
                r'tracking.*?number.*?not.*?found'
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    return {
                        'success': False,
                        'error': 'Tracking number not found or invalid',
                        'tracking_number': tracking_number
                    }
            
            return {
                'success': False,
                'error': 'No tracking information found in response',
                'tracking_number': tracking_number
            }
            
        except Exception as e:
            logger.error(f"Failed to parse tracking results: {e}")
            return {'success': False, 'error': str(e)}
    
    def parse_api_response(self, data: Dict, tracking_number: str) -> Dict:
        """Parse API response data"""
        try:
            # Extract tracking information from API response
            if isinstance(data, dict):
                # Look for common API response patterns
                status = data.get('status') or data.get('shipmentStatus') or data.get('trackingStatus')
                location = data.get('location') or data.get('currentLocation') or data.get('lastLocation')
                
                if status or location:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'Estes Express',
                        'status': status or 'Unknown',
                        'location': location,
                        'api_data': data
                    }
            
            return {
                'success': False,
                'error': 'Could not parse API response',
                'tracking_number': tracking_number
            }
            
        except Exception as e:
            logger.error(f"Failed to parse API response: {e}")
            return {'success': False, 'error': str(e)}
    
    async def track_shipment(self, tracking_number: str) -> Dict:
        """
        Main tracking method with 4-layer approach
        1. Playwright (ARM64 compatible)
        2. Selenium with Apple Silicon ChromeDriver
        3. Mobile API endpoints
        4. Direct HTTP requests
        """
        logger.info(f"Starting Apple Silicon Estes tracking for: {tracking_number}")
        
        methods = [
            ("Playwright", self.track_with_playwright),
            ("Selenium", lambda tn: self.track_with_selenium(tn)),
            ("Mobile API", self.track_with_mobile_api),
            ("HTTP Requests", self.track_with_http)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} method...")
                
                if method_name == "Playwright":
                    result = await method_func(tracking_number)
                else:
                    result = method_func(tracking_number)
                
                if result.get('success'):
                    logger.info(f"✅ {method_name} method succeeded")
                    return result
                else:
                    logger.warning(f"❌ {method_name} method failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ {method_name} method error: {e}")
                continue
        
        return {
            'success': False,
            'error': 'All tracking methods failed',
            'tracking_number': tracking_number,
            'carrier': 'Estes Express'
        }
    
    def track_with_http(self, tracking_number: str) -> Dict:
        """Fallback HTTP tracking method"""
        try:
            # Try direct form submission
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            
            # Get the page first
            response = self.session.get(tracking_url)
            if response.status_code != 200:
                return {'success': False, 'error': 'Could not access tracking page'}
            
            # Look for form data in the page
            import re
            csrf_match = re.search(r'name=["\']_token["\'].*?value=["\']([^"\']+)', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ''
            
            # Submit tracking form
            form_data = {
                'trackingNumber': tracking_number,
                '_token': csrf_token
            }
            
            response = self.session.post(tracking_url, data=form_data)
            if response.status_code == 200:
                return self.parse_tracking_results(response.text, tracking_number)
            
            return {'success': False, 'error': f'HTTP request failed: {response.status_code}'}
            
        except Exception as e:
            logger.error(f"HTTP tracking failed: {e}")
            return {'success': False, 'error': str(e)}

# Convenience function for async usage
async def track_estes_apple_silicon(tracking_number: str) -> Dict:
    """Track Estes Express shipment with Apple Silicon compatibility"""
    client = AppleSiliconEstesClient()
    return await client.track_shipment(tracking_number)

# Synchronous wrapper
def track_estes_sync(tracking_number: str) -> Dict:
    """Synchronous wrapper for Estes tracking"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(track_estes_apple_silicon(tracking_number))
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(track_estes_apple_silicon(tracking_number))
        finally:
            loop.close() 