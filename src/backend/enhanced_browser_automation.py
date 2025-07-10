#!/usr/bin/env python3
"""
Enhanced Browser Automation Module

This module implements advanced browser automation techniques to overcome
sophisticated anti-scraping measures used by Estes and FedEx.
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re

# Core imports
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Browser automation imports
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium_stealth import stealth
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

# Advanced networking
import cloudscraper
import httpx
import aiohttp

logger = logging.getLogger(__name__)

class EnhancedBrowserAutomation:
    """Advanced browser automation with multiple fallback engines"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
        self.session_cache = {}
        
    async def create_stealth_session(self, target: str = "generic") -> Dict[str, Any]:
        """Create a stealth session optimized for the target"""
        
        if target in self.session_cache:
            return self.session_cache[target]
        
        # Try Playwright first (most advanced)
        if PLAYWRIGHT_AVAILABLE:
            try:
                session = await self._create_playwright_session(target)
                self.session_cache[target] = session
                return session
            except Exception as e:
                self.logger.warning(f"Playwright session failed: {e}")
        
        # Fallback to Selenium with stealth
        if SELENIUM_AVAILABLE:
            try:
                session = await self._create_selenium_session(target)
                self.session_cache[target] = session
                return session
            except Exception as e:
                self.logger.warning(f"Selenium session failed: {e}")
        
        # Fallback to requests-html
        if REQUESTS_HTML_AVAILABLE:
            try:
                session = await self._create_requests_html_session(target)
                self.session_cache[target] = session
                return session
            except Exception as e:
                self.logger.warning(f"Requests-HTML session failed: {e}")
        
        # Final fallback to cloudscraper
        session = await self._create_cloudscraper_session(target)
        self.session_cache[target] = session
        return session
    
    async def _create_playwright_session(self, target: str) -> Dict[str, Any]:
        """Create Playwright session with advanced stealth"""
        
        playwright = await async_playwright().start()
        
        # Advanced browser configuration
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-background-networking',
                '--enable-features=NetworkService,NetworkServiceLogging',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-client-side-phishing-detection',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--disable-extensions'
            ]
        )
        
        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self._get_realistic_user_agent(target),
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            extra_http_headers=self._get_realistic_headers(target)
        )
        
        # Add stealth scripts
        await context.add_init_script(self._get_stealth_script())
        
        page = await context.new_page()
        
        return {
            'type': 'playwright',
            'playwright': playwright,
            'browser': browser,
            'context': context,
            'page': page
        }
    
    async def _create_selenium_session(self, target: str) -> Dict[str, Any]:
        """Create Selenium session with stealth patches"""
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={self._get_realistic_user_agent(target)}')
        
        # Additional stealth options
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        driver = webdriver.Chrome(options=options)
        
        # Apply stealth patches
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="MacIntel",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        return {
            'type': 'selenium',
            'driver': driver
        }
    
    async def _create_requests_html_session(self, target: str) -> Dict[str, Any]:
        """Create requests-html session"""
        
        session = HTMLSession()
        session.headers.update(self._get_realistic_headers(target))
        
        return {
            'type': 'requests_html',
            'session': session
        }
    
    async def _create_cloudscraper_session(self, target: str) -> Dict[str, Any]:
        """Create cloudscraper session for CloudFlare bypass"""
        
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'darwin',
                'desktop': True
            },
            debug=False
        )
        
        scraper.headers.update(self._get_realistic_headers(target))
        
        return {
            'type': 'cloudscraper',
            'session': scraper
        }
    
    def _get_realistic_user_agent(self, target: str) -> str:
        """Get realistic user agent for target"""
        
        if target.lower() == 'estes':
            # Use Chrome on macOS (common for business users)
            return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        elif target.lower() == 'fedex':
            # Use Chrome on Windows (common for shipping)
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        else:
            return self.ua.chrome
    
    def _get_realistic_headers(self, target: str) -> Dict[str, str]:
        """Get realistic headers for target"""
        
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        if target.lower() == 'estes':
            base_headers.update({
                'Sec-CH-UA': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"macOS"'
            })
        elif target.lower() == 'fedex':
            base_headers.update({
                'Sec-CH-UA': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"'
            })
        
        return base_headers
    
    def _get_stealth_script(self) -> str:
        """Get comprehensive stealth JavaScript"""
        
        return """
        // Remove webdriver traces
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', description: '', filename: 'internal-nacl-plugin'}
            ]
        });
        
        // Spoof languages
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        
        // Add chrome runtime
        window.chrome = {runtime: {}};
        
        // Spoof permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Spoof WebGL
        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter(parameter);
        };
        
        // Remove automation indicators
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """
    
    async def navigate_with_stealth(self, session: Dict[str, Any], url: str, wait_for: Optional[str] = None) -> str:
        """Navigate to URL with stealth techniques"""
        
        session_type = session['type']
        
        if session_type == 'playwright':
            return await self._playwright_navigate(session, url, wait_for)
        elif session_type == 'selenium':
            return await self._selenium_navigate(session, url, wait_for)
        elif session_type == 'requests_html':
            return await self._requests_html_navigate(session, url, wait_for)
        elif session_type == 'cloudscraper':
            return await self._cloudscraper_navigate(session, url, wait_for)
        else:
            raise ValueError(f"Unknown session type: {session_type}")
    
    async def _playwright_navigate(self, session: Dict[str, Any], url: str, wait_for: Optional[str] = None) -> str:
        """Navigate using Playwright"""
        
        page = session['page']
        
        # Random delay before navigation
        await asyncio.sleep(random.uniform(1, 3))
        
        # Navigate with realistic timing
        await page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Wait for specific element if provided
        if wait_for:
            try:
                await page.wait_for_selector(wait_for, timeout=15000)
            except:
                pass
        
        # Random human-like delay
        await asyncio.sleep(random.uniform(2, 5))
        
        # Get page content
        content = await page.content()
        return content
    
    async def _selenium_navigate(self, session: Dict[str, Any], url: str, wait_for: Optional[str] = None) -> str:
        """Navigate using Selenium"""
        
        driver = session['driver']
        
        # Random delay before navigation
        time.sleep(random.uniform(1, 3))
        
        # Navigate
        driver.get(url)
        
        # Wait for specific element if provided
        if wait_for:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            except:
                pass
        
        # Random human-like delay
        time.sleep(random.uniform(2, 5))
        
        # Get page content
        content = driver.page_source
        return content
    
    async def _requests_html_navigate(self, session: Dict[str, Any], url: str, wait_for: Optional[str] = None) -> str:
        """Navigate using requests-html"""
        
        html_session = session['session']
        
        # Random delay before navigation
        await asyncio.sleep(random.uniform(1, 3))
        
        # Get page
        response = html_session.get(url, timeout=30)
        
        # Render JavaScript if needed
        if wait_for or 'estes' in url.lower():
            response.html.render(timeout=20, wait=2)
        
        return response.html.html
    
    async def _cloudscraper_navigate(self, session: Dict[str, Any], url: str, wait_for: Optional[str] = None) -> str:
        """Navigate using cloudscraper"""
        
        scraper = session['session']
        
        # Random delay before navigation
        await asyncio.sleep(random.uniform(1, 3))
        
        # Get page
        response = scraper.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    async def extract_tracking_data(self, session: Dict[str, Any], url: str, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Extract tracking data using multiple methods"""
        
        try:
            # Navigate to page
            content = await self.navigate_with_stealth(session, url)
            
            # Parse content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Try multiple extraction methods
            if carrier.lower() == 'estes':
                return await self._extract_estes_data(session, soup, pro_number, content)
            elif 'fedex' in carrier.lower():
                return await self._extract_fedex_data(session, soup, pro_number, content)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Tracking extraction failed: {e}")
            return None
    
    async def _extract_estes_data(self, session: Dict[str, Any], soup: BeautifulSoup, pro_number: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract Estes tracking data using multiple methods"""
        
        # Method 1: Look for tracking results in DOM
        tracking_selectors = [
            '.tracking-results',
            '.shipment-details',
            '.tracking-info',
            '[data-testid="tracking-results"]',
            '.tracking-summary',
            '.shipment-status'
        ]
        
        for selector in tracking_selectors:
            elements = soup.select(selector)
            if elements:
                tracking_text = elements[0].get_text(strip=True)
                if tracking_text and pro_number in tracking_text:
                    return self._parse_estes_tracking_text(tracking_text, pro_number)
        
        # Method 2: Extract from JavaScript variables
        if session['type'] == 'playwright':
            js_data = await self._extract_js_variables(session)
            if js_data:
                return self._parse_estes_js_data(js_data, pro_number)
        
        # Method 3: Look for delivery patterns in text
        delivery_patterns = [
            r'Delivered\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+([A-Z\s,]+)',
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+Delivered\s+([A-Z\s,]+)'
        ]
        
        for pattern in delivery_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                match = matches[0]
                if len(match) >= 3:
                    return {
                        'status': 'success',
                        'pro_number': pro_number,
                        'carrier': 'Estes Express',
                        'tracking_status': f"Delivered {match[0]} {match[1]} at {match[2]}",
                        'tracking_location': match[2].strip(),
                        'tracking_event': f"Delivered on {match[0]} at {match[1]}",
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': 'enhanced_browser_automation'
                    }
        
        return None
    
    async def _extract_fedex_data(self, session: Dict[str, Any], soup: BeautifulSoup, pro_number: str, content: str) -> Optional[Dict[str, Any]]:
        """Extract FedEx tracking data using multiple methods"""
        
        # Method 1: Look for tracking results in DOM
        tracking_selectors = [
            '.tracking-details',
            '.shipment-progress',
            '.tracking-status',
            '[data-testid="tracking-details"]',
            '.package-details'
        ]
        
        for selector in tracking_selectors:
            elements = soup.select(selector)
            if elements:
                tracking_text = elements[0].get_text(strip=True)
                if tracking_text and pro_number in tracking_text:
                    return self._parse_fedex_tracking_text(tracking_text, pro_number)
        
        # Method 2: Extract from JavaScript variables
        if session['type'] == 'playwright':
            js_data = await self._extract_js_variables(session)
            if js_data:
                return self._parse_fedex_js_data(js_data, pro_number)
        
        # Method 3: Look for delivery patterns in text
        delivery_patterns = [
            r'Delivered\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+([A-Z\s,]+)',
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+.*?Delivered.*?([A-Z\s,]+)'
        ]
        
        for pattern in delivery_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                match = matches[0]
                if len(match) >= 3:
                    return {
                        'status': 'success',
                        'pro_number': pro_number,
                        'carrier': 'FedEx Freight',
                        'tracking_status': f"Delivered {match[0]} {match[1]} at {match[2]}",
                        'tracking_location': match[2].strip(),
                        'tracking_event': f"Delivered on {match[0]} at {match[1]}",
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': 'enhanced_browser_automation'
                    }
        
        return None
    
    async def _extract_js_variables(self, session: Dict[str, Any]) -> Optional[Dict]:
        """Extract JavaScript variables from page"""
        
        if session['type'] != 'playwright':
            return None
        
        page = session['page']
        
        try:
            # Try to extract common tracking data variables
            js_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Common variable names for tracking data
                    const varNames = [
                        'trackingData', 'shipmentData', 'trackingInfo',
                        '__INITIAL_STATE__', 'window.trackingData',
                        'pageData', 'shipmentInfo', 'trackingResults'
                    ];
                    
                    for (const varName of varNames) {
                        try {
                            const value = eval(varName);
                            if (value) {
                                data[varName] = value;
                            }
                        } catch (e) {
                            // Variable doesn't exist
                        }
                    }
                    
                    return Object.keys(data).length > 0 ? data : null;
                }
            """)
            
            return js_data
            
        except Exception as e:
            self.logger.debug(f"JavaScript extraction failed: {e}")
            return None
    
    def _parse_estes_tracking_text(self, text: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse Estes tracking text"""
        
        # Look for delivery information
        if 'delivered' in text.lower():
            return {
                'status': 'success',
                'pro_number': pro_number,
                'carrier': 'Estes Express',
                'tracking_status': 'Delivered',
                'tracking_event': text[:200],  # First 200 chars
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'estes_text_parsing'
            }
        
        return None
    
    def _parse_fedex_tracking_text(self, text: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse FedEx tracking text"""
        
        # Look for delivery information
        if 'delivered' in text.lower():
            return {
                'status': 'success',
                'pro_number': pro_number,
                'carrier': 'FedEx Freight',
                'tracking_status': 'Delivered',
                'tracking_event': text[:200],  # First 200 chars
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'fedex_text_parsing'
            }
        
        return None
    
    def _parse_estes_js_data(self, js_data: Dict, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse Estes JavaScript data"""
        
        # Recursively search for tracking information
        def search_object(obj, target_pro):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if target_pro in str(value):
                        return obj
                    result = search_object(value, target_pro)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = search_object(item, target_pro)
                    if result:
                        return result
            return None
        
        tracking_obj = search_object(js_data, pro_number)
        if tracking_obj:
            return {
                'status': 'success',
                'pro_number': pro_number,
                'carrier': 'Estes Express',
                'tracking_status': 'Data found in JavaScript',
                'tracking_event': str(tracking_obj)[:200],
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'estes_js_parsing'
            }
        
        return None
    
    def _parse_fedex_js_data(self, js_data: Dict, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse FedEx JavaScript data"""
        
        # Similar to Estes but for FedEx structure
        def search_object(obj, target_pro):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if target_pro in str(value):
                        return obj
                    result = search_object(value, target_pro)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = search_object(item, target_pro)
                    if result:
                        return result
            return None
        
        tracking_obj = search_object(js_data, pro_number)
        if tracking_obj:
            return {
                'status': 'success',
                'pro_number': pro_number,
                'carrier': 'FedEx Freight',
                'tracking_status': 'Data found in JavaScript',
                'tracking_event': str(tracking_obj)[:200],
                'tracking_timestamp': datetime.now().isoformat(),
                'extracted_from': 'fedex_js_parsing'
            }
        
        return None
    
    async def cleanup_session(self, session: Dict[str, Any]):
        """Clean up session resources"""
        
        session_type = session['type']
        
        try:
            if session_type == 'playwright':
                await session['context'].close()
                await session['browser'].close()
                await session['playwright'].stop()
            elif session_type == 'selenium':
                session['driver'].quit()
            elif session_type == 'requests_html':
                session['session'].close()
            elif session_type == 'cloudscraper':
                session['session'].close()
        except Exception as e:
            self.logger.debug(f"Session cleanup error: {e}")
    
    async def cleanup_all_sessions(self):
        """Clean up all cached sessions"""
        
        for session in self.session_cache.values():
            await self.cleanup_session(session)
        
        self.session_cache.clear() 