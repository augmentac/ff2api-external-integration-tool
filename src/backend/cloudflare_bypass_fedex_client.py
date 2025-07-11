"""
CloudFlare Bypass FedEx Freight Tracking Client
Solves CloudFlare protection barriers with advanced TLS fingerprint spoofing
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, quote

import requests
from curl_cffi import requests as cf_requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class CloudFlareBypassFedExClient:
    """
    CloudFlare bypass FedEx Freight tracking client
    Uses curl-cffi for TLS fingerprint spoofing and advanced challenge solving
    """
    
    def __init__(self):
        self.session = cf_requests.Session()
        self.base_urls = [
            "https://www.fedex.com/",
            "https://www.fedex.com/en-us/",
            "https://www.fedex.com/fedextrack/",
            "https://mobile.fedex.com/",
            "https://api.fedex.com/"
        ]
        self.tracking_endpoints = [
            "https://www.fedex.com/fedextrack/",
            "https://www.fedex.com/apps/fedextrack/",
            "https://www.fedex.com/wtrk/track/",
            "https://api.fedex.com/track/v1/trackingnumbers",
            "https://mobile.fedex.com/track/",
            "https://www.fedex.com/en-us/tracking.html"
        ]
        self.setup_session()
    
    def setup_session(self):
        """Setup session with CloudFlare bypass headers and TLS fingerprinting"""
        # Use Chrome 120 TLS fingerprint to bypass CloudFlare
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        })
        
        # Set CloudFlare bypass options
        self.cf_options = {
            'impersonate': 'chrome120',  # Use Chrome 120 TLS fingerprint
            'timeout': 30,
            'verify': False,
            'allow_redirects': True,
            'max_redirects': 10
        }
    
    def get_cloudflare_bypass_session(self) -> cf_requests.Session:
        """Get a new curl-cffi session with CloudFlare bypass capabilities"""
        session = cf_requests.Session()
        
        # Randomize TLS fingerprint
        fingerprints = ['chrome120', 'chrome119', 'chrome118', 'edge120', 'safari17']
        fingerprint = random.choice(fingerprints)
        
        # Set impersonation
        session.impersonate = fingerprint
        
        # CloudFlare bypass headers
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': f'"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        return session
    
    def get_random_user_agent(self) -> str:
        """Get a random realistic user agent"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)
    
    def solve_cloudflare_challenge(self, url: str, max_retries: int = 3) -> Optional[cf_requests.Response]:
        """
        Solve CloudFlare challenge using curl-cffi with TLS fingerprinting
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting CloudFlare bypass (attempt {attempt + 1}/{max_retries})")
                
                # Get new session with randomized fingerprint
                session = self.get_cloudflare_bypass_session()
                
                # Add random delay to mimic human behavior
                time.sleep(random.uniform(1, 3))
                
                # Make request with CloudFlare bypass
                response = session.get(url, **self.cf_options)
                
                # Check if we got past CloudFlare
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for CloudFlare challenge indicators
                    cf_indicators = [
                        'checking your browser',
                        'cloudflare',
                        'ray id',
                        'challenge',
                        'security check',
                        'ddos protection'
                    ]
                    
                    if not any(indicator in content for indicator in cf_indicators):
                        logger.info("✅ CloudFlare bypass successful")
                        return response
                    else:
                        logger.warning(f"❌ CloudFlare challenge detected (attempt {attempt + 1})")
                        
                        # If we detect a challenge, wait longer before retry
                        if attempt < max_retries - 1:
                            wait_time = random.uniform(5, 10) * (attempt + 1)
                            logger.info(f"Waiting {wait_time:.1f}s before retry...")
                            time.sleep(wait_time)
                
                elif response.status_code == 403:
                    logger.warning(f"❌ CloudFlare blocked request (403) - attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(10, 20))
                        
                elif response.status_code == 503:
                    logger.warning(f"❌ CloudFlare service unavailable (503) - attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(15, 30))
                        
                else:
                    logger.warning(f"❌ Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"CloudFlare bypass error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(5, 10))
        
        logger.error("❌ All CloudFlare bypass attempts failed")
        return None
    
    async def track_with_playwright(self, tracking_number: str) -> Dict:
        """Track using Playwright with CloudFlare bypass and enhanced wait conditions"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False,  # Show browser for debugging
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-blink-features=AutomationControlled',
                        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                )
                
                page = await context.new_page()
                
                # Navigate to FedEx Freight tracking page
                logger.info("🌐 Navigating to FedEx Freight tracking page...")
                await page.goto('https://www.fedex.com/en-us/tracking.html')
                
                # Wait for CloudFlare and page to load
                logger.info("⏳ Waiting for CloudFlare bypass and page load...")
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(8000)  # Extended wait for CloudFlare + React initialization
                
                # Look for the tracking input field
                logger.info("🔍 Looking for tracking input field...")
                
                # Try multiple selectors for the tracking input
                tracking_input_selectors = [
                    'input[data-testid="TrackingNumberTextInput"]',
                    'input[name="trackingnumber"]',
                    'input[placeholder*="tracking"]',
                    'input[placeholder*="number"]',
                    'input[type="text"]',
                    '#trackingNumber',
                    '.tracking-input'
                ]
                
                tracking_input = None
                for selector in tracking_input_selectors:
                    try:
                        tracking_input = await page.wait_for_selector(selector, timeout=10000)
                        if tracking_input:
                            logger.info(f"✅ Found tracking input with selector: {selector}")
                            break
                    except:
                        continue
                
                if not tracking_input:
                    logger.warning("❌ No tracking input found")
                    await browser.close()
                    return {'success': False, 'error': 'Tracking input not found'}
                
                # Enter the tracking number
                logger.info(f"📝 Entering tracking number: {tracking_number}")
                await tracking_input.click()
                await tracking_input.fill(tracking_number)
                
                # Look for the submit button
                logger.info("🔍 Looking for submit button...")
                submit_button_selectors = [
                    'button[data-testid="TrackingNumberSubmit"]',
                    'button[type="submit"]',
                    'button:has-text("Track")',
                    'button:has-text("Search")',
                    '.track-button',
                    '.submit-button'
                ]
                
                submit_button = None
                for selector in submit_button_selectors:
                    try:
                        submit_button = await page.wait_for_selector(selector, timeout=5000)
                        if submit_button:
                            logger.info(f"✅ Found submit button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not submit_button:
                    logger.warning("❌ Submit button not found")
                    await browser.close()
                    return {'success': False, 'error': 'Submit button not found'}
                
                # Click the submit button
                logger.info("🚀 Clicking submit button...")
                await submit_button.click()
                
                # ENHANCED WAIT CONDITIONS: Wait for actual tracking results to load
                logger.info("⏳ Waiting for tracking results with enhanced detection...")
                
                # Wait for initial network activity to settle
                await page.wait_for_load_state('networkidle')
                
                # Wait for tracking results with multiple detection strategies
                tracking_data_loaded = False
                max_wait_time = 60  # Extended to 60 seconds for FedEx (CloudFlare + React + API calls)
                check_interval = 3  # Check every 3 seconds
                
                for attempt in range(max_wait_time // check_interval):
                    logger.info(f"🔍 Checking for tracking data (attempt {attempt + 1}/{max_wait_time // check_interval})...")
                    
                    # Strategy 1: Check for specific FedEx tracking result elements
                    fedex_result_selectors = [
                        '[data-testid*="tracking"]',
                        '[data-testid*="shipment"]',
                        '[data-testid*="delivery"]',
                        '.tracking-results',
                        '.shipment-details',
                        '.tracking-info',
                        '.delivery-status',
                        '.shipment-status',
                        '[class*="tracking-result"]',
                        '[class*="shipment-detail"]',
                        '.tracking-summary',
                        '.delivery-info',
                        '.freight-details',
                        '.tracking-container'
                    ]
                    
                    for selector in fedex_result_selectors:
                        try:
                            result_elements = await page.query_selector_all(selector)
                            for result_element in result_elements:
                                if await result_element.is_visible():
                                    text_content = await result_element.text_content()
                                    if text_content and len(text_content.strip()) > 15:
                                        # Check if it contains meaningful tracking data
                                        tracking_keywords = ['delivered', 'transit', 'pickup', 'destination', 'origin', 'status', 'freight', tracking_number]
                                        if any(keyword.lower() in text_content.lower() for keyword in tracking_keywords):
                                            logger.info(f"✅ Found tracking data in element: {selector}")
                                            tracking_data_loaded = True
                                            break
                            if tracking_data_loaded:
                                break
                        except:
                            continue
                    
                    if tracking_data_loaded:
                        break
                    
                    # Strategy 2: Check for disappearance of loading indicators
                    loading_selectors = [
                        '.loading',
                        '.spinner',
                        '[class*="loading"]',
                        '[class*="spinner"]',
                        '.progress',
                        '[aria-label*="loading"]',
                        '[data-testid*="loading"]',
                        '.fedex-loading'
                    ]
                    
                    loading_present = False
                    for selector in loading_selectors:
                        try:
                            loading_elements = await page.query_selector_all(selector)
                            for loading_element in loading_elements:
                                if await loading_element.is_visible():
                                    loading_present = True
                                    break
                            if loading_present:
                                break
                        except:
                            continue
                    
                    if not loading_present:
                        # No loading indicators, check if we have meaningful content
                        page_content = await page.content()
                        if tracking_number in page_content and len(page_content) > 15000:
                            # Page has substantial content including our tracking number
                            logger.info("✅ Loading indicators gone and substantial content present")
                            tracking_data_loaded = True
                            break
                    
                    # Strategy 3: Monitor for AJAX completion by checking network activity
                    try:
                        await page.wait_for_load_state('networkidle', timeout=3000)
                        # If we reach networkidle, check if we have tracking data
                        current_content = await page.content()
                        if tracking_number in current_content:
                            content_length = len(current_content)
                            if content_length > 20000:  # Substantial content suggests data loaded
                                # Check for FedEx-specific tracking indicators
                                fedex_indicators = ['shipment', 'delivery', 'status', 'location', 'tracking', 'freight', 'fedex']
                                indicator_count = sum(1 for indicator in fedex_indicators if indicator in current_content.lower())
                                if indicator_count >= 4:  # Multiple FedEx indicators suggest real data
                                    logger.info(f"✅ Network idle with FedEx tracking indicators ({content_length} chars, {indicator_count} indicators)")
                                    tracking_data_loaded = True
                                    break
                    except:
                        pass  # Timeout is expected, continue checking
                    
                    # Strategy 4: Check for specific FedEx tracking status messages
                    try:
                        # Look for common FedEx status messages
                        status_messages = [
                            'Delivered',
                            'In transit',
                            'Out for delivery',
                            'Picked up',
                            'At destination sort facility',
                            'Departed FedEx location',
                            'Arrived at FedEx location'
                        ]
                        
                        current_content = await page.content()
                        for status in status_messages:
                            if status.lower() in current_content.lower():
                                logger.info(f"✅ Found FedEx status message: {status}")
                                tracking_data_loaded = True
                                break
                        
                        if tracking_data_loaded:
                            break
                    except:
                        pass
                    
                    # Wait before next check
                    await page.wait_for_timeout(check_interval * 1000)
                
                if not tracking_data_loaded:
                    logger.warning(f"⚠️ Tracking data detection timeout after {max_wait_time} seconds, proceeding with available content")
                else:
                    logger.info("✅ Tracking data successfully detected and loaded")
                
                # Additional wait to ensure all data is fully rendered
                await page.wait_for_timeout(8000)
                
                # Parse results
                content = await page.content()
                await browser.close()
                
                return self.parse_tracking_results(content, tracking_number)
                
        except Exception as e:
            logger.error(f"Playwright CloudFlare bypass tracking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_with_curl_cffi(self, tracking_number: str) -> Dict:
        """Track using curl-cffi with CloudFlare bypass"""
        try:
            # Try multiple tracking endpoints
            for endpoint in self.tracking_endpoints:
                try:
                    logger.info(f"Trying FedEx endpoint: {endpoint}")
                    
                    # Solve CloudFlare challenge
                    response = self.solve_cloudflare_challenge(endpoint)
                    
                    if response and response.status_code == 200:
                        # Look for tracking form in the response
                        content = response.text
                        
                        # Try to find and submit tracking form
                        import re
                        
                        # Look for form action
                        form_action_match = re.search(r'<form[^>]+action=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
                        if form_action_match:
                            form_action = form_action_match.group(1)
                            if not form_action.startswith('http'):
                                form_action = urljoin(endpoint, form_action)
                            
                            # Look for CSRF token or other hidden fields
                            csrf_match = re.search(r'<input[^>]+name=["\']_token["\'][^>]+value=["\']([^"\']+)', content)
                            csrf_token = csrf_match.group(1) if csrf_match else ''
                            
                            # Submit tracking form
                            form_data = {
                                'trackingNumber': tracking_number,
                                'trackNums': tracking_number,
                                'data.trackingNumber': tracking_number
                            }
                            
                            if csrf_token:
                                form_data['_token'] = csrf_token
                            
                            # Get new session for form submission
                            session = self.get_cloudflare_bypass_session()
                            
                            # Submit form
                            response = session.post(form_action, data=form_data, **self.cf_options)
                            
                            if response.status_code == 200:
                                result = self.parse_tracking_results(response.text, tracking_number)
                                if result.get('success'):
                                    return result
                        
                        # Try direct API endpoints
                        api_endpoints = [
                            f"https://api.fedex.com/track/v1/trackingnumbers/{tracking_number}",
                            f"https://www.fedex.com/trackingCal/track/{tracking_number}",
                            f"https://www.fedex.com/wtrk/track/{tracking_number}"
                        ]
                        
                        for api_url in api_endpoints:
                            try:
                                session = self.get_cloudflare_bypass_session()
                                session.headers.update({
                                    'Accept': 'application/json, text/plain, */*',
                                    'Content-Type': 'application/json',
                                    'X-Requested-With': 'XMLHttpRequest'
                                })
                                
                                api_response = session.get(api_url, **self.cf_options)
                                if api_response.status_code == 200:
                                    try:
                                        data = api_response.json()
                                        result = self.parse_api_response(data, tracking_number)
                                        if result.get('success'):
                                            return result
                                    except:
                                        # Try parsing as HTML
                                        result = self.parse_tracking_results(api_response.text, tracking_number)
                                        if result.get('success'):
                                            return result
                                            
                            except Exception as e:
                                logger.warning(f"API endpoint {api_url} failed: {e}")
                                continue
                
                except Exception as e:
                    logger.warning(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            return {'success': False, 'error': 'All curl-cffi tracking attempts failed'}
            
        except Exception as e:
            logger.error(f"curl-cffi tracking failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def track_with_selenium_cf_bypass(self, tracking_number: str) -> Dict:
        """Track using Selenium with CloudFlare bypass"""
        driver = None
        try:
            # Get ChromeDriver
            chrome_driver_path = ChromeDriverManager().install()
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # CloudFlare bypass options
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Try FedEx tracking
            tracking_urls = [
                'https://www.fedex.com/fedextrack/',
                'https://www.fedex.com/en-us/tracking.html'
            ]
            
            for url in tracking_urls:
                try:
                    logger.info(f"Selenium trying: {url}")
                    driver.get(url)
                    
                    # Wait for potential CloudFlare challenge
                    time.sleep(10)
                    
                    # Check for CloudFlare challenge
                    page_source = driver.page_source.lower()
                    if any(indicator in page_source for indicator in ['checking your browser', 'cloudflare', 'ray id']):
                        logger.warning("CloudFlare challenge detected, waiting...")
                        time.sleep(15)
                    
                    # Look for tracking input
                    tracking_selectors = [
                        (By.NAME, 'trackingNumber'),
                        (By.ID, 'trackingNumber'),
                        (By.CSS_SELECTOR, 'input[name*="track"]'),
                        (By.CSS_SELECTOR, 'input[id*="track"]'),
                        (By.CSS_SELECTOR, 'input[placeholder*="track"]')
                    ]
                    
                    tracking_input = None
                    for by_method, selector in tracking_selectors:
                        try:
                            tracking_input = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((by_method, selector))
                            )
                            break
                        except:
                            continue
                    
                    if tracking_input:
                        tracking_input.clear()
                        tracking_input.send_keys(tracking_number)
                        
                        # Look for submit button
                        submit_selectors = [
                            (By.CSS_SELECTOR, 'button[type="submit"]'),
                            (By.CSS_SELECTOR, 'input[type="submit"]'),
                            (By.XPATH, '//button[contains(text(), "Track")]')
                        ]
                        
                        for by_method, selector in submit_selectors:
                            try:
                                submit_button = driver.find_element(by_method, selector)
                                submit_button.click()
                                break
                            except:
                                continue
                        
                        # Wait for results
                        time.sleep(10)
                        
                        # Parse results
                        page_source = driver.page_source
                        result = self.parse_tracking_results(page_source, tracking_number)
                        
                        if result.get('success'):
                            return result
                
                except Exception as e:
                    logger.warning(f"Selenium error with {url}: {e}")
                    continue
            
            return {'success': False, 'error': 'Selenium CloudFlare bypass failed'}
            
        except Exception as e:
            logger.error(f"Selenium CloudFlare bypass failed: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def parse_tracking_results(self, html_content: str, tracking_number: str) -> Dict:
        """Parse tracking results from HTML content"""
        try:
            import re
            
            # First, check if this is actually JavaScript code or HTML fragments
            javascript_indicators = [
                'gtm.js',
                'getElementsByTagName',
                'var f=d.',
                'function(',
                'window.',
                'document.',
                '.js',
                'script',
                '});',
                'var ',
                'let ',
                'const ',
                'function ',
                'return ',
                'if(',
                'for(',
                'while('
            ]
            
            # Check if content contains JavaScript indicators
            for indicator in javascript_indicators:
                if indicator in html_content:
                    logger.warning(f"Detected JavaScript code in response, rejecting: {indicator}")
                    return {
                        'success': False,
                        'error': 'Response contains JavaScript code instead of tracking data',
                        'tracking_number': tracking_number
                    }
            
            # Check if content is mostly HTML tags
            html_tag_count = len(re.findall(r'<[^>]+>', html_content))
            if html_tag_count > 10 and len(html_content) < 1000:
                logger.warning("Response appears to be HTML structure rather than tracking data")
                return {
                    'success': False,
                    'error': 'Response contains HTML structure instead of tracking data',
                    'tracking_number': tracking_number
                }
            
            # Look for actual tracking information patterns with better validation
            tracking_patterns = [
                # More specific patterns that require context
                r'(?:shipment|package|freight)\s+(?:delivered|delivery|out for delivery|in transit|picked up|shipped)',
                r'(?:status|current status):\s*([^<\n]+)',
                r'(?:location|current location):\s*([^<\n]+)',
                r'(?:delivery date|delivered on):\s*([^<\n]+)',
                r'(?:pickup date|picked up on):\s*([^<\n]+)',
                r'(?:estimated.*?delivery):\s*([^<\n]+)'
            ]
            
            results = []
            for pattern in tracking_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                results.extend(matches)
            
            # Also look for structured tracking data
            structured_patterns = [
                r'tracking\s*#?\s*' + re.escape(tracking_number) + r'.*?(?:delivered|in transit|picked up|shipped)',
                r'(?:delivered|in transit|picked up|shipped).*?' + re.escape(tracking_number)
            ]
            
            for pattern in structured_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                results.extend(matches)
            
            # Validate results to ensure they're meaningful
            valid_results = []
            for result in results:
                if isinstance(result, str):
                    # Skip if it looks like code
                    if any(code_indicator in result for code_indicator in ['var ', 'function', '.js', 'getElementsBy', 'document.']):
                        continue
                    # Skip if it's too short or too long
                    if len(result) < 3 or len(result) > 200:
                        continue
                    # Skip if it contains suspicious characters
                    if any(char in result for char in ['<', '>', '{', '}', ';', '()', 'var']):
                        continue
                    valid_results.append(result)
            
            if valid_results:
                return {
                    'success': True,
                    'tracking_number': tracking_number,
                    'carrier': 'FedEx Freight',
                    'status': valid_results[0] if valid_results else 'Unknown',
                    'details': valid_results,
                    'raw_data': html_content[:1000]
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
                'error': 'No valid tracking information found in response',
                'tracking_number': tracking_number
            }
            
        except Exception as e:
            logger.error(f"Failed to parse tracking results: {e}")
            return {'success': False, 'error': str(e)}
    
    def parse_api_response(self, data: Dict, tracking_number: str) -> Dict:
        """Parse API response data"""
        try:
            if isinstance(data, dict):
                # Look for common API response patterns
                status = data.get('status') or data.get('shipmentStatus') or data.get('trackingStatus')
                location = data.get('location') or data.get('currentLocation') or data.get('lastLocation')
                
                if status or location:
                    return {
                        'success': True,
                        'tracking_number': tracking_number,
                        'carrier': 'FedEx Freight',
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
        Main tracking method with CloudFlare bypass approach
        1. curl-cffi with TLS fingerprint spoofing
        2. Playwright with CloudFlare bypass
        3. Selenium with CloudFlare bypass
        4. Mobile endpoints
        """
        logger.info(f"Starting CloudFlare bypass FedEx tracking for: {tracking_number}")
        
        methods = [
            ("curl-cffi TLS Bypass", self.track_with_curl_cffi),
            ("Playwright CF Bypass", self.track_with_playwright),
            ("Selenium CF Bypass", lambda tn: self.track_with_selenium_cf_bypass(tn)),
            ("Mobile Endpoints", self.track_with_mobile_endpoints)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} method...")
                
                if method_name == "Playwright CF Bypass":
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
            'error': 'All CloudFlare bypass methods failed',
            'tracking_number': tracking_number,
            'carrier': 'FedEx Freight'
        }
    
    def track_with_mobile_endpoints(self, tracking_number: str) -> Dict:
        """Track using mobile endpoints with CloudFlare bypass"""
        try:
            mobile_endpoints = [
                f"https://mobile.fedex.com/track/{tracking_number}",
                f"https://m.fedex.com/us/track/{tracking_number}",
                f"https://api.fedex.com/track/v1/trackingnumbers/{tracking_number}",
                f"https://www.fedex.com/mobile/track/{tracking_number}"
            ]
            
            for endpoint in mobile_endpoints:
                try:
                    session = self.get_cloudflare_bypass_session()
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                        'Accept': 'application/json, text/plain, */*',
                        'Referer': 'https://mobile.fedex.com/'
                    })
                    
                    response = session.get(endpoint, **self.cf_options)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            result = self.parse_api_response(data, tracking_number)
                            if result.get('success'):
                                return result
                        except:
                            result = self.parse_tracking_results(response.text, tracking_number)
                            if result.get('success'):
                                return result
                                
                except Exception as e:
                    logger.warning(f"Mobile endpoint {endpoint} failed: {e}")
                    continue
            
            return {'success': False, 'error': 'All mobile endpoints failed'}
            
        except Exception as e:
            logger.error(f"Mobile endpoints tracking failed: {e}")
            return {'success': False, 'error': str(e)}

# Convenience function for async usage
async def track_fedex_cloudflare_bypass(tracking_number: str) -> Dict:
    """Track FedEx Freight shipment with CloudFlare bypass"""
    client = CloudFlareBypassFedExClient()
    return await client.track_shipment(tracking_number)

# Synchronous wrapper
def track_fedex_sync(tracking_number: str) -> Dict:
    """Synchronous wrapper for FedEx tracking"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(track_fedex_cloudflare_bypass(tracking_number))
    except RuntimeError:
        # Create new event loop if none exists
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(track_fedex_cloudflare_bypass(tracking_number))
        finally:
            loop.close() 