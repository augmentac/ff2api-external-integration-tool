#!/usr/bin/env python3
"""
Cloud Browser Tracking System
Uses headless browsers that work in cloud environments
Adapts the successful browser automation methods for cloud deployment
"""

import asyncio
import os
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re

# Try to import playwright for cloud-compatible browser automation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Try to import selenium for fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

class CloudBrowserTracker:
    """
    Cloud-compatible browser tracking system
    Uses headless browsers that work in cloud environments
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
        # Detect cloud environment
        self.is_cloud = self.detect_cloud_environment()
        logger.info(f"Cloud environment detected: {self.is_cloud}")
        
    def detect_cloud_environment(self) -> bool:
        """Detect if we're running in a cloud environment"""
        cloud_indicators = [
            'STREAMLIT_CLOUD',
            'HEROKU',
            'DYNO',
            'RAILWAY',
            'VERCEL',
            'NETLIFY',
            'AWS_LAMBDA',
            'GOOGLE_CLOUD_RUN'
        ]
        
        for indicator in cloud_indicators:
            if os.environ.get(indicator):
                return True
        
        # Check hostname patterns
        hostname = os.environ.get('HOSTNAME', '').lower()
        if any(pattern in hostname for pattern in ['streamlit', 'heroku', 'railway', 'vercel']):
            return True
        
        return False
    
    def setup_session(self):
        """Setup HTTP session with realistic headers"""
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
    
    async def track_shipment(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """
        Main tracking method that uses cloud-compatible browser automation
        """
        logger.info(f"🌐 Cloud browser tracking: {carrier} - {tracking_number}")
        
        # Route to appropriate carrier method
        if "estes" in carrier.lower():
            return await self.track_estes_browser(tracking_number)
        elif "fedex" in carrier.lower():
            return await self.track_fedex_browser(tracking_number)
        elif "peninsula" in carrier.lower():
            return await self.track_peninsula_browser(tracking_number)
        elif "r&l" in carrier.lower():
            return await self.track_rl_browser(tracking_number)
        else:
            return await self.track_generic_browser(tracking_number, carrier)
    
    async def track_estes_browser(self, tracking_number: str) -> Dict[str, Any]:
        """
        Track Estes using cloud-compatible browser automation
        """
        logger.info(f"📦 Cloud browser tracking Estes: {tracking_number}")
        
        # Try Playwright first (better cloud compatibility)
        if PLAYWRIGHT_AVAILABLE:
            try:
                result = await self.track_estes_playwright(tracking_number)
                if result.get('success'):
                    logger.info("✅ Playwright Estes tracking successful")
                    return result
                else:
                    logger.warning(f"Playwright failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Playwright error: {e}")
        
        # Try Selenium as fallback
        if SELENIUM_AVAILABLE:
            try:
                result = await self.track_estes_selenium_cloud(tracking_number)
                if result.get('success'):
                    logger.info("✅ Selenium Estes tracking successful")
                    return result
                else:
                    logger.warning(f"Selenium failed: {result.get('error')}")
            except Exception as e:
                logger.warning(f"Selenium error: {e}")
        
        # If browser automation fails, try HTTP methods
        try:
            result = await self.track_estes_http_advanced(tracking_number)
            if result.get('success'):
                logger.info("✅ Advanced HTTP Estes tracking successful")
                return result
        except Exception as e:
            logger.warning(f"Advanced HTTP error: {e}")
        
        return {
            'success': False,
            'error': 'All cloud browser tracking methods failed',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': 'Estes Express',
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_estes_playwright(self, tracking_number: str) -> Dict[str, Any]:
        """
        Track Estes using Playwright (cloud-compatible)
        """
        try:
            async with async_playwright() as p:
                # Use Chromium with cloud-optimized settings
                browser = await p.chromium.launch(
                    headless=True,  # Always headless for cloud
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-extensions',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--disable-ipc-flooding-protection',
                        '--disable-software-rasterizer',
                        '--disable-background-networking',
                        '--disable-default-apps',
                        '--disable-sync',
                        '--disable-translate',
                        '--hide-scrollbars',
                        '--metrics-recording-only',
                        '--mute-audio',
                        '--no-first-run',
                        '--safebrowsing-disable-auto-update',
                        '--single-process',  # Important for cloud environments
                        '--disable-setuid-sandbox'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Navigate to tracking page
                logger.info("🌐 Navigating to Estes tracking page...")
                await page.goto('https://www.estes-express.com/myestes/shipment-tracking/', wait_until='networkidle')
                
                # Wait for Angular app to load
                logger.info("⏳ Waiting for Angular app to load...")
                await page.wait_for_timeout(10000)  # 10 second wait for Angular
                
                # Look for tracking form
                logger.info("🔍 Looking for tracking form...")
                
                # Try multiple selectors for the tracking input
                input_selectors = [
                    'textarea[placeholder*="track"]',
                    'textarea[placeholder*="number"]',
                    'textarea[name*="track"]',
                    'textarea[id*="track"]',
                    'textarea',
                    'input[type="text"]',
                    'mat-form-field textarea',
                    '.mat-mdc-form-field textarea'
                ]
                
                tracking_input = None
                for selector in input_selectors:
                    try:
                        tracking_input = await page.wait_for_selector(selector, timeout=5000)
                        if tracking_input:
                            logger.info(f"✅ Found tracking input: {selector}")
                            break
                    except:
                        continue
                
                if not tracking_input:
                    await browser.close()
                    return {'success': False, 'error': 'Tracking input not found'}
                
                # Enter tracking number
                logger.info(f"📝 Entering tracking number: {tracking_number}")
                await tracking_input.click()
                await tracking_input.fill(tracking_number)
                
                # Find and click submit button
                logger.info("🔍 Looking for submit button...")
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Search")',
                    'button:has-text("Track")',
                    '.btn-primary',
                    '#shipmentTrackingSubmitButton'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = await page.query_selector(selector)
                        if submit_button:
                            logger.info(f"✅ Found submit button: {selector}")
                            break
                    except:
                        continue
                
                if not submit_button:
                    await browser.close()
                    return {'success': False, 'error': 'Submit button not found'}
                
                # Click submit and wait for results
                logger.info("🚀 Submitting tracking form...")
                await submit_button.click()
                
                # Wait for tracking results with enhanced detection
                logger.info("⏳ Waiting for tracking results...")
                await page.wait_for_load_state('networkidle')
                
                # Wait for content to load
                max_wait = 30
                for i in range(max_wait):
                    content = await page.content()
                    if tracking_number in content and len(content) > 15000:
                        logger.info(f"✅ Tracking data loaded after {i+1} seconds")
                        break
                    await page.wait_for_timeout(1000)
                
                # Get final content and parse
                final_content = await page.content()
                await browser.close()
                
                return self.parse_estes_tracking_results(final_content, tracking_number)
                
        except Exception as e:
            logger.error(f"Playwright Estes tracking failed: {e}")
            return {'success': False, 'error': f'Playwright error: {str(e)}'}
    
    async def track_estes_selenium_cloud(self, tracking_number: str) -> Dict[str, Any]:
        """
        Track Estes using Selenium with cloud-optimized settings
        """
        driver = None
        try:
            # Cloud-optimized Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--disable-software-rasterizer')
            
            # Try to use ChromeDriver
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"ChromeDriverManager failed: {e}")
                # Try system ChromeDriver
                driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to tracking page
            logger.info("🌐 Navigating to Estes tracking page...")
            driver.get('https://www.estes-express.com/myestes/shipment-tracking/')
            
            # Wait for page to load
            time.sleep(10)
            
            # Find tracking input
            logger.info("🔍 Looking for tracking input...")
            tracking_input = None
            input_selectors = [
                (By.CSS_SELECTOR, 'textarea[placeholder*="track"]'),
                (By.CSS_SELECTOR, 'textarea[placeholder*="number"]'),
                (By.CSS_SELECTOR, 'textarea'),
                (By.CSS_SELECTOR, 'input[type="text"]'),
                (By.TAG_NAME, 'textarea')
            ]
            
            for by_method, selector in input_selectors:
                try:
                    tracking_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    logger.info(f"✅ Found tracking input: {selector}")
                    break
                except:
                    continue
            
            if not tracking_input:
                return {'success': False, 'error': 'Tracking input not found'}
            
            # Enter tracking number
            logger.info(f"📝 Entering tracking number: {tracking_number}")
            tracking_input.click()
            tracking_input.clear()
            tracking_input.send_keys(tracking_number)
            
            # Find and click submit button
            logger.info("🔍 Looking for submit button...")
            submit_button = None
            submit_selectors = [
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.XPATH, '//button[contains(text(), "Search")]'),
                (By.XPATH, '//button[contains(text(), "Track")]'),
                (By.CSS_SELECTOR, '.btn-primary'),
                (By.ID, 'shipmentTrackingSubmitButton')
            ]
            
            for by_method, selector in submit_selectors:
                try:
                    submit_button = driver.find_element(by_method, selector)
                    logger.info(f"✅ Found submit button: {selector}")
                    break
                except:
                    continue
            
            if not submit_button:
                return {'success': False, 'error': 'Submit button not found'}
            
            # Click submit and wait for results
            logger.info("🚀 Submitting tracking form...")
            submit_button.click()
            
            # Wait for results to load
            logger.info("⏳ Waiting for tracking results...")
            time.sleep(15)  # Wait for AJAX to complete
            
            # Wait for content to appear
            max_wait = 30
            for i in range(max_wait):
                page_source = driver.page_source
                if tracking_number in page_source and len(page_source) > 15000:
                    logger.info(f"✅ Tracking data loaded after {i+1} seconds")
                    break
                time.sleep(1)
            
            # Get final page source and parse
            final_page_source = driver.page_source
            return self.parse_estes_tracking_results(final_page_source, tracking_number)
            
        except Exception as e:
            logger.error(f"Selenium Estes tracking failed: {e}")
            return {'success': False, 'error': f'Selenium error: {str(e)}'}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def track_estes_http_advanced(self, tracking_number: str) -> Dict[str, Any]:
        """
        Advanced HTTP tracking with session management and form parsing
        """
        try:
            # Step 1: Get the tracking page to establish session
            tracking_url = "https://www.estes-express.com/myestes/shipment-tracking/"
            logger.info("🌐 Getting tracking page...")
            
            response = self.session.get(tracking_url, timeout=15)
            if response.status_code != 200:
                return {'success': False, 'error': f'Could not access tracking page: {response.status_code}'}
            
            # Step 2: Parse the page for form data and tokens
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for CSRF tokens
            csrf_token = None
            csrf_inputs = soup.find_all('input', {'name': re.compile(r'.*token.*', re.I)})
            for input_elem in csrf_inputs:
                if input_elem.get('value'):
                    csrf_token = input_elem.get('value')
                    break
            
            # Look for form action
            form = soup.find('form')
            form_action = form.get('action') if form else None
            
            # Step 3: Submit tracking form
            logger.info("📝 Submitting tracking form...")
            
            form_data = {
                'trackingNumber': tracking_number,
                'proNumber': tracking_number,
                'shipmentNumber': tracking_number
            }
            
            if csrf_token:
                form_data['_token'] = csrf_token
                form_data['csrfToken'] = csrf_token
            
            # Set form-specific headers
            form_headers = {
                **self.session.headers,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.estes-express.com',
                'Referer': tracking_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Submit to form action or same URL
            submit_url = urljoin(tracking_url, form_action) if form_action else tracking_url
            
            response = self.session.post(submit_url, data=form_data, headers=form_headers, timeout=15)
            
            if response.status_code == 200:
                return self.parse_estes_tracking_results(response.text, tracking_number)
            else:
                return {'success': False, 'error': f'Form submission failed: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Advanced HTTP tracking failed: {e}")
            return {'success': False, 'error': f'Advanced HTTP error: {str(e)}'}
    
    def parse_estes_tracking_results(self, html_content: str, tracking_number: str) -> Dict[str, Any]:
        """
        Parse Estes tracking results from HTML content
        Enhanced version with better data extraction
        """
        try:
            # Check if tracking number is in content
            if tracking_number not in html_content:
                return {
                    'success': False,
                    'error': 'Tracking number not found in response',
                    'status': 'No status available',
                    'location': 'No location available',
                    'events': []
                }
            
            logger.info(f"✅ Tracking number {tracking_number} found in response")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize tracking data
            tracking_data = {
                'success': True,
                'status': 'Tracking data found',
                'location': 'Location data available',
                'events': [],
                'carrier': 'Estes Express',
                'tracking_number': tracking_number,
                'timestamp': time.time()
            }
            
            # Extract tracking events
            events = []
            latest_status = None
            latest_location = None
            
            # Look for table rows with tracking data
            rows = soup.find_all('tr')
            for row in rows:
                row_text = row.get_text(strip=True)
                
                # Look for date patterns
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', row_text)
                if date_match and any(keyword in row_text.lower() for keyword in ['delivered', 'transit', 'pickup', 'origin', 'destination']):
                    event_data = {
                        'date': date_match.group(1),
                        'description': row_text
                    }
                    
                    # Extract status
                    status_keywords = ['delivered', 'out for delivery', 'in transit', 'picked up', 'at origin', 'at destination']
                    for keyword in status_keywords:
                        if keyword in row_text.lower():
                            event_data['status'] = keyword.title()
                            latest_status = keyword.title()
                            break
                    
                    # Extract location
                    location_match = re.search(r'([A-Z][a-z]+,\s*[A-Z]{2})', row_text)
                    if location_match:
                        event_data['location'] = location_match.group(1)
                        latest_location = location_match.group(1)
                    
                    events.append(event_data)
            
            # Update tracking data
            if events:
                tracking_data['events'] = events
                tracking_data['status'] = latest_status or 'Tracking events found'
                tracking_data['location'] = latest_location or 'Location data found'
                logger.info(f"✅ Extracted {len(events)} tracking events")
            else:
                # Even if no structured events, we found the tracking number
                tracking_data['status'] = 'Tracking number found in system'
                tracking_data['location'] = 'Data available in system'
                logger.info("✅ Tracking number found, but no structured events extracted")
            
            return tracking_data
            
        except Exception as e:
            logger.error(f"Error parsing Estes tracking results: {e}")
            return {
                'success': False,
                'error': f'Parsing error: {str(e)}',
                'status': 'No status available',
                'location': 'No location available',
                'events': []
            }
    
    # Placeholder methods for other carriers
    async def track_fedex_browser(self, tracking_number: str) -> Dict[str, Any]:
        """FedEx browser tracking - to be implemented"""
        return {
            'success': False,
            'error': 'FedEx browser tracking not yet implemented',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': 'FedEx Freight',
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_peninsula_browser(self, tracking_number: str) -> Dict[str, Any]:
        """Peninsula browser tracking - to be implemented"""
        return {
            'success': False,
            'error': 'Peninsula browser tracking not yet implemented',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': 'Peninsula Truck Lines',
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_rl_browser(self, tracking_number: str) -> Dict[str, Any]:
        """R&L browser tracking - to be implemented"""
        return {
            'success': False,
            'error': 'R&L browser tracking not yet implemented',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': 'R&L Carriers',
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }
    
    async def track_generic_browser(self, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """Generic browser tracking"""
        return {
            'success': False,
            'error': f'Browser tracking not implemented for {carrier}',
            'status': 'No status available',
            'location': 'No location available',
            'events': [],
            'carrier': carrier,
            'tracking_number': tracking_number,
            'timestamp': time.time()
        }

# Async wrapper for compatibility
async def track_shipment_browser(tracking_number: str, carrier: str) -> Dict[str, Any]:
    """
    Main async function for cloud browser tracking
    """
    tracker = CloudBrowserTracker()
    return await tracker.track_shipment(tracking_number, carrier) 