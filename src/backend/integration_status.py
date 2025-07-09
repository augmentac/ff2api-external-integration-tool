"""
Integration Status Service

This service monitors the health and performance of all integrations including:
- API endpoints
- Web scrapers (LTL carriers)
- Database connectivity
- Recent activity metrics
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
import requests
from requests.exceptions import RequestException, Timeout

from .carrier_detection import CarrierDetector
from .ltl_tracking_client import LTLTrackingClient
from .database import DatabaseManager


@dataclass
class IntegrationStatus:
    """Status information for an integration"""
    integration_id: str
    name: str
    type: str
    status: str  # 'healthy', 'degraded', 'failed', 'unknown'
    last_check: datetime
    response_time: Optional[float] = None
    success_rate: Optional[float] = None
    error_message: Optional[str] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    daily_requests: int = 0
    daily_successes: int = 0
    daily_failures: int = 0


@dataclass
class SystemOverview:
    """Overall system health overview"""
    overall_status: str  # 'healthy', 'degraded', 'failed'
    total_integrations: int
    healthy_integrations: int
    degraded_integrations: int
    failed_integrations: int
    last_updated: datetime
    total_requests_today: int
    total_successes_today: int
    total_failures_today: int


class IntegrationStatusService:
    """Service for monitoring integration health and performance"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.carrier_detector = CarrierDetector()
        self.tracking_client = LTLTrackingClient()
        self.logger = logging.getLogger(__name__)
        
    def get_system_overview(self, brokerage_name: str) -> SystemOverview:
        """Get overall system health overview"""
        try:
            # Get all integration statuses
            all_statuses = self.get_all_integration_statuses(brokerage_name)
            
            # Calculate counts
            total = len(all_statuses)
            healthy = len([s for s in all_statuses if s.status == 'healthy'])
            degraded = len([s for s in all_statuses if s.status == 'degraded'])
            failed = len([s for s in all_statuses if s.status == 'failed'])
            
            # Determine overall status
            if failed > 0:
                overall_status = 'failed'
            elif degraded > 0:
                overall_status = 'degraded'
            elif healthy > 0:
                overall_status = 'healthy'
            else:
                overall_status = 'unknown'
            
            # Calculate totals
            total_requests = sum(s.daily_requests for s in all_statuses)
            total_successes = sum(s.daily_successes for s in all_statuses)
            total_failures = sum(s.daily_failures for s in all_statuses)
            
            return SystemOverview(
                overall_status=overall_status,
                total_integrations=total,
                healthy_integrations=healthy,
                degraded_integrations=degraded,
                failed_integrations=failed,
                last_updated=datetime.now(),
                total_requests_today=total_requests,
                total_successes_today=total_successes,
                total_failures_today=total_failures
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system overview: {e}")
            return SystemOverview(
                overall_status='unknown',
                total_integrations=0,
                healthy_integrations=0,
                degraded_integrations=0,
                failed_integrations=0,
                last_updated=datetime.now(),
                total_requests_today=0,
                total_successes_today=0,
                total_failures_today=0
            )
    
    def get_all_integration_statuses(self, brokerage_name: str) -> List[IntegrationStatus]:
        """Get status for all integrations"""
        statuses = []
        
        # Get API integrations
        api_statuses = self.get_api_integration_statuses(brokerage_name)
        statuses.extend(api_statuses)
        
        # Get web scraper statuses (LTL carriers)
        web_scraper_statuses = self.get_web_scraper_statuses()
        statuses.extend(web_scraper_statuses)
        
        # Get database status
        db_status = self.get_database_status()
        statuses.append(db_status)
        
        return statuses
    
    def get_api_integration_statuses(self, brokerage_name: str) -> List[IntegrationStatus]:
        """Get status for API integrations"""
        statuses = []
        
        try:
            # Get all API integrations for this brokerage
            integrations = self.db_manager.get_external_integrations(brokerage_name)
            api_integrations = [i for i in integrations if i['type_name'] != 'web_scraper']
            
            for integration in api_integrations:
                status = self._check_api_integration_status(integration)
                statuses.append(status)
                
        except Exception as e:
            self.logger.error(f"Error getting API integration statuses: {e}")
            
        return statuses
    
    def get_web_scraper_statuses(self) -> List[IntegrationStatus]:
        """Get status for web scraper integrations (LTL carriers)"""
        statuses = []
        
        try:
            # Get all carriers from detector
            all_carriers = self.carrier_detector.get_all_carriers()
            
            # Focus on priority carriers (our 5 main ones)
            priority_carriers = ['fedex_freight', 'rl_carriers', 'estes', 'tforce_freight', 'peninsula_truck_lines']
            
            for carrier_code in priority_carriers:
                carrier_info = self.carrier_detector.get_carrier_info(carrier_code)
                if carrier_info:
                    status = self._check_web_scraper_status(carrier_code, carrier_info)
                    statuses.append(status)
            
            # Add a summary status for legacy carriers
            legacy_carriers = [c for c in all_carriers if c['carrier_code'] not in priority_carriers]
            if legacy_carriers:
                legacy_status = self._create_legacy_carrier_status(legacy_carriers)
                statuses.append(legacy_status)
                
        except Exception as e:
            self.logger.error(f"Error getting web scraper statuses: {e}")
            
        return statuses
    
    def get_database_status(self) -> IntegrationStatus:
        """Get database connectivity status"""
        try:
            start_time = time.time()
            
            # Test database connection
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            conn.close()
            
            response_time = time.time() - start_time
            
            # Get today's tracking statistics
            today_stats = self._get_today_tracking_stats()
            
            return IntegrationStatus(
                integration_id='database',
                name='Database Connection',
                type='database',
                status='healthy',
                last_check=datetime.now(),
                response_time=response_time,
                success_rate=100.0,
                error_message=None,
                last_success=datetime.now(),
                last_failure=None,
                daily_requests=today_stats['total_requests'],
                daily_successes=today_stats['successful_requests'],
                daily_failures=today_stats['failed_requests']
            )
            
        except Exception as e:
            return IntegrationStatus(
                integration_id='database',
                name='Database Connection',
                type='database',
                status='failed',
                last_check=datetime.now(),
                response_time=None,
                success_rate=0.0,
                error_message=str(e),
                last_success=None,
                last_failure=datetime.now(),
                daily_requests=0,
                daily_successes=0,
                daily_failures=1
            )
    
    def _check_api_integration_status(self, integration: Dict) -> IntegrationStatus:
        """Check the status of an API integration"""
        try:
            # Get recent execution history
            history = self._get_recent_execution_history(integration['id'])
            
            if not history:
                return IntegrationStatus(
                    integration_id=str(integration['id']),
                    name=integration['name'],
                    type=integration['type_name'],
                    status='unknown',
                    last_check=datetime.now(),
                    error_message='No execution history found'
                )
            
            # Calculate success rate from recent history
            total_executions = len(history)
            successful_executions = len([h for h in history if h['status'] == 'success'])
            success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
            
            # Determine status based on success rate
            if success_rate >= 90:
                status = 'healthy'
            elif success_rate >= 70:
                status = 'degraded'
            else:
                status = 'failed'
            
            # Get most recent execution
            recent_execution = history[0] if history else None
            last_success = None
            last_failure = None
            
            if recent_execution:
                if recent_execution['status'] == 'success':
                    last_success = datetime.fromisoformat(recent_execution['executed_at'])
                else:
                    last_failure = datetime.fromisoformat(recent_execution['executed_at'])
            
            # Get today's statistics
            today_stats = self._get_today_integration_stats(integration['id'])
            
            return IntegrationStatus(
                integration_id=str(integration['id']),
                name=integration['name'],
                type=integration['type_name'],
                status=status,
                last_check=datetime.now(),
                response_time=recent_execution.get('response_time') if recent_execution else None,
                success_rate=success_rate,
                error_message=recent_execution.get('error_message') if recent_execution and recent_execution['status'] != 'success' else None,
                last_success=last_success,
                last_failure=last_failure,
                daily_requests=today_stats['total_requests'],
                daily_successes=today_stats['successful_requests'],
                daily_failures=today_stats['failed_requests']
            )
            
        except Exception as e:
            return IntegrationStatus(
                integration_id=str(integration['id']),
                name=integration['name'],
                type=integration['type_name'],
                status='failed',
                last_check=datetime.now(),
                error_message=f'Error checking status: {str(e)}'
            )
    
    def _check_web_scraper_status(self, carrier_code: str, carrier_info: Dict) -> IntegrationStatus:
        """Check the status of a web scraper integration"""
        try:
            # Test carrier connection
            connection_test = self.tracking_client.test_carrier_connection(carrier_code)
            
            if connection_test['success']:
                status = 'healthy'
                error_message = None
                response_time = connection_test.get('response_time', 0)
                last_success = datetime.now()
                last_failure = None
            else:
                status = 'degraded'  # Degraded instead of failed for web scrapers
                error_message = connection_test.get('error', 'Connection test failed')
                response_time = None
                last_success = None
                last_failure = datetime.now()
            
            # Get today's tracking statistics for this carrier
            today_stats = self._get_today_carrier_stats(carrier_code)
            
            # Calculate success rate
            total_requests = today_stats['total_requests']
            successful_requests = today_stats['successful_requests']
            success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else None
            
            return IntegrationStatus(
                integration_id=f'web_scraper_{carrier_code}',
                name=carrier_info['name'],
                type='web_scraper',
                status=status,
                last_check=datetime.now(),
                response_time=response_time,
                success_rate=success_rate,
                error_message=error_message,
                last_success=last_success,
                last_failure=last_failure,
                daily_requests=total_requests,
                daily_successes=successful_requests,
                daily_failures=today_stats['failed_requests']
            )
            
        except Exception as e:
            return IntegrationStatus(
                integration_id=f'web_scraper_{carrier_code}',
                name=carrier_info['name'],
                type='web_scraper',
                status='failed',
                last_check=datetime.now(),
                error_message=f'Error checking status: {str(e)}'
            )
    
    def _create_legacy_carrier_status(self, legacy_carriers: List[Dict]) -> IntegrationStatus:
        """Create a summary status for legacy carriers"""
        return IntegrationStatus(
            integration_id='legacy_carriers',
            name=f'Legacy Carriers ({len(legacy_carriers)} available)',
            type='web_scraper_legacy',
            status='healthy',
            last_check=datetime.now(),
            response_time=None,
            success_rate=None,
            error_message=None,
            last_success=None,
            last_failure=None,
            daily_requests=0,
            daily_successes=0,
            daily_failures=0
        )
    
    def _get_recent_execution_history(self, integration_id: int, limit: int = 10) -> List[Dict]:
        """Get recent execution history for an integration"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT executed_at, status, response_time, error_message
                FROM integration_execution_history
                WHERE integration_id = ?
                ORDER BY executed_at DESC
                LIMIT ?
            ''', (integration_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'executed_at': row[0],
                    'status': row[1],
                    'response_time': row[2],
                    'error_message': row[3]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting execution history: {e}")
            return []
    
    def _get_today_integration_stats(self, integration_id: int) -> Dict[str, int]:
        """Get today's statistics for an integration"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN status != 'success' THEN 1 ELSE 0 END) as failed_requests
                FROM integration_execution_history
                WHERE integration_id = ? AND DATE(executed_at) = ?
            ''', (integration_id, today))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_requests': result[0] or 0,
                'successful_requests': result[1] or 0,
                'failed_requests': result[2] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting today's integration stats: {e}")
            return {'total_requests': 0, 'successful_requests': 0, 'failed_requests': 0}
    
    def _get_today_carrier_stats(self, carrier_code: str) -> Dict[str, int]:
        """Get today's statistics for a carrier"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN scrape_success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN scrape_success = 0 THEN 1 ELSE 0 END) as failed_requests
                FROM tracking_results
                WHERE carrier_name LIKE ? AND DATE(created_at) = ?
            ''', (f'%{carrier_code}%', today))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_requests': result[0] or 0,
                'successful_requests': result[1] or 0,
                'failed_requests': result[2] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting today's carrier stats: {e}")
            return {'total_requests': 0, 'successful_requests': 0, 'failed_requests': 0}
    
    def _get_today_tracking_stats(self) -> Dict[str, int]:
        """Get today's tracking statistics"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN scrape_success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN scrape_success = 0 THEN 1 ELSE 0 END) as failed_requests
                FROM tracking_results
                WHERE DATE(created_at) = ?
            ''', (today,))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_requests': result[0] or 0,
                'successful_requests': result[1] or 0,
                'failed_requests': result[2] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting today's tracking stats: {e}")
            return {'total_requests': 0, 'successful_requests': 0, 'failed_requests': 0}
    
    def get_recent_activity(self, brokerage_name: str, hours: int = 24) -> List[Dict]:
        """Get recent activity across all integrations"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            since_time_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get API integration activity
            cursor.execute('''
                SELECT ieh.executed_at, ei.integration_name, 'API' as type, 
                       ieh.status, ieh.response_time, ieh.error_message
                FROM integration_execution_history ieh
                JOIN external_integrations ei ON ieh.integration_id = ei.id
                WHERE ei.brokerage_name = ? AND ieh.executed_at >= ?
                ORDER BY ieh.executed_at DESC
                LIMIT 50
            ''', (brokerage_name, since_time_str))
            
            activity = []
            for row in cursor.fetchall():
                activity.append({
                    'timestamp': row[0],
                    'integration_name': row[1],
                    'type': row[2],
                    'status': row[3],
                    'response_time': row[4],
                    'error_message': row[5]
                })
            
            # Get web scraper activity
            cursor.execute('''
                SELECT created_at, carrier_name, 'Web Scraper' as type,
                       CASE WHEN scrape_success = 1 THEN 'success' ELSE 'failed' END as status,
                       NULL as response_time, error_message
                FROM tracking_results
                WHERE created_at >= ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (since_time_str,))
            
            for row in cursor.fetchall():
                activity.append({
                    'timestamp': row[0],
                    'integration_name': row[1],
                    'type': row[2],
                    'status': row[3],
                    'response_time': row[4],
                    'error_message': row[5]
                })
            
            conn.close()
            
            # Sort by timestamp
            activity.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return activity[:50]  # Return most recent 50
            
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}")
            return []
    
    def refresh_all_statuses(self, brokerage_name: str) -> None:
        """Refresh all integration statuses (can be called on-demand)"""
        try:
            # This will trigger fresh checks for all integrations
            self.get_all_integration_statuses(brokerage_name)
            self.logger.info(f"Refreshed all integration statuses for {brokerage_name}")
        except Exception as e:
            self.logger.error(f"Error refreshing statuses: {e}")
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'tracking_client'):
            self.tracking_client.close() 