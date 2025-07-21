#!/usr/bin/env python3
"""
Fix Peninsula Truck Lines tracking extraction

This script addresses the issue where Peninsula tracking returns hardcoded fallback
locations instead of real website data.

ROOT CAUSE IDENTIFIED:
1. Peninsula website (peninsulatrucklines.com) is returning a "parking" page (domain parked)
2. Real tracking functionality is not available on this domain
3. The system falls back to hardcoded locations: ['SEATTLE, WA', 'PORTLAND, OR', 'TACOMA, WA', 'SPOKANE, WA', 'VANCOUVER, WA']
4. All tracking attempts fail because the website doesn't exist as a functional tracking portal

SOLUTION APPROACHES:
"""

import asyncio
import aiohttp
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional

class PeninsulaTrackingFixer:
    """Fix Peninsula tracking issues"""
    
    def __init__(self):
        self.alternative_domains = [
            "http://peninsulatrucklines.com",  # Try HTTP
            "https://peninsulafreight.com",   # Alternative domain
            "https://peninsula-trucking.com", # Alternative domain
            "https://peninsulatransport.com", # Alternative domain
            "https://ptlfreight.com"          # Potential short domain
        ]
        
        # Third-party tracking services that might have Peninsula data
        self.third_party_services = [
            "https://www.trackingmore.com/track/peninsula-truck-lines/{pro}",
            "https://packagetrackr.com/track/{pro}",
            "https://17track.net/en/track#{pro}",
            "https://www.shipmentsight.com/tracking/{pro}",
            "https://www.freightquote.com/track/{pro}"
        ]
    
    async def diagnose_peninsula_issue(self, pro_numbers: List[str]):
        """Comprehensive diagnosis of Peninsula tracking issues"""
        
        print("🔍 PENINSULA TRACKING ISSUE DIAGNOSIS")
        print("=" * 60)
        
        # 1. Test main domain accessibility
        await self._test_domain_accessibility()
        
        # 2. Search for alternative Peninsula domains
        await self._search_alternative_domains()
        
        # 3. Test third-party tracking services
        await self._test_third_party_services(pro_numbers[0] if pro_numbers else "536246546")
        
        # 4. Analyze the fallback system
        await self._analyze_fallback_system()
        
        # 5. Provide recommendations
        self._provide_recommendations()
    
    async def _test_domain_accessibility(self):
        """Test Peninsula domain accessibility"""
        
        print("\n1. DOMAIN ACCESSIBILITY TEST")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            domain = "https://www.peninsulatrucklines.com"
            
            try:
                async with session.get(domain, timeout=10) as response:
                    content = await response.text()
                    
                    print(f"✅ Domain accessible: {domain}")
                    print(f"   Status: {response.status}")
                    print(f"   Content-Length: {len(content)}")
                    print(f"   Headers: {dict(response.headers)}")
                    
                    # Check for parking indicators
                    parking_indicators = [
                        'parking_session',
                        'domain parking',
                        'parked domain',
                        'this domain is for sale',
                        'godaddy.com',
                        'sedo.com'
                    ]
                    
                    content_lower = content.lower()
                    headers_str = str(response.headers).lower()
                    
                    for indicator in parking_indicators:
                        if indicator in content_lower or indicator in headers_str:
                            print(f"   🚨 PARKING INDICATOR FOUND: {indicator}")
                    
                    # Check for actual tracking functionality
                    soup = BeautifulSoup(content, 'html.parser')
                    forms = soup.find_all('form')
                    inputs = soup.find_all('input')
                    
                    print(f"   Forms found: {len(forms)}")
                    print(f"   Input fields found: {len(inputs)}")
                    
                    if len(content) < 2000 and 'parking_session' in headers_str:
                        print("   ❌ CONFIRMED: Domain is PARKED (not functional)")
                        return False
                    
            except Exception as e:
                print(f"❌ Domain inaccessible: {e}")
                return False
        
        return True
    
    async def _search_alternative_domains(self):
        """Search for alternative Peninsula domains"""
        
        print("\n2. ALTERNATIVE DOMAIN SEARCH")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            for domain in self.alternative_domains:
                try:
                    async with session.get(domain, timeout=5) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Look for tracking-related content
                            if any(keyword in content.lower() for keyword in ['track', 'pro', 'shipment', 'freight']):
                                print(f"✅ Potential alternative: {domain}")
                                print(f"   Status: {response.status}")
                                print(f"   Contains tracking keywords")
                            else:
                                print(f"⚠️  Domain accessible but no tracking: {domain}")
                        else:
                            print(f"❌ {domain}: Status {response.status}")
                            
                except Exception as e:
                    print(f"❌ {domain}: {e}")
    
    async def _test_third_party_services(self, pro_number: str):
        """Test third-party tracking services"""
        
        print(f"\n3. THIRD-PARTY SERVICES TEST (PRO: {pro_number})")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            for service_template in self.third_party_services:
                service_url = service_template.replace("{pro}", pro_number)
                
                try:
                    async with session.get(service_url, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Look for Peninsula-specific tracking data
                            if pro_number in content and any(keyword in content.lower() for keyword in ['peninsula', 'delivered', 'transit']):
                                print(f"✅ POTENTIAL DATA FOUND: {service_url}")
                                print(f"   PRO {pro_number} found in response")
                                
                                # Extract potential tracking info
                                soup = BeautifulSoup(content, 'html.parser')
                                text = soup.get_text()
                                
                                # Look for status and location
                                status_pattern = r'(delivered|in transit|picked up|out for delivery)'
                                location_pattern = r'([A-Z]{2,}\s*,\s*[A-Z]{2})'
                                
                                status_match = re.search(status_pattern, text, re.IGNORECASE)
                                location_match = re.search(location_pattern, text)
                                
                                if status_match:
                                    print(f"   Status found: {status_match.group(1)}")
                                if location_match:
                                    print(f"   Location found: {location_match.group(1)}")
                            else:
                                print(f"❌ No Peninsula data: {service_url}")
                        else:
                            print(f"❌ {service_url}: Status {response.status}")
                            
                except Exception as e:
                    print(f"❌ {service_template}: {e}")
    
    async def _analyze_fallback_system(self):
        """Analyze the current fallback system"""
        
        print("\n4. FALLBACK SYSTEM ANALYSIS")
        print("-" * 30)
        
        # Hardcoded locations from the system
        peninsula_fallback_locations = [
            'SEATTLE, WA', 
            'PORTLAND, OR', 
            'TACOMA, WA', 
            'SPOKANE, WA', 
            'VANCOUVER, WA'
        ]
        
        print("Current Peninsula fallback locations:")
        for i, location in enumerate(peninsula_fallback_locations):
            print(f"   {i}: {location}")
        
        print("\nFallback logic:")
        print("   - Uses hash(pro_number) % 5 to select location")
        print("   - Always returns one of the 5 hardcoded WA/OR locations")
        print("   - No attempt to get real tracking data")
        
        # Test the current logic
        test_pros = ["536246546", "536246554", "537313956", "62263246"]
        
        print("\nCurrent fallback results for reported PRO numbers:")
        for pro in test_pros:
            pro_hash = hash(pro) % len(peninsula_fallback_locations)
            location = peninsula_fallback_locations[pro_hash]
            print(f"   PRO {pro}: {location} (hash index: {pro_hash})")
    
    def _provide_recommendations(self):
        """Provide recommendations for fixing Peninsula tracking"""
        
        print("\n5. RECOMMENDATIONS")
        print("-" * 30)
        
        print("IMMEDIATE FIXES:")
        print("1. ❌ DISABLE Peninsula fallback locations until real website is found")
        print("2. 🔍 RESEARCH correct Peninsula Truck Lines website/API")
        print("3. 📞 CONTACT Peninsula directly for tracking API information")
        print("4. ⚠️  WARN users that Peninsula tracking is not functional")
        
        print("\nLONG-TERM SOLUTIONS:")
        print("1. 🌐 Find the actual Peninsula tracking portal")
        print("2. 🔌 Integrate with Peninsula's real API if available")
        print("3. 🤝 Partner with third-party tracking services")
        print("4. 📊 Use EDI integration if Peninsula supports it")
        
        print("\nCODE CHANGES NEEDED:")
        print("1. Update advanced_extraction_strategies.py lines 551")
        print("2. Update carrier_specific_enhancer.py line 471")
        print("3. Add proper error handling for Peninsula")
        print("4. Implement alternative data sources")

    def create_peninsula_fix_patch(self):
        """Create a patch to fix Peninsula tracking"""
        
        patch_content = '''
# PENINSULA TRACKING FIX PATCH
# ============================

# Problem: Peninsula website is parked, returns fallback locations
# Solution: Disable fallback until real tracking source is found

# File 1: advanced_extraction_strategies.py line 551
# BEFORE:
# 'peninsula': ['SEATTLE, WA', 'PORTLAND, OR', 'TACOMA, WA', 'SPOKANE, WA', 'VANCOUVER, WA'],

# AFTER:
# 'peninsula': [],  # DISABLED: Real Peninsula website not accessible

# File 2: carrier_specific_enhancer.py line 471  
# BEFORE:
# locations = ['SEATTLE, WA', 'PORTLAND, OR', 'TACOMA, WA', 'SPOKANE, WA', 'VANCOUVER, WA']

# AFTER:
# locations = []  # DISABLED: Real Peninsula website not accessible
# # Return proper error instead of fake data

# File 3: Add proper Peninsula error handling
# Add to both files:
def _handle_peninsula_unavailable(self, pro_number: str) -> Dict[str, Any]:
    """Handle Peninsula unavailable website"""
    return {
        'status': 'Tracking Unavailable',
        'location': 'Unknown - Website Not Accessible',
        'event': f'Peninsula tracking temporarily unavailable for PRO {pro_number}',
        'timestamp': datetime.now().isoformat(),
        'error': 'Peninsula website is not currently functional',
        'recommendation': 'Contact Peninsula Truck Lines directly for tracking information'
    }
'''
        
        return patch_content

async def main():
    """Main function to diagnose and fix Peninsula tracking"""
    
    fixer = PeninsulaTrackingFixer()
    
    # Test PRO numbers from the issue report
    test_pros = [
        "536246546",  # Reported: "VANCOUVER, WA"
        "536246554",  # Reported: "VANCOUVER, WA"
        "537313956",  # Reported: "SPOKANE, WA"
        "62263246"    # Reported: "TACOMA, WA"
    ]
    
    # Run comprehensive diagnosis
    await fixer.diagnose_peninsula_issue(test_pros)
    
    print("\n" + "=" * 60)
    print("PENINSULA TRACKING FIX PATCH")
    print("=" * 60)
    
    patch = fixer.create_peninsula_fix_patch()
    print(patch)

if __name__ == "__main__":
    asyncio.run(main())