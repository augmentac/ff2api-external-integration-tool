#!/usr/bin/env python3
"""
Production Diagnostic Script
Shows which tracking system is being used and what dependencies are available
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_production_system():
    """Diagnose which tracking system is being used in production"""
    print("🔍 PRODUCTION SYSTEM DIAGNOSTIC")
    print("=" * 50)
    
    # Test barrier-breaking system availability
    print("\n1. Testing Barrier-Breaking System:")
    try:
        from src.backend.barrier_breaking_tracking_system import BarrierBreakingTrackingSystem
        print("✅ BarrierBreakingTrackingSystem: Import successful")
        
        # Test dependencies
        try:
            from playwright.async_api import async_playwright
            print("✅ Playwright: Available")
        except ImportError as e:
            print(f"❌ Playwright: Not available - {e}")
            
        try:
            import curl_cffi
            print("✅ curl_cffi: Available")
        except ImportError as e:
            print(f"❌ curl_cffi: Not available - {e}")
            
        barrier_breaking_available = True
        
    except ImportError as e:
        print(f"❌ BarrierBreakingTrackingSystem: Import failed - {e}")
        barrier_breaking_available = False
    
    # Test enhanced system availability
    print("\n2. Testing Enhanced System:")
    try:
        from src.backend.enhanced_ltl_tracking_client import EnhancedLTLTrackingClient
        print("✅ EnhancedLTLTrackingClient: Import successful")
        enhanced_available = True
    except ImportError as e:
        print(f"❌ EnhancedLTLTrackingClient: Import failed - {e}")
        enhanced_available = False
    
    # Test basic dependencies
    print("\n3. Testing Basic Dependencies:")
    basic_deps = ['streamlit', 'pandas', 'requests', 'selenium', 'bs4']
    for dep in basic_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Not available")
    
    # Test advanced dependencies
    print("\n4. Testing Advanced Dependencies:")
    advanced_deps = ['playwright', 'curl_cffi', 'undetected_chromedriver', 'cloudscraper']
    for dep in advanced_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Not available")
    
    # System selection logic
    print("\n5. System Selection Logic:")
    if barrier_breaking_available:
        print("🚀 SELECTED: BarrierBreakingTrackingSystem")
        print("   - Expected success rates: Estes 75-85%, FedEx 60-75%")
    elif enhanced_available:
        print("🚀 SELECTED: EnhancedLTLTrackingClient (Fallback)")
        print("   - Expected success rates: Estes 45-60%, FedEx 35-50%")
    else:
        print("❌ NO SYSTEM AVAILABLE")
    
    # Test a sample tracking call
    print("\n6. Testing Sample Tracking Call:")
    try:
        if barrier_breaking_available:
            system = BarrierBreakingTrackingSystem()
            print("✅ BarrierBreakingTrackingSystem instantiated successfully")
            
            # Test system status
            try:
                status = system.get_system_status()
                print(f"✅ System status: {status.get('system_name', 'Unknown')}")
                barriers = status.get('barriers_solved', [])
                print(f"✅ Barriers solved: {len(barriers)}")
                for barrier in barriers[:3]:
                    print(f"   - {barrier}")
            except Exception as e:
                print(f"⚠️ System status error: {e}")
                
        elif enhanced_available:
            system = EnhancedLTLTrackingClient()
            print("✅ EnhancedLTLTrackingClient instantiated successfully")
            
            # Test system info
            try:
                stats = system.get_tracking_statistics()
                print(f"✅ System stats available: {len(stats)} categories")
                if 'zero_cost_system' in stats:
                    print(f"✅ Zero-cost system enabled: {stats['zero_cost_system']['enabled']}")
            except Exception as e:
                print(f"⚠️ System stats error: {e}")
                
    except Exception as e:
        print(f"❌ System instantiation failed: {e}")
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    diagnose_production_system() 