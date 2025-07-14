#!/usr/bin/env python3
"""
Real Data Extractor

This module focuses on extracting actual tracking data from carrier websites
with no simulation or fallback to fake data.
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class RealDataExtractor:
    """Extract real tracking data from carrier websites"""
    
    def __init__(self):
        self.carrier_patterns = {
            'fedex': {
                'status_patterns': [
                    r'<span[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*tracking-status[^"]*"[^>]*>([^<]*)</div>',
                    r'status[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i',
                    r'<td[^>]*>Status</td>\s*<td[^>]*>([^<]*)</td>'
                ],
                'location_patterns': [
                    r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*destination[^"]*"[^>]*>([^<]*)</div>',
                    r'location[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i',
                    r'<td[^>]*>Location</td>\s*<td[^>]*>([^<]*)</td>'
                ],
                'date_patterns': [
                    r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</span>',
                    r'deliveryDate[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i',
                    r'<td[^>]*>Date</td>\s*<td[^>]*>([^<]*)</td>'
                ]
            },
            'estes': {
                'status_patterns': [
                    r'<span[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*delivery-status[^"]*"[^>]*>([^<]*)</div>',
                    r'<td[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</td>',
                    r'status[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i'
                ],
                'location_patterns': [
                    r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*consignee[^"]*"[^>]*>([^<]*)</div>',
                    r'<td[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</td>',
                    r'consigneeAddress[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i'
                ],
                'date_patterns': [
                    r'<span[^>]*class="[^"]*delivery-date[^"]*"[^>]*>([^<]*)</span>',
                    r'<td[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</td>',
                    r'deliveryDate[\'"]?\s*:\s*[\'"]([^\'"]*)[\'"]/i'
                ]
            },
            'peninsula': {
                'status_patterns': [
                    r'<span[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*tracking-status[^"]*"[^>]*>([^<]*)</div>',
                    r'<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>'
                ],
                'location_patterns': [
                    r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*destination[^"]*"[^>]*>([^<]*)</div>'
                ],
                'date_patterns': [
                    r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</span>',
                    r'<td[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</td>'
                ]
            },
            'rl': {
                'status_patterns': [
                    r'<span[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*tracking-status[^"]*"[^>]*>([^<]*)</div>',
                    r'<td[^>]*class="[^"]*status[^"]*"[^>]*>([^<]*)</td>'
                ],
                'location_patterns': [
                    r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</span>',
                    r'<div[^>]*class="[^"]*destination[^"]*"[^>]*>([^<]*)</div>',
                    r'<td[^>]*class="[^"]*location[^"]*"[^>]*>([^<]*)</td>'
                ],
                'date_patterns': [
                    r'<span[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</span>',
                    r'<td[^>]*class="[^"]*date[^"]*"[^>]*>([^<]*)</td>'
                ]
            }
        }
    
    async def extract_real_tracking_data(self, session: aiohttp.ClientSession, url: str, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Extract real tracking data from carrier website"""
        
        try:
            # Get the page content
            content = await self._get_page_content(session, url, pro_number, carrier)
            if not content:
                return None
            
            # Extract tracking information using multiple methods
            tracking_info = await self._extract_tracking_info_comprehensive(content, pro_number, carrier)
            
            if tracking_info:
                logger.info(f"✅ Successfully extracted real tracking data for {pro_number} from {carrier}")
                return tracking_info
            else:
                logger.warning(f"❌ Could not extract tracking data for {pro_number} from {carrier}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Real data extraction failed for {pro_number}: {e}")
            return None
    
    async def _get_page_content(self, session: aiohttp.ClientSession, url: str, pro_number: str, carrier: str) -> Optional[str]:
        """Get page content with proper tracking request"""
        
        try:
            # Build tracking URL with PRO number
            tracking_url = self._build_tracking_url(url, pro_number, carrier)
            
            # Use realistic headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try GET request first
            timeout = aiohttp.ClientTimeout(total=15)
            async with session.get(tracking_url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    if len(content) > 1000:  # Ensure we got substantial content
                        return content
            
            # Try POST request if GET failed
            form_data = {
                'pro': pro_number,
                'trackingNumber': pro_number,
                'proNumber': pro_number,
                'billOfLading': pro_number,
                'search': pro_number,
                'number': pro_number
            }
            
            async with session.post(url, data=form_data, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    if len(content) > 1000:
                        return content
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get page content: {e}")
            return None
    
    def _build_tracking_url(self, base_url: str, pro_number: str, carrier: str) -> str:
        """Build tracking URL with PRO number"""
        
        # Carrier-specific URL patterns
        url_patterns = {
            'fedex': f"{base_url}?trackingNumber={pro_number}",
            'estes': f"{base_url}?pro={pro_number}",
            'peninsula': f"{base_url}?trackingNumber={pro_number}",
            'rl': f"{base_url}?pro={pro_number}"
        }
        
        return url_patterns.get(carrier, f"{base_url}?trackingNumber={pro_number}")
    
    async def _extract_tracking_info_comprehensive(self, content: str, pro_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Comprehensive tracking information extraction"""
        
        # Method 1: Try JSON data extraction
        json_data = self._extract_json_data(content)
        if json_data:
            tracking_info = self._parse_json_tracking_data(json_data, pro_number)
            if tracking_info:
                return tracking_info
        
        # Method 2: Try HTML pattern matching
        html_data = self._extract_html_patterns(content, carrier)
        if html_data:
            return html_data
        
        # Method 3: Try table extraction
        table_data = self._extract_table_data(content)
        if table_data:
            return table_data
        
        # Method 4: Try microdata/schema.org
        microdata = self._extract_microdata(content)
        if microdata:
            return microdata
        
        return None
    
    def _extract_json_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON data from page content"""
        
        # Look for JSON in script tags
        json_patterns = [
            r'<script[^>]*type="application/json"[^>]*>([^<]*)</script>',
            r'<script[^>]*>.*?var\s+tracking\s*=\s*({[^}]*}[^<]*)</script>',
            r'<script[^>]*>.*?window\.__INITIAL_STATE__\s*=\s*({[^}]*}[^<]*)</script>',
            r'<script[^>]*>.*?trackingData\s*=\s*({[^}]*}[^<]*)</script>'
        ]
        
        for pattern in json_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    json_str = match.group(1)
                    data = json.loads(json_str)
                    if isinstance(data, dict) and self._has_tracking_data(data):
                        return data
                except:
                    continue
        
        return None
    
    def _has_tracking_data(self, data: Dict[str, Any]) -> bool:
        """Check if JSON data contains tracking information"""
        
        tracking_indicators = ['status', 'location', 'delivery', 'tracking', 'shipment', 'destination']
        
        data_str = json.dumps(data).lower()
        
        # Check if at least 2 tracking indicators are present
        indicator_count = sum(1 for indicator in tracking_indicators if indicator in data_str)
        return indicator_count >= 2
    
    def _parse_json_tracking_data(self, data: Dict[str, Any], pro_number: str) -> Optional[Dict[str, Any]]:
        """Parse JSON data for tracking information"""
        
        def extract_nested_value(obj, keys):
            for key in keys:
                if isinstance(obj, dict) and key in obj:
                    obj = obj[key]
                else:
                    return None
            return obj
        
        # Common JSON structure patterns
        status_paths = [
            ['status'],
            ['deliveryStatus'],
            ['trackingStatus'],
            ['shipment', 'status'],
            ['tracking', 'status'],
            ['result', 'status']
        ]
        
        location_paths = [
            ['location'],
            ['destination'],
            ['deliveryLocation'],
            ['consigneeAddress'],
            ['shipment', 'destination'],
            ['tracking', 'location'],
            ['result', 'location']
        ]
        
        date_paths = [
            ['deliveryDate'],
            ['date'],
            ['timestamp'],
            ['lastUpdate'],
            ['shipment', 'deliveryDate'],
            ['tracking', 'date'],
            ['result', 'date']
        ]
        
        # Extract values
        status = None
        location = None
        date = None
        
        for path in status_paths:
            status = extract_nested_value(data, path)
            if status:
                break
        
        for path in location_paths:
            location = extract_nested_value(data, path)
            if location:
                break
        
        for path in date_paths:
            date = extract_nested_value(data, path)
            if date:
                break
        
        # Return if we found meaningful data
        if status and (location or date):
            return {
                'status': str(status),
                'location': str(location) if location else 'Unknown',
                'event': f'Package {status.lower()}',
                'timestamp': str(date) if date else datetime.now().isoformat()
            }
        
        return None
    
    def _extract_html_patterns(self, content: str, carrier: str) -> Optional[Dict[str, Any]]:
        """Extract tracking info using HTML patterns"""
        
        patterns = self.carrier_patterns.get(carrier, {})
        
        extracted = {}
        
        # Extract status
        for pattern in patterns.get('status_patterns', []):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if match.group(1).strip():
                    extracted['status'] = match.group(1).strip()
                    break
            if 'status' in extracted:
                break
        
        # Extract location
        for pattern in patterns.get('location_patterns', []):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if match.group(1).strip():
                    extracted['location'] = match.group(1).strip()
                    break
            if 'location' in extracted:
                break
        
        # Extract date
        for pattern in patterns.get('date_patterns', []):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if match.group(1).strip():
                    extracted['date'] = match.group(1).strip()
                    break
            if 'date' in extracted:
                break
        
        # Return if we found meaningful data
        if extracted.get('status') and (extracted.get('location') or extracted.get('date')):
            return {
                'status': extracted['status'],
                'location': extracted.get('location', 'Unknown'),
                'event': f"Package {extracted['status'].lower()}",
                'timestamp': extracted.get('date', datetime.now().isoformat())
            }
        
        return None
    
    def _extract_table_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract tracking data from HTML tables"""
        
        soup = BeautifulSoup(content, 'html.parser')
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            # Look for tracking table patterns
            headers = []
            header_row = rows[0]
            for cell in header_row.find_all(['th', 'td']):
                headers.append(cell.get_text().strip().lower())
            
            # Check if this looks like a tracking table
            tracking_indicators = ['status', 'location', 'date', 'time', 'destination', 'delivery']
            if not any(indicator in ' '.join(headers) for indicator in tracking_indicators):
                continue
            
            # Extract data from the most recent row (usually the last one)
            data_rows = rows[1:]
            if data_rows:
                # Try the last row first (most recent)
                for row in reversed(data_rows):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= len(headers):
                        row_data = {}
                        for i, cell in enumerate(cells[:len(headers)]):
                            if i < len(headers):
                                row_data[headers[i]] = cell.get_text().strip()
                        
                        # Extract tracking info from row
                        status = self._find_status_in_row(row_data)
                        location = self._find_location_in_row(row_data)
                        date = self._find_date_in_row(row_data)
                        
                        if status and (location or date):
                            return {
                                'status': status,
                                'location': location or 'Unknown',
                                'event': f'Package {status.lower()}',
                                'timestamp': date or datetime.now().isoformat()
                            }
        
        return None
    
    def _find_status_in_row(self, row_data: Dict[str, str]) -> Optional[str]:
        """Find status information in table row"""
        
        status_keywords = ['status', 'delivery', 'tracking']
        
        for key, value in row_data.items():
            if any(keyword in key.lower() for keyword in status_keywords):
                if value and len(value.strip()) > 2:
                    return value.strip()
        
        return None
    
    def _find_location_in_row(self, row_data: Dict[str, str]) -> Optional[str]:
        """Find location information in table row"""
        
        location_keywords = ['location', 'destination', 'city', 'address', 'consignee']
        
        for key, value in row_data.items():
            if any(keyword in key.lower() for keyword in location_keywords):
                if value and len(value.strip()) > 2:
                    return value.strip()
        
        return None
    
    def _find_date_in_row(self, row_data: Dict[str, str]) -> Optional[str]:
        """Find date information in table row"""
        
        date_keywords = ['date', 'time', 'timestamp', 'delivery', 'updated']
        
        for key, value in row_data.items():
            if any(keyword in key.lower() for keyword in date_keywords):
                if value and len(value.strip()) > 2:
                    return value.strip()
        
        return None
    
    def _extract_microdata(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract tracking data from microdata/schema.org"""
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for schema.org microdata
        microdata_elements = soup.find_all(attrs={'itemscope': True})
        
        for element in microdata_elements:
            itemtype = element.get('itemtype', '')
            if 'parcel' in itemtype.lower() or 'delivery' in itemtype.lower():
                
                status_elem = element.find(attrs={'itemprop': 'deliveryStatus'})
                location_elem = element.find(attrs={'itemprop': 'deliveryAddress'})
                date_elem = element.find(attrs={'itemprop': 'expectedDeliveryDate'})
                
                if status_elem and status_elem.get_text().strip():
                    return {
                        'status': status_elem.get_text().strip(),
                        'location': location_elem.get_text().strip() if location_elem else 'Unknown',
                        'event': f'Package {status_elem.get_text().strip().lower()}',
                        'timestamp': date_elem.get_text().strip() if date_elem else datetime.now().isoformat()
                    }
        
        return None