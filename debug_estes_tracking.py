#!/usr/bin/env python3
"""
Debug Estes Tracking Form Detection
Inspect the actual Estes website to understand form structure
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup

class EstesTrackingDebugger:
    """Debug Estes tracking form detection"""
    
    def __init__(self):
        self.test_pro = "0628143046"
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup session with realistic headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def debug_http_request(self):
        """Debug HTTP request to understand page structure"""
        print("🔍 DEBUGGING HTTP REQUEST")
        print("=" * 50)
        
        try:
            # Try main tracking page
            url = "https://www.estes-express.com/myestes/shipment-tracking/"
            print(f"📡 Requesting: {url}")
            
            response = self.session.get(url, timeout=10)
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Content Length: {len(response.text)}")
            
            if response.status_code == 200:
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for forms
                forms = soup.find_all('form')
                print(f"📋 Found {len(forms)} forms")
                
                for i, form in enumerate(forms):
                    print(f"\n📋 Form {i+1}:")
                    print(f"   Action: {form.get('action', 'No action')}")
                    print(f"   Method: {form.get('method', 'No method')}")
                    print(f"   ID: {form.get('id', 'No ID')}")
                    print(f"   Class: {form.get('class', 'No class')}")
                    
                    # Look for input fields
                    inputs = form.find_all('input')
                    print(f"   Inputs: {len(inputs)}")
                    for input_field in inputs:
                        print(f"     - Name: {input_field.get('name', 'No name')}")
                        print(f"       Type: {input_field.get('type', 'No type')}")
                        print(f"       ID: {input_field.get('id', 'No ID')}")
                        print(f"       Placeholder: {input_field.get('placeholder', 'No placeholder')}")
                
                # Look for tracking-related elements
                tracking_elements = soup.find_all(text=lambda text: 'track' in text.lower() if text else False)
                print(f"\n🔍 Found {len(tracking_elements)} elements containing 'track'")
                
                # Look for input fields that might be tracking inputs
                all_inputs = soup.find_all('input')
                print(f"\n📝 All input fields ({len(all_inputs)}):")
                for input_field in all_inputs:
                    name = input_field.get('name', '')
                    id_attr = input_field.get('id', '')
                    placeholder = input_field.get('placeholder', '')
                    type_attr = input_field.get('type', '')
                    
                    if any(keyword in f"{name} {id_attr} {placeholder}".lower() for keyword in ['track', 'pro', 'number', 'shipment']):
                        print(f"   🎯 POTENTIAL TRACKING INPUT:")
                        print(f"      Name: {name}")
                        print(f"      ID: {id_attr}")
                        print(f"      Type: {type_attr}")
                        print(f"      Placeholder: {placeholder}")
                        print(f"      Class: {input_field.get('class', 'No class')}")
                
                # Save page content for inspection
                with open('estes_page_debug.html', 'w') as f:
                    f.write(response.text)
                print(f"\n💾 Page content saved to 'estes_page_debug.html'")
                
            else:
                print(f"❌ HTTP request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ HTTP debug failed: {e}")
    
    def debug_selenium_detection(self):
        """Debug Selenium form detection"""
        print("\n🔍 DEBUGGING SELENIUM DETECTION")
        print("=" * 50)
        
        driver = None
        try:
            # Create ChromeDriver
            chrome_driver_path = ChromeDriverManager().install()
            print(f"🚗 ChromeDriver: {chrome_driver_path}")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            service = Service(chrome_driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to tracking page
            url = "https://www.estes-express.com/myestes/shipment-tracking/"
            print(f"🌐 Navigating to: {url}")
            driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            print(f"📄 Page title: {driver.title}")
            print(f"📄 Current URL: {driver.current_url}")
            
            # Try to find tracking inputs with various selectors
            selectors_to_try = [
                ('NAME', 'trackingNumber'),
                ('ID', 'trackingNumber'),
                ('NAME', 'tracking'),
                ('ID', 'tracking'),
                ('CSS_SELECTOR', 'input[name*="track"]'),
                ('CSS_SELECTOR', 'input[id*="track"]'),
                ('CSS_SELECTOR', 'input[placeholder*="track"]'),
                ('CSS_SELECTOR', 'input[placeholder*="PRO"]'),
                ('CSS_SELECTOR', 'input[placeholder*="number"]'),
                ('CSS_SELECTOR', 'input[type="text"]'),
                ('CSS_SELECTOR', 'input[type="search"]'),
                ('XPATH', '//input[contains(@placeholder, "track")]'),
                ('XPATH', '//input[contains(@placeholder, "PRO")]'),
                ('XPATH', '//input[contains(@placeholder, "number")]')
            ]
            
            found_inputs = []
            for method, selector in selectors_to_try:
                try:
                    if method == 'NAME':
                        elements = driver.find_elements(By.NAME, selector)
                    elif method == 'ID':
                        elements = driver.find_elements(By.ID, selector)
                    elif method == 'CSS_SELECTOR':
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    elif method == 'XPATH':
                        elements = driver.find_elements(By.XPATH, selector)
                    
                    if elements:
                        print(f"✅ Found {len(elements)} elements with {method}: {selector}")
                        for i, element in enumerate(elements):
                            try:
                                print(f"   Element {i+1}:")
                                print(f"     Tag: {element.tag_name}")
                                print(f"     Name: {element.get_attribute('name')}")
                                print(f"     ID: {element.get_attribute('id')}")
                                print(f"     Type: {element.get_attribute('type')}")
                                print(f"     Placeholder: {element.get_attribute('placeholder')}")
                                print(f"     Class: {element.get_attribute('class')}")
                                print(f"     Visible: {element.is_displayed()}")
                                print(f"     Enabled: {element.is_enabled()}")
                                
                                found_inputs.append({
                                    'method': method,
                                    'selector': selector,
                                    'element': element
                                })
                            except Exception as e:
                                print(f"     Error getting element info: {e}")
                    else:
                        print(f"❌ No elements found with {method}: {selector}")
                        
                except Exception as e:
                    print(f"❌ Error trying {method} {selector}: {e}")
            
            # Try to interact with found inputs
            if found_inputs:
                print(f"\n🎯 Testing interaction with {len(found_inputs)} found inputs")
                for i, input_info in enumerate(found_inputs):
                    try:
                        element = input_info['element']
                        if element.is_displayed() and element.is_enabled():
                            print(f"   Testing element {i+1}...")
                            element.clear()
                            element.send_keys(self.test_pro)
                            
                            # Look for submit button
                            submit_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                            if submit_buttons:
                                print(f"   Found {len(submit_buttons)} submit buttons")
                                submit_buttons[0].click()
                                time.sleep(3)
                                
                                # Check if page changed
                                new_url = driver.current_url
                                if new_url != url:
                                    print(f"   ✅ Page changed to: {new_url}")
                                    
                                    # Look for tracking results
                                    page_source = driver.page_source
                                    if any(keyword in page_source.lower() for keyword in ['delivered', 'in transit', 'picked up', 'tracking']):
                                        print(f"   ✅ Found tracking-related content")
                                    else:
                                        print(f"   ❌ No tracking content found")
                                else:
                                    print(f"   ❌ Page did not change")
                            else:
                                print(f"   ❌ No submit button found")
                            
                            break  # Only test the first viable input
                    except Exception as e:
                        print(f"   ❌ Error testing element {i+1}: {e}")
            
            # Save page source for inspection
            with open('estes_selenium_debug.html', 'w') as f:
                f.write(driver.page_source)
            print(f"\n💾 Selenium page source saved to 'estes_selenium_debug.html'")
            
        except Exception as e:
            print(f"❌ Selenium debug failed: {e}")
        finally:
            if driver:
                driver.quit()
    
    async def debug_playwright_detection(self):
        """Debug Playwright form detection"""
        print("\n🔍 DEBUGGING PLAYWRIGHT DETECTION")
        print("=" * 50)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                # Navigate to tracking page
                url = "https://www.estes-express.com/myestes/shipment-tracking/"
                print(f"🌐 Navigating to: {url}")
                await page.goto(url)
                await page.wait_for_load_state('networkidle')
                
                print(f"📄 Page title: {await page.title()}")
                print(f"📄 Current URL: {page.url}")
                
                # Try to find tracking inputs with various selectors
                selectors_to_try = [
                    'input[name*="track"]',
                    'input[id*="track"]',
                    'input[placeholder*="track"]',
                    'input[placeholder*="PRO"]',
                    'input[placeholder*="number"]',
                    'input[type="text"]',
                    'input[type="search"]',
                    'input[name="trackingNumber"]',
                    'input[id="trackingNumber"]'
                ]
                
                found_inputs = []
                for selector in selectors_to_try:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"✅ Found {len(elements)} elements with selector: {selector}")
                            for i, element in enumerate(elements):
                                try:
                                    name = await element.get_attribute('name')
                                    id_attr = await element.get_attribute('id')
                                    type_attr = await element.get_attribute('type')
                                    placeholder = await element.get_attribute('placeholder')
                                    class_attr = await element.get_attribute('class')
                                    visible = await element.is_visible()
                                    enabled = await element.is_enabled()
                                    
                                    print(f"   Element {i+1}:")
                                    print(f"     Name: {name}")
                                    print(f"     ID: {id_attr}")
                                    print(f"     Type: {type_attr}")
                                    print(f"     Placeholder: {placeholder}")
                                    print(f"     Class: {class_attr}")
                                    print(f"     Visible: {visible}")
                                    print(f"     Enabled: {enabled}")
                                    
                                    found_inputs.append({
                                        'selector': selector,
                                        'element': element
                                    })
                                except Exception as e:
                                    print(f"     Error getting element info: {e}")
                        else:
                            print(f"❌ No elements found with selector: {selector}")
                    except Exception as e:
                        print(f"❌ Error trying selector {selector}: {e}")
                
                # Try to interact with found inputs
                if found_inputs:
                    print(f"\n🎯 Testing interaction with {len(found_inputs)} found inputs")
                    for i, input_info in enumerate(found_inputs):
                        try:
                            element = input_info['element']
                            if await element.is_visible() and await element.is_enabled():
                                print(f"   Testing element {i+1}...")
                                await element.fill(self.test_pro)
                                
                                # Look for submit button
                                submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Track")')
                                if submit_button:
                                    print(f"   Found submit button")
                                    await submit_button.click()
                                    await page.wait_for_load_state('networkidle')
                                    
                                    # Check if page changed
                                    new_url = page.url
                                    if new_url != url:
                                        print(f"   ✅ Page changed to: {new_url}")
                                        
                                        # Look for tracking results
                                        content = await page.content()
                                        if any(keyword in content.lower() for keyword in ['delivered', 'in transit', 'picked up', 'tracking']):
                                            print(f"   ✅ Found tracking-related content")
                                        else:
                                            print(f"   ❌ No tracking content found")
                                    else:
                                        print(f"   ❌ Page did not change")
                                else:
                                    print(f"   ❌ No submit button found")
                                
                                break  # Only test the first viable input
                        except Exception as e:
                            print(f"   ❌ Error testing element {i+1}: {e}")
                
                # Save page content for inspection
                content = await page.content()
                with open('estes_playwright_debug.html', 'w') as f:
                    f.write(content)
                print(f"\n💾 Playwright page content saved to 'estes_playwright_debug.html'")
                
                await browser.close()
                
        except Exception as e:
            print(f"❌ Playwright debug failed: {e}")
    
    async def run_full_debug(self):
        """Run complete debugging session"""
        print("🔍 ESTES TRACKING FORM DEBUG SESSION")
        print("=" * 60)
        print(f"🎯 Test PRO Number: {self.test_pro}")
        print("=" * 60)
        
        # Debug HTTP request
        self.debug_http_request()
        
        # Debug Selenium detection
        self.debug_selenium_detection()
        
        # Debug Playwright detection
        await self.debug_playwright_detection()
        
        print("\n" + "=" * 60)
        print("🎯 DEBUG SESSION COMPLETE")
        print("=" * 60)
        print("📁 Files created:")
        print("   - estes_page_debug.html (HTTP request)")
        print("   - estes_selenium_debug.html (Selenium)")
        print("   - estes_playwright_debug.html (Playwright)")
        print("=" * 60)

async def main():
    """Main debug function"""
    debugger = EstesTrackingDebugger()
    await debugger.run_full_debug()

if __name__ == "__main__":
    asyncio.run(main()) 