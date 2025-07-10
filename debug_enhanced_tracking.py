#!/usr/bin/env python3
"""
Debug Enhanced Tracking System
Shows what content is actually being retrieved from carrier websites
"""

import asyncio
import logging
from src.backend.apple_silicon_estes_client import AppleSiliconEstesClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_estes_tracking():
    """Debug what content is actually being retrieved from Estes"""
    print("🔍 Debugging Enhanced Estes Tracking System")
    print("=" * 60)
    
    client = AppleSiliconEstesClient()
    tracking_number = "0628143046"
    
    print(f"📦 Testing PRO: {tracking_number}")
    print("-" * 40)
    
    # Test Playwright method and capture raw content
    try:
        print("🎭 Testing Playwright method...")
        
        # Temporarily modify the client to return raw content
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Show browser
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Navigate to Estes tracking page
            print("🌐 Navigating to Estes tracking page...")
            await page.goto('https://www.estes-express.com/myestes/shipment-tracking/')
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(10000)
            
            # Get initial content
            initial_content = await page.content()
            print(f"📄 Initial page content length: {len(initial_content)} characters")
            
            # Check if we can find the form
            try:
                form_container = await page.wait_for_selector('#shipmentTrackingFormContainer', timeout=15000)
                print("✅ Found form container")
                
                # Look for textarea
                textarea = await page.wait_for_selector('textarea', timeout=10000)
                if textarea:
                    print("✅ Found textarea")
                    
                    # Enter tracking number
                    await textarea.click()
                    await textarea.fill(tracking_number)
                    print(f"📝 Entered tracking number: {tracking_number}")
                    
                    # Look for submit button
                    submit_button = await page.query_selector('#shipmentTrackingSubmitButton')
                    if not submit_button:
                        submit_button = await page.query_selector('button[type="submit"]')
                    
                    if submit_button:
                        print("✅ Found submit button")
                        await submit_button.click()
                        print("🚀 Clicked submit button")
                        
                        # Wait for results with extended timeout
                        print("⏳ Waiting for results (60 seconds)...")
                        await page.wait_for_timeout(60000)  # Wait 60 seconds
                        
                        # Get final content
                        final_content = await page.content()
                        print(f"📄 Final page content length: {len(final_content)} characters")
                        
                        # Check if tracking number is in content
                        if tracking_number in final_content:
                            print("✅ Tracking number found in final content")
                        else:
                            print("❌ Tracking number NOT found in final content")
                        
                        # Look for specific tracking indicators
                        tracking_indicators = ['delivered', 'transit', 'pickup', 'status', 'shipment', 'tracking']
                        found_indicators = [ind for ind in tracking_indicators if ind in final_content.lower()]
                        print(f"📊 Found tracking indicators: {found_indicators}")
                        
                        # Save content for inspection
                        with open('debug_estes_final_content.html', 'w') as f:
                            f.write(final_content)
                        print("💾 Saved final content to debug_estes_final_content.html")
                        
                        # Show a sample of the content
                        print("📝 Sample of final content:")
                        print("-" * 40)
                        # Look for content around the tracking number
                        if tracking_number in final_content:
                            idx = final_content.find(tracking_number)
                            start = max(0, idx - 200)
                            end = min(len(final_content), idx + 200)
                            sample = final_content[start:end]
                            print(sample)
                        else:
                            # Just show first 500 chars
                            print(final_content[:500])
                        print("-" * 40)
                        
                    else:
                        print("❌ Submit button not found")
                else:
                    print("❌ Textarea not found")
            except Exception as e:
                print(f"❌ Error with form interaction: {e}")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Playwright debug failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_estes_tracking()) 