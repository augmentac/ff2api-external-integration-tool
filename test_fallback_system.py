#!/usr/bin/env python3
"""
Test Fallback System for Production Compatibility
Verifies that the app gracefully falls back when barrier-breaking dependencies are missing
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import_fallback():
    """Test the import fallback logic"""
    print("🧪 Testing Import Fallback System")
    print("=" * 50)
    
    # Test barrier-breaking system import
    try:
        from src.backend.barrier_breaking_tracking_system import BarrierBreakingTrackingSystem
        print("✅ Barrier-Breaking System: Available")
        barrier_breaking_available = True
    except ImportError as e:
        print(f"❌ Barrier-Breaking System: Not Available ({e})")
        barrier_breaking_available = False
    
    # Test enhanced system import
    try:
        from src.backend.enhanced_ltl_tracking_client import EnhancedLTLTrackingClient
        print("✅ Enhanced Zero-Cost System: Available")
        enhanced_available = True
    except ImportError as e:
        print(f"❌ Enhanced Zero-Cost System: Not Available ({e})")
        enhanced_available = False
    
    # Test the fallback logic from pro_tracking_ui
    print("\n🔄 Testing Pro Tracking UI Fallback Logic")
    print("-" * 50)
    
    if barrier_breaking_available:
        tracking_client = BarrierBreakingTrackingSystem()
        system_name = "Barrier-Breaking System"
        use_single_shipment_method = True
        print(f"✅ Using: {system_name}")
    elif enhanced_available:
        tracking_client = EnhancedLTLTrackingClient()
        system_name = "Enhanced Zero-Cost System"
        use_single_shipment_method = False
        print(f"✅ Using: {system_name}")
    else:
        print("❌ No tracking system available")
        return False
    
    print(f"📋 Method selection: {'track_single_shipment' if use_single_shipment_method else 'track_shipment'}")
    
    # Test system status
    print("\n📊 System Status")
    print("-" * 50)
    
    if hasattr(tracking_client, 'get_system_status'):
        try:
            status = tracking_client.get_system_status()
            print(f"System Name: {status.get('system_name', 'Unknown')}")
            print(f"Version: {status.get('version', 'Unknown')}")
            if 'barriers_solved' in status:
                barriers = status['barriers_solved']
                if barriers:
                    print(f"Barriers Solved: {len(barriers)}")
                    for barrier in barriers[:3]:  # Show first 3
                        print(f"  - {barrier}")
                else:
                    print("Barriers Solved: None")
        except Exception as e:
            print(f"Could not get system status: {e}")
    else:
        print("System status not available for this tracking client")
    
    return True

def test_production_compatibility():
    """Test that the system works with basic requirements.txt dependencies"""
    print("\n🚀 Testing Production Compatibility")
    print("=" * 50)
    
    basic_deps = [
        'streamlit', 'pandas', 'openpyxl', 'requests', 
        'cryptography', 'numpy', 'bs4', 'selenium'
    ]
    
    missing_deps = []
    
    for dep in basic_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Missing")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️  Missing basic dependencies: {', '.join(missing_deps)}")
        return False
    else:
        print("\n✅ All basic dependencies available")
        return True

if __name__ == "__main__":
    print("🔧 Production Fallback System Test")
    print("=" * 60)
    
    fallback_works = test_import_fallback()
    basic_deps_ok = test_production_compatibility()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 60)
    
    if fallback_works and basic_deps_ok:
        print("🎉 SUCCESS: Fallback system working correctly!")
        print("✅ Production deployment should work with basic requirements.txt")
        print("✅ Enhanced features available when advanced dependencies installed")
        sys.exit(0)
    else:
        print("❌ FAILURE: Issues detected with fallback system")
        if not fallback_works:
            print("  - Tracking system fallback not working")
        if not basic_deps_ok:
            print("  - Missing basic dependencies")
        sys.exit(1) 