#!/usr/bin/env python3
"""
Comprehensive Test for Barrier-Breaking Tracking System
Tests the Apple Silicon Estes client and CloudFlare bypass FedEx client
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.backend.barrier_breaking_tracking_system import (
    BarrierBreakingTrackingSystem,
    track_estes_barrier_solved,
    track_fedex_barrier_solved,
    track_sync_with_barriers_solved
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('barrier_breaking_test.log')
    ]
)

logger = logging.getLogger(__name__)

class BarrierBreakingTestSuite:
    """Test suite for the barrier-breaking tracking system"""
    
    def __init__(self):
        self.system = BarrierBreakingTrackingSystem()
        self.test_results = []
        
        # Test tracking numbers (replace with real ones for testing)
        self.test_tracking_numbers = {
            'estes': [
                '1234567890',  # 10-digit Estes format
                '01234567890',  # 11-digit Estes format
                '2345678901',
                '3456789012'
            ],
            'fedex': [
                '100123456789',  # 12-digit FedEx format
                '10012345678901',  # 14-digit FedEx format
                '100234567890',
                '100345678901'
            ],
            'peninsula': [
                '12345678',  # 8-digit Peninsula format
                '23456789',
                'PEN12345',
                'P1234567'
            ],
            'rl': [
                '123456789',  # 9-digit R&L format
                '234567890',
                'RL1234567',
                'R12345678'
            ]
        }
    
    def test_system_initialization(self):
        """Test system initialization and status"""
        logger.info("🧪 Testing system initialization...")
        
        try:
            status = self.system.get_system_status()
            
            result = {
                'test_name': 'System Initialization',
                'success': True,
                'details': {
                    'system_name': status['system_name'],
                    'version': status['version'],
                    'capabilities': status['capabilities'],
                    'barriers_solved': status['barriers_solved'],
                    'supported_carriers': status['supported_carriers']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ System initialization successful")
            logger.info(f"💪 Barriers solved: {len(status['barriers_solved'])}")
            logger.info(f"🚛 Supported carriers: {len(status['supported_carriers'])}")
            
        except Exception as e:
            result = {
                'test_name': 'System Initialization',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ System initialization failed: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_carrier_detection(self):
        """Test carrier detection logic"""
        logger.info("🧪 Testing carrier detection...")
        
        detection_tests = [
            ('1234567890', 'estes'),
            ('01234567890', 'estes'),
            ('100123456789', 'fedex'),
            ('10012345678901', 'fedex'),
            ('12345678', 'peninsula'),
            ('PEN12345', 'peninsula'),
            ('123456789', 'rl'),
            ('RL1234567', 'rl'),
            ('UNKNOWN123', 'unknown')
        ]
        
        successful_detections = 0
        failed_detections = 0
        detection_details = []
        
        for tracking_number, expected_carrier in detection_tests:
            try:
                detected_carrier = self.system.detect_carrier(tracking_number)
                is_correct = detected_carrier == expected_carrier
                
                if is_correct:
                    successful_detections += 1
                    logger.info(f"✅ {tracking_number} -> {detected_carrier} (correct)")
                else:
                    failed_detections += 1
                    logger.warning(f"❌ {tracking_number} -> {detected_carrier} (expected {expected_carrier})")
                
                detection_details.append({
                    'tracking_number': tracking_number,
                    'expected': expected_carrier,
                    'detected': detected_carrier,
                    'correct': is_correct
                })
                
            except Exception as e:
                failed_detections += 1
                logger.error(f"❌ Detection error for {tracking_number}: {e}")
                detection_details.append({
                    'tracking_number': tracking_number,
                    'expected': expected_carrier,
                    'detected': 'error',
                    'correct': False,
                    'error': str(e)
                })
        
        success_rate = (successful_detections / len(detection_tests)) * 100
        
        result = {
            'test_name': 'Carrier Detection',
            'success': success_rate >= 90,  # 90% success rate threshold
            'details': {
                'total_tests': len(detection_tests),
                'successful_detections': successful_detections,
                'failed_detections': failed_detections,
                'success_rate': success_rate,
                'detection_details': detection_details
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Carrier detection success rate: {success_rate:.1f}%")
        self.test_results.append(result)
        return result
    
    async def test_apple_silicon_estes_barrier(self):
        """Test Apple Silicon Estes barrier breakthrough"""
        logger.info("🧪 Testing Apple Silicon Estes barrier breakthrough...")
        
        successful_tracks = 0
        failed_tracks = 0
        track_details = []
        
        for tracking_number in self.test_tracking_numbers['estes']:
            try:
                logger.info(f"🔧 Testing Apple Silicon barrier for Estes: {tracking_number}")
                start_time = time.time()
                
                result = await self.system.track_estes_with_barriers_solved(tracking_number)
                
                elapsed_time = time.time() - start_time
                
                if result.get('success'):
                    successful_tracks += 1
                    logger.info(f"✅ Apple Silicon barrier solved for {tracking_number}")
                    logger.info(f"💪 Barrier solved: {result.get('barrier_solved', 'Unknown')}")
                else:
                    failed_tracks += 1
                    logger.warning(f"❌ Apple Silicon barrier failed for {tracking_number}: {result.get('error')}")
                
                track_details.append({
                    'tracking_number': tracking_number,
                    'success': result.get('success', False),
                    'method': result.get('method', 'Unknown'),
                    'barrier_solved': result.get('barrier_solved', 'None'),
                    'elapsed_time': elapsed_time,
                    'error': result.get('error') if not result.get('success') else None
                })
                
            except Exception as e:
                failed_tracks += 1
                logger.error(f"❌ Apple Silicon test error for {tracking_number}: {e}")
                track_details.append({
                    'tracking_number': tracking_number,
                    'success': False,
                    'error': str(e),
                    'elapsed_time': 0
                })
        
        total_tests = len(self.test_tracking_numbers['estes'])
        success_rate = (successful_tracks / total_tests) * 100 if total_tests > 0 else 0
        
        result = {
            'test_name': 'Apple Silicon Estes Barrier',
            'success': success_rate >= 75,  # 75% success rate threshold
            'details': {
                'total_tests': total_tests,
                'successful_tracks': successful_tracks,
                'failed_tracks': failed_tracks,
                'success_rate': success_rate,
                'target_success_rate': '75-85%',
                'barrier_type': 'Apple Silicon ARM64 CPU Architecture',
                'track_details': track_details
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Apple Silicon Estes barrier success rate: {success_rate:.1f}%")
        self.test_results.append(result)
        return result
    
    async def test_cloudflare_fedex_barrier(self):
        """Test CloudFlare FedEx barrier breakthrough"""
        logger.info("🧪 Testing CloudFlare FedEx barrier breakthrough...")
        
        successful_tracks = 0
        failed_tracks = 0
        track_details = []
        
        for tracking_number in self.test_tracking_numbers['fedex']:
            try:
                logger.info(f"🔧 Testing CloudFlare barrier for FedEx: {tracking_number}")
                start_time = time.time()
                
                result = await self.system.track_fedex_with_barriers_solved(tracking_number)
                
                elapsed_time = time.time() - start_time
                
                if result.get('success'):
                    successful_tracks += 1
                    logger.info(f"✅ CloudFlare barrier solved for {tracking_number}")
                    logger.info(f"💪 Barrier solved: {result.get('barrier_solved', 'Unknown')}")
                else:
                    failed_tracks += 1
                    logger.warning(f"❌ CloudFlare barrier failed for {tracking_number}: {result.get('error')}")
                
                track_details.append({
                    'tracking_number': tracking_number,
                    'success': result.get('success', False),
                    'method': result.get('method', 'Unknown'),
                    'barrier_solved': result.get('barrier_solved', 'None'),
                    'elapsed_time': elapsed_time,
                    'error': result.get('error') if not result.get('success') else None
                })
                
            except Exception as e:
                failed_tracks += 1
                logger.error(f"❌ CloudFlare test error for {tracking_number}: {e}")
                track_details.append({
                    'tracking_number': tracking_number,
                    'success': False,
                    'error': str(e),
                    'elapsed_time': 0
                })
        
        total_tests = len(self.test_tracking_numbers['fedex'])
        success_rate = (successful_tracks / total_tests) * 100 if total_tests > 0 else 0
        
        result = {
            'test_name': 'CloudFlare FedEx Barrier',
            'success': success_rate >= 60,  # 60% success rate threshold
            'details': {
                'total_tests': total_tests,
                'successful_tracks': successful_tracks,
                'failed_tracks': failed_tracks,
                'success_rate': success_rate,
                'target_success_rate': '60-75%',
                'barrier_type': 'CloudFlare Protection + TLS Fingerprinting',
                'track_details': track_details
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🎯 CloudFlare FedEx barrier success rate: {success_rate:.1f}%")
        self.test_results.append(result)
        return result
    
    async def test_integrated_system(self):
        """Test the integrated barrier-breaking system"""
        logger.info("🧪 Testing integrated barrier-breaking system...")
        
        # Collect all test tracking numbers
        all_tracking_numbers = []
        for carrier_numbers in self.test_tracking_numbers.values():
            all_tracking_numbers.extend(carrier_numbers)
        
        try:
            logger.info(f"📦 Testing {len(all_tracking_numbers)} tracking numbers...")
            start_time = time.time()
            
            result = await self.system.track_multiple_shipments(all_tracking_numbers)
            
            elapsed_time = time.time() - start_time
            
            # Analyze results by carrier
            carrier_results = {}
            for track_result in result['results']:
                carrier = track_result.get('carrier', 'unknown')
                if carrier not in carrier_results:
                    carrier_results[carrier] = {'successful': 0, 'failed': 0, 'total': 0}
                
                carrier_results[carrier]['total'] += 1
                if track_result.get('success'):
                    carrier_results[carrier]['successful'] += 1
                else:
                    carrier_results[carrier]['failed'] += 1
            
            # Calculate success rates by carrier
            for carrier, stats in carrier_results.items():
                stats['success_rate'] = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
            
            test_result = {
                'test_name': 'Integrated Barrier-Breaking System',
                'success': result['success_rate'] >= 70,  # 70% overall success rate threshold
                'details': {
                    'total_shipments': result['total_shipments'],
                    'successful_tracks': result['successful_tracks'],
                    'failed_tracks': result['failed_tracks'],
                    'overall_success_rate': result['success_rate'],
                    'barriers_solved': result['barriers_solved'],
                    'elapsed_time': elapsed_time,
                    'carrier_breakdown': carrier_results,
                    'individual_results': result['results']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Integrated system success rate: {result['success_rate']:.1f}%")
            logger.info(f"💪 Barriers solved: {', '.join(result['barriers_solved'])}")
            
            for carrier, stats in carrier_results.items():
                logger.info(f"🚛 {carrier}: {stats['success_rate']:.1f}% ({stats['successful']}/{stats['total']})")
            
        except Exception as e:
            test_result = {
                'test_name': 'Integrated Barrier-Breaking System',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"❌ Integrated system test failed: {e}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def run_all_tests(self):
        """Run all tests in the barrier-breaking test suite"""
        logger.info("🚀 Starting Barrier-Breaking Tracking System Test Suite")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_system_initialization,
            self.test_carrier_detection,
            self.test_apple_silicon_estes_barrier,
            self.test_cloudflare_fedex_barrier,
            self.test_integrated_system
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test in tests:
            try:
                if asyncio.iscoroutinefunction(test):
                    result = await test()
                else:
                    result = test()
                
                if result.get('success'):
                    passed_tests += 1
                    logger.info(f"✅ {result['test_name']} - PASSED")
                else:
                    failed_tests += 1
                    logger.error(f"❌ {result['test_name']} - FAILED")
                
                logger.info("-" * 80)
                
            except Exception as e:
                failed_tests += 1
                logger.error(f"❌ Test execution error: {e}")
                logger.info("-" * 80)
        
        # Generate final summary
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        elapsed_time = time.time() - start_time
        
        summary = {
            'test_suite': 'Barrier-Breaking Tracking System',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'elapsed_time': elapsed_time,
            'timestamp': datetime.now().isoformat(),
            'individual_results': self.test_results
        }
        
        # Save results to file
        with open('barrier_breaking_test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("=" * 80)
        logger.info("🎯 BARRIER-BREAKING TEST SUITE COMPLETE")
        logger.info(f"📊 Overall Success Rate: {success_rate:.1f}%")
        logger.info(f"✅ Passed: {passed_tests}/{total_tests}")
        logger.info(f"❌ Failed: {failed_tests}/{total_tests}")
        logger.info(f"⏱️  Total Time: {elapsed_time:.2f}s")
        logger.info("=" * 80)
        
        return summary

async def main():
    """Run the barrier-breaking test suite"""
    test_suite = BarrierBreakingTestSuite()
    return await test_suite.run_all_tests()

if __name__ == "__main__":
    # Run the test suite
    results = asyncio.run(main())
    
    # Print final status
    if results['success_rate'] >= 70:
        print("\n🎉 BARRIER-BREAKING SYSTEM: READY FOR DEPLOYMENT")
        print(f"💪 Successfully solved technical barriers with {results['success_rate']:.1f}% success rate")
        sys.exit(0)
    else:
        print(f"\n⚠️  BARRIER-BREAKING SYSTEM: NEEDS IMPROVEMENT")
        print(f"❌ Current success rate: {results['success_rate']:.1f}% (target: 70%+)")
        sys.exit(1) 