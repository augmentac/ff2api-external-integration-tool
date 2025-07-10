#!/usr/bin/env python3
"""
Production Barrier-Breaking System Test
Quick test to verify the barrier-breaking system is working in production
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.backend.barrier_breaking_tracking_system import BarrierBreakingTrackingSystem

async def test_production_barrier_breaking():
    """Test the barrier-breaking system with real PRO numbers"""
    
    print("🚀 Testing Production Barrier-Breaking System")
    print("=" * 50)
    
    # Test PRO numbers from your results
    test_pros = [
        "0628143046",  # Estes Express
        "1751027634",  # FedEx Freight Economy
        "4012381741",  # FedEx Freight Priority
        "2121121287",  # Estes Express
    ]
    
    system = BarrierBreakingTrackingSystem()
    
    print(f"📦 Testing {len(test_pros)} PRO numbers...")
    print()
    
    successful_tracks = 0
    barriers_solved = set()
    
    for i, pro_number in enumerate(test_pros, 1):
        print(f"🔍 Test {i}/{len(test_pros)}: {pro_number}")
        
        try:
            result = await system.track_single_shipment(pro_number)
            
            if result.get('success'):
                successful_tracks += 1
                status = "✅ SUCCESS"
                method = result.get('method', 'Unknown')
                barrier = result.get('barrier_solved', 'None')
                if barrier:
                    barriers_solved.add(barrier)
                print(f"    {status} - {method}")
                print(f"    Status: {result.get('status', 'Unknown')}")
                if barrier:
                    print(f"    Barrier Solved: {barrier}")
            else:
                status = "❌ FAILED"
                error = result.get('error', 'Unknown error')
                print(f"    {status} - {error}")
                
        except Exception as e:
            print(f"    ❌ EXCEPTION - {str(e)}")
            
        print()
    
    # Summary
    success_rate = (successful_tracks / len(test_pros)) * 100
    print("📊 PRODUCTION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Successful Tracks: {successful_tracks}/{len(test_pros)} ({success_rate:.1f}%)")
    print(f"💪 Barriers Solved: {', '.join(barriers_solved) if barriers_solved else 'None'}")
    
    if success_rate > 0:
        print("🎉 BARRIER-BREAKING SYSTEM IS WORKING IN PRODUCTION!")
    else:
        print("⚠️  BARRIER-BREAKING SYSTEM NEEDS ATTENTION")
    
    return success_rate > 0

if __name__ == "__main__":
    success = asyncio.run(test_production_barrier_breaking())
    sys.exit(0 if success else 1) 