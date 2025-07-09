"""
External Integration Client for FF2API
Handles integration with external APIs and data sources
"""

import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

class ExternalIntegrationClient:
    """Main client for handling external integrations"""
    
    def __init__(self, integration_config: Dict[str, Any]):
        self.integration_config = integration_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize integration handler based on type
        self.handler = self._get_integration_handler()
    
    def _get_integration_handler(self) -> 'BaseIntegrationHandler':
        """Get the appropriate integration handler based on type"""
        integration_type = self.integration_config.get('type_name')
        
        handlers = {
            'ltl_carrier': LTLCarrierHandler,
            'freight_api': FreightAPIHandler,
            'tracking_api': TrackingAPIHandler,
            'pricing_api': PricingAPIHandler,
            'warehouse_api': WarehouseAPIHandler,
            'customs_api': CustomsAPIHandler,
            'edi_integration': EDIIntegrationHandler,
            'custom_integration': CustomIntegrationHandler
        }
        
        handler_class = handlers.get(integration_type, CustomIntegrationHandler)
        return handler_class(self.integration_config)
    
    def execute_integration(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute the integration and return results"""
        try:
            start_time = time.time()
            
            # Execute the integration
            result = self.handler.execute(input_data)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'SUCCESS',
                'execution_time': execution_time,
                'records_processed': result.get('records_processed', 0),
                'records_success': result.get('records_success', 0),
                'records_failed': result.get('records_failed', 0),
                'data': result.get('data', []),
                'error_log': result.get('error_log', [])
            }
            
        except Exception as e:
            self.logger.error(f"Integration execution failed: {e}")
            return {
                'status': 'FAILED',
                'execution_time': 0,
                'records_processed': 0,
                'records_success': 0,
                'records_failed': 0,
                'data': [],
                'error_log': [str(e)]
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the external API"""
        try:
            return self.handler.test_connection()
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'message': f"Connection test failed: {e}"
            }


class BaseIntegrationHandler(ABC):
    """Base class for all integration handlers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Setup authentication
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication for the session"""
        auth_config = self.config.get('auth_credentials', {})
        
        if 'api_key' in auth_config:
            header_name = auth_config.get('api_key_header', 'X-API-Key')
            self.session.headers.update({header_name: auth_config['api_key']})
        
        elif 'bearer_token' in auth_config:
            self.session.headers.update({
                'Authorization': f"Bearer {auth_config['bearer_token']}"
            })
        
        elif 'username' in auth_config and 'password' in auth_config:
            self.session.auth = (auth_config['username'], auth_config['password'])
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FF2API-External-Integration/1.0'
        })
    
    @abstractmethod
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute the integration"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the external API"""
        pass
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a request with proper error handling and rate limiting"""
        base_url = self.config['config_data'].get('base_url', '')
        url = urljoin(base_url, endpoint)
        
        # Add timeout
        timeout = self.config['config_data'].get('timeout', 30)
        kwargs['timeout'] = timeout
        
        # Make request
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        
        return response
    
    def _handle_rate_limit(self):
        """Handle rate limiting"""
        rate_limit = self.config['config_data'].get('rate_limit', 100)
        # Simple rate limiting - sleep for 60/rate_limit seconds
        time.sleep(60 / rate_limit)


class LTLCarrierHandler(BaseIntegrationHandler):
    """Handler for LTL carrier integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute LTL carrier integration"""
        try:
            # Get carrier-specific data
            carrier_code = self.config['config_data'].get('carrier_code', '')
            service_types = self.config['config_data'].get('service_types', ['LTL'])
            
            results = []
            errors = []
            
            # Example: Get rate quotes for shipments
            if input_data and isinstance(input_data, list):
                for shipment in input_data:
                    try:
                        rate_quote = self._get_rate_quote(shipment)
                        results.append(rate_quote)
                    except Exception as e:
                        errors.append(f"Error getting rate for shipment {shipment.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"LTL carrier integration failed: {e}")
            raise
    
    def _get_rate_quote(self, shipment: Dict[str, Any]) -> Dict[str, Any]:
        """Get rate quote for a shipment"""
        # Example implementation - this would be carrier-specific
        payload = {
            'origin': shipment.get('origin'),
            'destination': shipment.get('destination'),
            'weight': shipment.get('weight'),
            'service_type': 'LTL'
        }
        
        response = self._make_request('POST', '/rates/quote', json=payload)
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to LTL carrier API"""
        try:
            response = self._make_request('GET', '/health')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class FreightAPIHandler(BaseIntegrationHandler):
    """Handler for generic freight API integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute freight API integration"""
        try:
            supported_modes = self.config['config_data'].get('supported_modes', ['LTL', 'FTL'])
            
            results = []
            errors = []
            
            # Example: Get freight information
            if input_data and isinstance(input_data, list):
                for freight_request in input_data:
                    try:
                        freight_info = self._get_freight_info(freight_request)
                        results.append(freight_info)
                    except Exception as e:
                        errors.append(f"Error getting freight info for {freight_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Freight API integration failed: {e}")
            raise
    
    def _get_freight_info(self, freight_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get freight information"""
        response = self._make_request('GET', f"/freight/{freight_request.get('id')}")
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to freight API"""
        try:
            response = self._make_request('GET', '/status')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class TrackingAPIHandler(BaseIntegrationHandler):
    """Handler for tracking API integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute tracking API integration"""
        try:
            tracking_methods = self.config['config_data'].get('tracking_methods', ['TRACKING_NUMBER'])
            
            results = []
            errors = []
            
            # Example: Get tracking information
            if input_data and isinstance(input_data, list):
                for tracking_request in input_data:
                    try:
                        tracking_info = self._get_tracking_info(tracking_request)
                        results.append(tracking_info)
                    except Exception as e:
                        errors.append(f"Error getting tracking info for {tracking_request.get('tracking_number', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Tracking API integration failed: {e}")
            raise
    
    def _get_tracking_info(self, tracking_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get tracking information"""
        tracking_number = tracking_request.get('tracking_number')
        response = self._make_request('GET', f"/tracking/{tracking_number}")
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to tracking API"""
        try:
            response = self._make_request('GET', '/ping')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class PricingAPIHandler(BaseIntegrationHandler):
    """Handler for pricing API integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute pricing API integration"""
        try:
            pricing_models = self.config['config_data'].get('pricing_models', ['SPOT_RATE'])
            currency = self.config['config_data'].get('currency', 'USD')
            
            results = []
            errors = []
            
            # Example: Get pricing information
            if input_data and isinstance(input_data, list):
                for pricing_request in input_data:
                    try:
                        pricing_info = self._get_pricing_info(pricing_request)
                        results.append(pricing_info)
                    except Exception as e:
                        errors.append(f"Error getting pricing info for {pricing_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Pricing API integration failed: {e}")
            raise
    
    def _get_pricing_info(self, pricing_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing information"""
        payload = {
            'origin': pricing_request.get('origin'),
            'destination': pricing_request.get('destination'),
            'weight': pricing_request.get('weight'),
            'service_type': pricing_request.get('service_type', 'LTL'),
            'currency': self.config['config_data'].get('currency', 'USD')
        }
        
        response = self._make_request('POST', '/pricing/calculate', json=payload)
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to pricing API"""
        try:
            response = self._make_request('GET', '/health')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class WarehouseAPIHandler(BaseIntegrationHandler):
    """Handler for warehouse API integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute warehouse API integration"""
        try:
            warehouse_locations = self.config['config_data'].get('warehouse_locations', [])
            operations = self.config['config_data'].get('operations', ['INBOUND', 'OUTBOUND'])
            
            results = []
            errors = []
            
            # Example: Get warehouse information
            if input_data and isinstance(input_data, list):
                for warehouse_request in input_data:
                    try:
                        warehouse_info = self._get_warehouse_info(warehouse_request)
                        results.append(warehouse_info)
                    except Exception as e:
                        errors.append(f"Error getting warehouse info for {warehouse_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Warehouse API integration failed: {e}")
            raise
    
    def _get_warehouse_info(self, warehouse_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get warehouse information"""
        response = self._make_request('GET', f"/warehouse/{warehouse_request.get('location')}")
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to warehouse API"""
        try:
            response = self._make_request('GET', '/status')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class CustomsAPIHandler(BaseIntegrationHandler):
    """Handler for customs API integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute customs API integration"""
        try:
            results = []
            errors = []
            
            # Example: Get customs information
            if input_data and isinstance(input_data, list):
                for customs_request in input_data:
                    try:
                        customs_info = self._get_customs_info(customs_request)
                        results.append(customs_info)
                    except Exception as e:
                        errors.append(f"Error getting customs info for {customs_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Customs API integration failed: {e}")
            raise
    
    def _get_customs_info(self, customs_request: Dict[str, Any]) -> Dict[str, Any]:
        """Get customs information"""
        response = self._make_request('GET', f"/customs/{customs_request.get('declaration_id')}")
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to customs API"""
        try:
            response = self._make_request('GET', '/health')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class EDIIntegrationHandler(BaseIntegrationHandler):
    """Handler for EDI integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute EDI integration"""
        try:
            standards = self.config['config_data'].get('standards', ['x12'])
            
            results = []
            errors = []
            
            # Example: Process EDI documents
            if input_data and isinstance(input_data, list):
                for edi_request in input_data:
                    try:
                        edi_info = self._process_edi_document(edi_request)
                        results.append(edi_info)
                    except Exception as e:
                        errors.append(f"Error processing EDI document {edi_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"EDI integration failed: {e}")
            raise
    
    def _process_edi_document(self, edi_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process EDI document"""
        # This would contain actual EDI processing logic
        # For now, return a placeholder
        return {
            'document_id': edi_request.get('id'),
            'status': 'processed',
            'message': 'EDI document processed successfully'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to EDI system"""
        try:
            # EDI systems might use different connection methods
            response = self._make_request('GET', '/status')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class CustomIntegrationHandler(BaseIntegrationHandler):
    """Handler for custom integrations"""
    
    def execute(self, input_data: Any = None) -> Dict[str, Any]:
        """Execute custom integration"""
        try:
            protocol = self.config['config_data'].get('protocol', 'REST')
            data_format = self.config['config_data'].get('data_format', 'JSON')
            
            results = []
            errors = []
            
            # Example: Generic processing
            if input_data and isinstance(input_data, list):
                for custom_request in input_data:
                    try:
                        custom_info = self._process_custom_request(custom_request)
                        results.append(custom_info)
                    except Exception as e:
                        errors.append(f"Error processing custom request {custom_request.get('id', 'unknown')}: {e}")
            
            return {
                'records_processed': len(input_data) if input_data else 0,
                'records_success': len(results),
                'records_failed': len(errors),
                'data': results,
                'error_log': errors
            }
            
        except Exception as e:
            self.logger.error(f"Custom integration failed: {e}")
            raise
    
    def _process_custom_request(self, custom_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process custom request"""
        # Generic processing based on configuration
        endpoint = custom_request.get('endpoint', '/')
        method = custom_request.get('method', 'GET')
        
        response = self._make_request(method, endpoint, json=custom_request.get('payload'))
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to custom API"""
        try:
            response = self._make_request('GET', '/')
            return {
                'success': True,
                'message': 'Connection successful',
                'details': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Connection failed: {e}"
            }


class OutputFileGenerator:
    """Generate output files from integration results"""
    
    def __init__(self, output_config: Dict[str, Any]):
        self.output_config = output_config
        self.logger = logging.getLogger(__name__)
    
    def generate_output_file(self, data: List[Dict[str, Any]], integration_name: str) -> str:
        """Generate output file from integration data"""
        try:
            output_format = self.output_config.get('output_format', 'CSV')
            output_name = self.output_config.get('output_name', 'integration_output')
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_pattern = self.output_config.get('file_naming_pattern', f"{output_name}_{integration_name}_{timestamp}")
            
            if output_format.upper() == 'CSV':
                filename = f"{filename_pattern}.csv"
                return self._generate_csv_file(data, filename)
            elif output_format.upper() == 'JSON':
                filename = f"{filename_pattern}.json"
                return self._generate_json_file(data, filename)
            elif output_format.upper() == 'EXCEL':
                filename = f"{filename_pattern}.xlsx"
                return self._generate_excel_file(data, filename)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
        except Exception as e:
            self.logger.error(f"Error generating output file: {e}")
            raise
    
    def _generate_csv_file(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Generate CSV output file"""
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        # Apply field selection if configured
        output_fields = self.output_config.get('output_fields')
        if output_fields:
            df = df[output_fields]
        
        # Save to file
        output_path = f"data/outputs/{filename}"
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def _generate_json_file(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Generate JSON output file"""
        output_path = f"data/outputs/{filename}"
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return output_path
    
    def _generate_excel_file(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Generate Excel output file"""
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        # Apply field selection if configured
        output_fields = self.output_config.get('output_fields')
        if output_fields:
            df = df[output_fields]
        
        # Save to file
        output_path = f"data/outputs/{filename}"
        df.to_excel(output_path, index=False)
        
        return output_path 