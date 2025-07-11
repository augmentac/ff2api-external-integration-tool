#!/usr/bin/env python3
"""
Status Event Extractor

This module provides proper event extraction logic with:
- Chronological event sorting
- Event hierarchy determination
- Latest status identification
- Structured data extraction
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class StatusEventExtractor:
    """
    Advanced event extractor that properly identifies the latest tracking event
    with chronological sorting and status hierarchy
    """
    
    def __init__(self):
        # Event hierarchy - higher numbers = higher priority
        self.event_hierarchy = {
            'delivered': 100,
            'delivery_complete': 100,
            'out_for_delivery': 90,
            'delivery_attempted': 85,
            'at_delivery_location': 80,
            'in_transit': 70,
            'departed_facility': 65,
            'at_terminal': 60,
            'arrived_facility': 55,
            'picked_up': 50,
            'at_origin': 45,
            'scheduled': 40,
            'pending': 30,
            'label_created': 20,
            'unknown': 10
        }
        
        # Status keywords for identification
        self.status_keywords = {
            'delivered': ['delivered', 'delivery complete', 'delivered to'],
            'out_for_delivery': ['out for delivery', 'on vehicle', 'with driver'],
            'delivery_attempted': ['delivery attempted', 'attempted delivery', 'delivery exception'],
            'at_delivery_location': ['at delivery location', 'arrival at destination'],
            'in_transit': ['in transit', 'on the way', 'en route'],
            'departed_facility': ['departed', 'left facility', 'departed terminal'],
            'at_terminal': ['at terminal', 'arrived at terminal', 'at facility'],
            'arrived_facility': ['arrived at facility', 'received at'],
            'picked_up': ['picked up', 'origin scan', 'pickup'],
            'at_origin': ['at origin', 'origin facility'],
            'scheduled': ['scheduled', 'appointment', 'scheduled delivery'],
            'pending': ['pending', 'shipment created', 'ready for pickup'],
            'label_created': ['label created', 'shipment information']
        }
        
        # Carrier-specific event selectors
        self.carrier_selectors = {
            'fedex': {
                'event_container': '[data-testid="TrackingEvent"], .tracking-event, .scan-event',
                'timestamp_selectors': ['.event-date', '.scan-date', '[data-testid="EventDate"]'],
                'status_selectors': ['.event-status', '.scan-status', '[data-testid="EventStatus"]'],
                'location_selectors': ['.event-location', '.scan-location', '[data-testid="EventLocation"]'],
                'timestamp_patterns': [
                    r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)',
                    r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)',
                    r'(\w+,\s+\w+\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)'
                ]
            },
            'estes': {
                'event_container': '.tracking-history-item, .status-event, .shipment-event',
                'timestamp_selectors': ['.event-date', '.status-date', '.delivery-date'],
                'status_selectors': ['.event-status', '.status-description', '.shipment-status'],
                'location_selectors': ['.event-location', '.terminal-location', '.delivery-location'],
                'timestamp_patterns': [
                    r'(\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)',
                    r'(\d{2}/\d{2}/\d{4})',
                    r'(\w+\s+\d{1,2},\s+\d{4})'
                ]
            },
            'peninsula': {
                'event_container': '.tracking-event, .activity-item, .status-row',
                'timestamp_selectors': ['.event-date', '.activity-date', '.status-date'],
                'status_selectors': ['.event-description', '.activity-status', '.status-text'],
                'location_selectors': ['.event-location', '.activity-location', '.terminal-name'],
                'timestamp_patterns': [
                    r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}[ap]m)',
                    r'(\d{2}/\d{2}/\d{4})',
                    r'(\d{1,2}/\d{1,2}/\d{4})'
                ]
            },
            'rl': {
                'event_container': '.shipment-event, .tracking-event, .activity-row',
                'timestamp_selectors': ['.event-date', '.activity-date', '.scan-date'],
                'status_selectors': ['.event-status', '.activity-description', '.scan-description'],
                'location_selectors': ['.event-location', '.activity-location', '.scan-location'],
                'timestamp_patterns': [
                    r'(\d{2}/\d{2}/\d{4}\s+\|\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M)',
                    r'(\d{2}/\d{2}/\d{4})',
                    r'(\w+\s+\d{2}/\d{2}/\d{4})'
                ]
            }
        }
    
    def extract_latest_event(self, html_content: str, carrier: str) -> Dict[str, Any]:
        """
        Extract the most recent tracking event with proper parsing
        
        Args:
            html_content: Raw HTML content from carrier website
            carrier: Carrier name (fedex, estes, peninsula, rl)
            
        Returns:
            Dict containing the latest event information
        """
        try:
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all events from HTML
            events = self.parse_all_events(soup, carrier.lower())
            
            if not events:
                return self.create_no_events_result(carrier)
            
            # Sort events chronologically
            sorted_events = self.sort_events_by_timestamp(events)
            
            # Apply status hierarchy to get the most important event
            latest_event = self.get_highest_priority_event(sorted_events)
            
            return self.format_latest_event_result(latest_event, carrier)
            
        except Exception as e:
            logger.error(f"Error extracting latest event: {e}")
            return self.create_error_result(str(e), carrier)
    
    def parse_all_events(self, soup: BeautifulSoup, carrier: str) -> List[Dict[str, Any]]:
        """
        Parse all tracking events from HTML content
        
        Args:
            soup: BeautifulSoup parsed HTML
            carrier: Carrier name
            
        Returns:
            List of all tracking events found
        """
        events = []
        
        try:
            # Get carrier-specific selectors
            selectors = self.carrier_selectors.get(carrier, self.carrier_selectors['fedex'])
            
            # Method 1: Extract from structured event containers
            event_containers = soup.select(selectors['event_container'])
            for container in event_containers:
                event = self.extract_event_from_container(container, selectors)
                if event:
                    events.append(event)
            
            # Method 2: Extract from tables
            table_events = self.extract_events_from_tables(soup, carrier)
            events.extend(table_events)
            
            # Method 3: Extract from text patterns
            text_events = self.extract_events_from_text_patterns(soup, carrier)
            events.extend(text_events)
            
            # Method 4: Extract from JavaScript/JSON data
            js_events = self.extract_events_from_javascript(soup, carrier)
            events.extend(js_events)
            
        except Exception as e:
            logger.error(f"Error parsing events: {e}")
        
        return events
    
    def extract_event_from_container(self, container, selectors: Dict) -> Optional[Dict[str, Any]]:
        """Extract event data from a structured container"""
        try:
            event = {}
            
            # Extract timestamp
            timestamp = None
            for ts_selector in selectors['timestamp_selectors']:
                ts_element = container.select_one(ts_selector)
                if ts_element:
                    timestamp = self.clean_text(ts_element.get_text())
                    break
            
            # Extract status
            status = None
            for status_selector in selectors['status_selectors']:
                status_element = container.select_one(status_selector)
                if status_element:
                    status = self.clean_text(status_element.get_text())
                    break
            
            # Extract location
            location = None
            for loc_selector in selectors['location_selectors']:
                loc_element = container.select_one(loc_selector)
                if loc_element:
                    location = self.clean_text(loc_element.get_text())
                    break
            
            # If we have meaningful data, create event
            if timestamp and status:
                parsed_ts = self.parse_timestamp(timestamp)
                priority = self.get_status_priority(status)
                
                event = {
                    'timestamp': timestamp,
                    'status': status,
                    'location': location or 'Unknown',
                    'description': status,
                    'source': 'container',
                    'raw_html': str(container)[:500],  # First 500 chars for debugging
                    'parsed_timestamp': parsed_ts,
                    'priority': priority
                }
                
                return event
            
        except Exception as e:
            logger.debug(f"Error extracting event from container: {e}")
        
        return None
    
    def extract_events_from_tables(self, soup: BeautifulSoup, carrier: str) -> List[Dict[str, Any]]:
        """Extract events from table structures"""
        events = []
        
        try:
            tables = soup.find_all('table')
            for table in tables:
                try:
                    rows = table.find_all('tr')
                    for row in rows:
                        try:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                event = self.extract_event_from_table_row(cells, carrier)
                                if event:
                                    events.append(event)
                        except AttributeError:
                            continue
                except AttributeError:
                    continue
        
        except Exception as e:
            logger.debug(f"Error extracting events from tables: {e}")
        
        return events
    
    def extract_event_from_table_row(self, cells: List, carrier: str) -> Optional[Dict[str, Any]]:
        """Extract event from table row cells"""
        try:
            # Look for date patterns in cells
            timestamp = None
            status = None
            location = None
            
            for cell in cells:
                cell_text = self.clean_text(cell.get_text())
                
                # Check if this cell contains a timestamp
                if not timestamp and self.is_timestamp(cell_text):
                    timestamp = cell_text
                
                # Check if this cell contains a status
                if not status and self.is_status(cell_text):
                    status = cell_text
                
                # Check if this cell contains a location
                if not location and self.is_location(cell_text):
                    location = cell_text
            
            # Create event if we have minimum required data
            if timestamp and status:
                return {
                    'timestamp': timestamp,
                    'status': status,
                    'location': location or 'Unknown',
                    'description': status,
                    'source': 'table',
                    'parsed_timestamp': self.parse_timestamp(timestamp),
                    'priority': self.get_status_priority(status)
                }
        
        except Exception as e:
            logger.debug(f"Error extracting event from table row: {e}")
        
        return None
    
    def extract_events_from_text_patterns(self, soup: BeautifulSoup, carrier: str) -> List[Dict[str, Any]]:
        """Extract events from text patterns using regex"""
        events = []
        
        try:
            text_content = soup.get_text()
            
            # Carrier-specific patterns
            if carrier == 'estes':
                # Estes pattern: "Delivered 07/02/2025 2:30 PM"
                pattern = r'(Delivered|In Transit|Picked Up|At Terminal)\s+(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)'
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    events.append({
                        'status': match[0],
                        'timestamp': f"{match[1]} {match[2]}",
                        'location': 'Unknown',
                        'description': match[0],
                        'source': 'text_pattern',
                        'parsed_timestamp': self.parse_timestamp(f"{match[1]} {match[2]}"),
                        'priority': self.get_status_priority(match[0])
                    })
            
            elif carrier == 'peninsula':
                # Peninsula pattern: "07/02/2025 2:30pm Delivered CITY, ST"
                pattern = r'(\d{2}/\d{2}/\d{4})\s+(\d{1,2}:\d{2}[ap]m)\s+(Delivered|PICKUP|LINE MFST|ASG ROUTE|DEL MFST)(?:\s+([A-Z\s]+))?'
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    events.append({
                        'status': match[2],
                        'timestamp': f"{match[0]} {match[1]}",
                        'location': match[3] if len(match) > 3 and match[3] else 'Unknown',
                        'description': match[2],
                        'source': 'text_pattern',
                        'parsed_timestamp': self.parse_timestamp(f"{match[0]} {match[1]}"),
                        'priority': self.get_status_priority(match[2])
                    })
            
            elif carrier == 'rl':
                # R&L pattern: "Delivered 07/02/2025 | 10:31:00 AM"
                pattern = r'(Delivered|In Transit|Picked Up)\s+(\d{2}/\d{2}/\d{4})\s*\|\s*(\d{1,2}:\d{2}:\d{2}\s*[AP]M)'
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    events.append({
                        'status': match[0],
                        'timestamp': f"{match[1]} | {match[2]}",
                        'location': 'Unknown',
                        'description': match[0],
                        'source': 'text_pattern',
                        'parsed_timestamp': self.parse_timestamp(f"{match[1]} {match[2]}"),
                        'priority': self.get_status_priority(match[0])
                    })
        
        except Exception as e:
            logger.debug(f"Error extracting events from text patterns: {e}")
        
        return events
    
    def extract_events_from_javascript(self, soup: BeautifulSoup, carrier: str) -> List[Dict[str, Any]]:
        """Extract events from JavaScript/JSON data embedded in HTML"""
        events = []
        
        try:
            script_tags = soup.find_all('script')
            for script in script_tags:
                script_content = script.get_text()
                
                # Look for JSON data with tracking events
                json_patterns = [
                    r'trackingEvents\s*:\s*(\[.*?\])',
                    r'events\s*:\s*(\[.*?\])',
                    r'scanEvents\s*:\s*(\[.*?\])',
                    r'"events":\s*(\[.*?\])'
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            events_data = json.loads(match)
                            if isinstance(events_data, list):
                                for event_data in events_data:
                                    if isinstance(event_data, dict):
                                        event = self.parse_json_event(event_data, carrier)
                                        if event:
                                            events.append(event)
                        except json.JSONDecodeError:
                            continue
        
        except Exception as e:
            logger.debug(f"Error extracting events from JavaScript: {e}")
        
        return events
    
    def parse_json_event(self, event_data: Dict, carrier: str) -> Optional[Dict[str, Any]]:
        """Parse event from JSON data"""
        try:
            # Common JSON fields
            timestamp = event_data.get('date') or event_data.get('timestamp') or event_data.get('eventDate')
            status = event_data.get('status') or event_data.get('eventType') or event_data.get('description')
            location = event_data.get('location') or event_data.get('eventLocation') or event_data.get('city')
            
            if timestamp and status:
                return {
                    'timestamp': str(timestamp),
                    'status': str(status),
                    'location': str(location) if location else 'Unknown',
                    'description': str(status),
                    'source': 'json',
                    'parsed_timestamp': self.parse_timestamp(str(timestamp)),
                    'priority': self.get_status_priority(str(status))
                }
        
        except Exception as e:
            logger.debug(f"Error parsing JSON event: {e}")
        
        return None
    
    def sort_events_by_timestamp(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events chronologically by timestamp"""
        try:
            # Filter events with valid timestamps
            valid_events = [e for e in events if e.get('parsed_timestamp')]
            
            # Sort by parsed timestamp (most recent first)
            sorted_events = sorted(valid_events, key=lambda x: x['parsed_timestamp'], reverse=True)
            
            return sorted_events
        
        except Exception as e:
            logger.error(f"Error sorting events: {e}")
            return events
    
    def get_highest_priority_event(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get the highest priority event from chronologically sorted events"""
        if not events:
            return {}
        
        # If we have a delivered event, prioritize it
        for event in events:
            if event.get('priority', 0) >= 100:  # Delivered status
                return event
        
        # Otherwise, get the most recent event with highest priority
        highest_priority_event = max(events, key=lambda x: (x.get('priority', 0), x.get('parsed_timestamp', datetime.min)))
        
        return highest_priority_event
    
    def get_status_priority(self, status: str) -> int:
        """Get priority score for a status"""
        if not status:
            return 0
        
        status_lower = status.lower()
        
        # Check each status category
        for status_type, keywords in self.status_keywords.items():
            if any(keyword in status_lower for keyword in keywords):
                return self.event_hierarchy.get(status_type, 10)
        
        return 10  # Default priority for unknown status
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        if not timestamp_str:
            return datetime.min
        
        # Common timestamp formats
        formats = [
            '%m/%d/%Y %I:%M:%S %p',
            '%m/%d/%Y %I:%M %p',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%B %d, %Y %I:%M %p',
            '%b %d, %Y %I:%M %p',
            '%A, %B %d, %Y %I:%M %p'
        ]
        
        # Clean timestamp string
        clean_timestamp = re.sub(r'\s+', ' ', timestamp_str.strip())
        clean_timestamp = re.sub(r'\|', '', clean_timestamp)
        
        for fmt in formats:
            try:
                return datetime.strptime(clean_timestamp, fmt)
            except ValueError:
                continue
        
        # If no format matches, try to extract just the date
        date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', clean_timestamp)
        if date_match:
            try:
                return datetime.strptime(date_match.group(1), '%m/%d/%Y')
            except ValueError:
                pass
        
        return datetime.min
    
    def is_timestamp(self, text: str) -> bool:
        """Check if text contains a timestamp"""
        if not text or len(text) < 8:
            return False
        
        # Look for common timestamp patterns
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\w+\s+\d{1,2},\s+\d{4}',
            r'\d{1,2}:\d{2}:\d{2}',
            r'\d{1,2}:\d{2}\s+[AP]M'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    def is_status(self, text: str) -> bool:
        """Check if text contains a status"""
        if not text or len(text) < 3:
            return False
        
        text_lower = text.lower()
        
        # Check for status keywords
        all_keywords = []
        for keywords in self.status_keywords.values():
            all_keywords.extend(keywords)
        
        return any(keyword in text_lower for keyword in all_keywords)
    
    def is_location(self, text: str) -> bool:
        """Check if text contains a location"""
        if not text or len(text) < 3:
            return False
        
        # Look for location patterns
        location_patterns = [
            r'[A-Z][a-z]+,\s*[A-Z]{2}',  # City, ST
            r'[A-Z][A-Z\s]+,\s*[A-Z]{2}',  # CITY NAME, ST
            r'[A-Z]{2}\s+\d{5}',  # ST 12345
            r'terminal',
            r'facility',
            r'depot'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in location_patterns)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        cleaned = re.sub(r'[^\w\s/:-]', '', cleaned)
        
        return cleaned
    
    def format_latest_event_result(self, event: Dict[str, Any], carrier: str) -> Dict[str, Any]:
        """Format the latest event result"""
        if not event:
            return self.create_no_events_result(carrier)
        
        return {
            'success': True,
            'status': event.get('status', 'Unknown'),
            'location': event.get('location', 'Unknown'),
            'timestamp': event.get('timestamp', 'Unknown'),
            'event_description': event.get('description', event.get('status', 'Unknown')),
            'is_delivered': event.get('priority', 0) >= 100,
            'confidence_score': self.calculate_confidence_score(event),
            'carrier': carrier,
            'extraction_method': event.get('source', 'unknown'),
            'parsed_timestamp': event.get('parsed_timestamp', datetime.min).isoformat() if event.get('parsed_timestamp') else None,
            'priority': event.get('priority', 0)
        }
    
    def calculate_confidence_score(self, event: Dict[str, Any]) -> float:
        """Calculate confidence score for the extracted event"""
        score = 0.0
        
        # Base score for having an event
        if event:
            score += 0.3
        
        # Score for timestamp
        if event.get('parsed_timestamp') and event['parsed_timestamp'] != datetime.min:
            score += 0.3
        
        # Score for recognized status
        if event.get('priority', 0) > 10:
            score += 0.2
        
        # Score for location
        if event.get('location') and event['location'] != 'Unknown':
            score += 0.1
        
        # Score for extraction method
        if event.get('source') in ['container', 'json']:
            score += 0.1
        
        return min(score, 1.0)
    
    def create_no_events_result(self, carrier: str) -> Dict[str, Any]:
        """Create result when no events are found - but treat as valid response"""
        return {
            'success': True,  # This is a valid response, just no tracking data available
            'status': 'No tracking information available',
            'location': 'Contact carrier for details',
            'timestamp': 'Unknown',
            'event_description': 'PRO number was processed but no tracking events found',
            'is_delivered': False,
            'confidence_score': 0.6,  # Moderate confidence - we got a valid response
            'carrier': carrier,
            'extraction_method': 'no_events_found',
            'note': 'Valid response received but no tracking events available - PRO may be too new or already completed'
        }
    
    def create_error_result(self, error_message: str, carrier: str) -> Dict[str, Any]:
        """Create result when extraction fails"""
        return {
            'success': False,
            'status': 'Extraction failed',
            'location': 'Unknown',
            'timestamp': 'Unknown',
            'event_description': 'Event extraction failed',
            'is_delivered': False,
            'confidence_score': 0.0,
            'carrier': carrier,
            'extraction_method': 'error',
            'error': error_message
        } 