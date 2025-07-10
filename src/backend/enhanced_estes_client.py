#!/usr/bin/env python3
"""
Enhanced Estes Express Tracking Client

This module implements advanced tracking for Estes Express using multiple
browser automation techniques to overcome Apple Silicon CPU barriers and
JavaScript rendering issues.
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .enhanced_browser_automation import EnhancedBrowserAutomation

logger = logging.getLogger(__name__)

class EnhancedEstesClient:
    """Enhanced Estes Express tracking client with multiple fallback methods"""
    
    def __init__(self):
        self.browser_automation = EnhancedBrowserAutomation()
        self.logger = logging.getLogger(__name__)
        
        # Estes tracking URLs
        self.tracking_urls = [
            'https://www.estes-express.com/shipment-tracking/track-shipment',
            'https://www.estes-express.com/track',
            'https://www.estes-express.com/myestes/shipment-tracking'
        ]
        
        # Mobile-friendly URLs (often less protected)
        self.mobile_urls = [
            'https://m.estes-express.com/track',
            'https://mobile.estes-express.com/shipment-tracking'
        ]
        
        # API endpoints discovered through analysis
        self.api_endpoints = [
            'https://www.estes-express.com/api/shipment-tracking/track',
            'https://www.estes-express.com/services/tracking/shipment',
            'https://api.estes-express.com/v1/tracking'
        ]
    
    async def track_shipment(self, pro_number: str) -> Dict[str, Any]:
        """Track shipment using multiple enhanced methods"""
        
        self.logger.info(f"Starting enhanced Estes tracking for PRO: {pro_number}")
        
        # Method 1: Try browser automation with stealth
        try:
            result = await self._track_with_browser_automation(pro_number)
            if result and result.get('status') == 'success':
                self.logger.info(f"Browser automation successful for PRO: {pro_number}")
                return result
        except Exception as e:
            self.logger.warning(f"Browser automation failed: {e}")
        
        # Method 2: Try mobile-friendly URLs
        try:
            result = await self._track_with_mobile_urls(pro_number)
            if result and result.get('status') == 'success':
                self.logger.info(f"Mobile URL tracking successful for PRO: {pro_number}")
                return result
        except Exception as e:
            self.logger.warning(f"Mobile URL tracking failed: {e}")
        
        # Method 3: Try API endpoints
        try:
            result = await self._track_with_api_endpoints(pro_number)
            if result and result.get('status') == 'success':
                self.logger.info(f"API endpoint tracking successful for PRO: {pro_number}")
                return result
        except Exception as e:
            self.logger.warning(f"API endpoint tracking failed: {e}")
        
        # Method 4: Try legacy fallback
        try:
            result = await self._track_with_legacy_fallback(pro_number)
            if result and result.get('status') == 'success':
                self.logger.info(f"Legacy fallback successful for PRO: {pro_number}")
                return result
        except Exception as e:
            self.logger.warning(f"Legacy fallback failed: {e}")
        
        # All methods failed
        return {
            'status': 'error',
            'pro_number': pro_number,
            'carrier': 'Estes Express',
            'error_message': 'All enhanced tracking methods failed - CPU architecture and JavaScript barriers remain',
            'tracking_timestamp': datetime.now().isoformat(),
            'extracted_from': 'enhanced_estes_client_all_methods_failed'
        }
    
    async def _track_with_browser_automation(self, pro_number: str) -> Optional[Dict[str, Any]]:
        """Track using advanced browser automation"""
        
        session = None
        try:
            # Create stealth session optimized for Estes
            session = await self.browser_automation.create_stealth_session('estes')
            
            # Try each tracking URL
            for url in self.tracking_urls:
                try:
                    # Navigate to tracking page
                    content = await self.browser_automation.navigate_with_stealth(
                        session, url, wait_for='input[name*="track"], input[id*="track"]'
                    )
                    
                    # Submit tracking form if we're on the right page
                    if session['type'] == 'playwright':
                        result = await self._submit_estes_form_playwright(session, pro_number)
                        if result:
                            return result
                    elif session['type'] == 'selenium':
                        result = await self._submit_estes_form_selenium(session, pro_number)
                        if result:
                            return result
                    
                    # Try direct URL construction
                    direct_url = f"{url}?pro={pro_number}"
                    tracking_data = await self.browser_automation.extract_tracking_data(
                        session, direct_url, pro_number, 'estes'
                    )
                    if tracking_data:
                        return tracking_data
                        
                except Exception as e:
                    self.logger.debug(f"URL {url} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Browser automation tracking failed: {e}")
            return None
        finally:
            if session:
                await self.browser_automation.cleanup_session(session)
    
    async def _submit_estes_form_playwright(self, session: Dict[str, Any], pro_number: str) -> Optional[Dict[str, Any]]:
        """Submit Estes tracking form using Playwright"""
        
        page = session['page']
        
        try:
            # Look for tracking input field
            input_selectors = [
                'input[name*="track"]',
                'input[id*="track"]',
                'input[placeholder*="PRO"]',
                'input[placeholder*="tracking"]',
                '#trackingNumber',
                '#proNumber',
                '.tracking-input'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = await page.wait_for_selector(selector, timeout=5000)
                    if input_element:
                        break
                except:
                    continue
            
            if not input_element:
                return None
            
            # Clear and fill the input
            await input_element.clear()
            await input_element.fill(pro_number)
            
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Track")',
                'button:has-text("Search")',
                '.track-button',
                '.submit-button'
            ]
            
            submit_element = None
            for selector in submit_selectors:
                try:
                    submit_element = await page.wait_for_selector(selector, timeout=5000)
                    if submit_element:
                        break
                except:
                    continue
            
            if submit_element:
                # Click submit and wait for results
                await submit_element.click()
                await page.wait_for_timeout(3000)  # Wait for results to load
                
                # Extract tracking data from results page
                content = await page.content()
                return await self._parse_estes_results(content, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Playwright form submission failed: {e}")
            return None
    
    async def _submit_estes_form_selenium(self, session: Dict[str, Any], pro_number: str) -> Optional[Dict[str, Any]]:
        """Submit Estes tracking form using Selenium"""
        
        driver = session['driver']
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Look for tracking input field
            input_selectors = [
                (By.NAME, 'trackingNumber'),
                (By.ID, 'trackingNumber'),
                (By.ID, 'proNumber'),
                (By.CSS_SELECTOR, 'input[name*="track"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="PRO"]'),
                (By.CSS_SELECTOR, '.tracking-input')
            ]
            
            input_element = None
            for by, selector in input_selectors:
                try:
                    input_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if input_element:
                        break
                except:
                    continue
            
            if not input_element:
                return None
            
            # Clear and fill the input
            input_element.clear()
            input_element.send_keys(pro_number)
            
            # Look for submit button
            submit_selectors = [
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
                (By.CSS_SELECTOR, 'button:contains("Track")'),
                (By.CSS_SELECTOR, '.track-button'),
                (By.CSS_SELECTOR, '.submit-button')
            ]
            
            submit_element = None
            for by, selector in submit_selectors:
                try:
                    submit_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if submit_element:
                        break
                except:
                    continue
            
            if submit_element:
                # Click submit and wait for results
                submit_element.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.tracking-results, .shipment-details'))
                )
                
                # Extract tracking data from results page
                content = driver.page_source
                return await self._parse_estes_results(content, pro_number)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Selenium form submission failed: {e}")
            return None
    
    async def _track_with_mobile_urls(self, pro_number: str) -> Optional[Dict[str, Any]]:
        """Track using mobile-friendly URLs (often less protected)"""
        
        session = None
        try:
            # Create session optimized for mobile
            session = await self.browser_automation.create_stealth_session('estes')
            
            for url in self.mobile_urls:
                try:
                    # Try direct URL construction for mobile
                    mobile_tracking_url = f"{url}?pro={pro_number}"
                    
                    tracking_data = await self.browser_automation.extract_tracking_data(
                        session, mobile_tracking_url, pro_number, 'estes'
                    )
                    if tracking_data:
                        return tracking_data
                        
                except Exception as e:
                    self.logger.debug(f"Mobile URL {url} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Mobile URL tracking failed: {e}")
            return None
        finally:
            if session:
                await self.browser_automation.cleanup_session(session)
    
    async def _track_with_api_endpoints(self, pro_number: str) -> Optional[Dict[str, Any]]:
        """Track using discovered API endpoints"""
        
        session = None
        try:
            session = await self.browser_automation.create_stealth_session('estes')
            
            if session['type'] == 'cloudscraper':
                scraper = session['session']
                
                for endpoint in self.api_endpoints:
                    try:
                        # Try GET request
                        response = scraper.get(
                            f"{endpoint}?pro={pro_number}",
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                            result = await self._parse_api_response(data, pro_number)
                            if result:
                                return result
                        
                        # Try POST request
                        response = scraper.post(
                            endpoint,
                            json={'proNumber': pro_number, 'trackingNumber': pro_number},
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                            result = await self._parse_api_response(data, pro_number)
                            if result:
                                return result
                                
                    except Exception as e:
                        self.logger.debug(f"API endpoint {endpoint} failed: {e}")
                        continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"API endpoint tracking failed: {e}")
            return None
        finally:
            if session:
                await self.browser_automation.cleanup_session(session)
    
    async def _track_with_legacy_fallback(self, pro_number: str) -> Optional[Dict[str, Any]]:
        """Track using legacy fallback methods"""
        
        try:
            # Use the existing zero-cost carrier system as fallback
            from .zero_cost_carriers import ZeroCostCarrierTracking
            
            zero_cost = ZeroCostCarrierTracking()
            result = await zero_cost.track_estes_express(pro_number)
            
            if result and result.get('status') == 'success':
                # Enhance the result with our metadata
                result['extracted_from'] = 'enhanced_estes_client_legacy_fallback'
                result['enhancement_note'] = 'Fallback to zero-cost system successful'
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Legacy fallback failed: {e}")
            return None
    
    async def _parse_estes_results(self, content: str, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse Estes tracking results from HTML content"""
        
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for tracking information patterns
        tracking_patterns = [
            # Delivery patterns
            (r'Delivered\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+(.+)', 'delivered'),
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+Delivered\s+(.+)', 'delivered'),
            
            # In transit patterns
            (r'In Transit\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+(.+)', 'in_transit'),
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+In Transit\s+(.+)', 'in_transit'),
            
            # Picked up patterns
            (r'Picked Up\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+(.+)', 'picked_up'),
            (r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+Picked Up\s+(.+)', 'picked_up')
        ]
        
        for pattern, status_type in tracking_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                match = matches[0]
                if len(match) >= 3:
                    return {
                        'status': 'success',
                        'pro_number': pro_number,
                        'carrier': 'Estes Express',
                        'tracking_status': status_type.replace('_', ' ').title(),
                        'tracking_location': match[2].strip(),
                        'tracking_event': f"{status_type.replace('_', ' ').title()} on {match[0]} at {match[1]}",
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': 'enhanced_estes_client_html_parsing'
                    }
        
        # Look for any mention of the PRO number with status
        if pro_number in content:
            # Extract surrounding context
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pro_number in line:
                    # Get context around the PRO number
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 3)
                    context = ' '.join(lines[context_start:context_end])
                    
                    # Look for status keywords
                    status_keywords = ['delivered', 'in transit', 'picked up', 'out for delivery']
                    for keyword in status_keywords:
                        if keyword in context.lower():
                            return {
                                'status': 'success',
                                'pro_number': pro_number,
                                'carrier': 'Estes Express',
                                'tracking_status': keyword.title(),
                                'tracking_event': context[:200],
                                'tracking_timestamp': datetime.now().isoformat(),
                                'extracted_from': 'enhanced_estes_client_context_parsing'
                            }
        
        return None
    
    async def _parse_api_response(self, data: Any, pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse API response data"""
        
        try:
            if isinstance(data, str):
                # Try to parse as JSON
                try:
                    data = json.loads(data)
                except:
                    # Parse as text
                    if pro_number in data:
                        return {
                            'status': 'success',
                            'pro_number': pro_number,
                            'carrier': 'Estes Express',
                            'tracking_status': 'Found in API response',
                            'tracking_event': data[:200],
                            'tracking_timestamp': datetime.now().isoformat(),
                            'extracted_from': 'enhanced_estes_client_api_text_parsing'
                        }
            
            if isinstance(data, dict):
                # Recursively search for tracking information
                def search_dict(obj, target_pro):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if target_pro in str(value):
                                return obj
                            result = search_dict(value, target_pro)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = search_dict(item, target_pro)
                            if result:
                                return result
                    return None
                
                tracking_obj = search_dict(data, pro_number)
                if tracking_obj:
                    return {
                        'status': 'success',
                        'pro_number': pro_number,
                        'carrier': 'Estes Express',
                        'tracking_status': 'Found in API response',
                        'tracking_event': str(tracking_obj)[:200],
                        'tracking_timestamp': datetime.now().isoformat(),
                        'extracted_from': 'enhanced_estes_client_api_json_parsing'
                    }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"API response parsing failed: {e}")
            return None 