#!/usr/bin/env python3
"""
LTL Tracking Streamlit App
Main application entry point for Streamlit Cloud deployment
"""

import streamlit as st
import asyncio
import logging
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the enhanced streamlit cloud tracker (only change needed)
TRACKING_SYSTEM_AVAILABLE = False
StreamlitCloudTracker = None

try:
    from src.backend.streamlit_cloud_tracker import EnhancedStreamlitCloudTracker as StreamlitCloudTracker
    TRACKING_SYSTEM_AVAILABLE = True
    logger.info("✅ Enhanced Streamlit Cloud Tracker loaded successfully")
except ImportError as e:
    TRACKING_SYSTEM_AVAILABLE = False
    logger.error(f"❌ Failed to load tracking system: {e}")
    StreamlitCloudTracker = None

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="LTL Tracking System",
        page_icon="🚚",
        layout="wide"
    )
    
    st.title("🚚 LTL Tracking System")
    st.markdown("**Cloud-Native Tracking with Enhanced Success Rates**")
    
    # System status
    if TRACKING_SYSTEM_AVAILABLE:
        st.success("✅ Tracking system loaded successfully")
        
        # Initialize tracker
        try:
            if StreamlitCloudTracker is None:
                raise ImportError("StreamlitCloudTracker not available")
            tracker = StreamlitCloudTracker()
            
            with st.expander("🔧 System Status"):
                st.write("**System:** Enhanced Streamlit Cloud Tracker")
                st.write("**Environment:** Cloud-optimized with enhanced methods")
                st.write("**Expected Success Rates:**")
                st.write("- FedEx Freight: 15-25% (Enhanced request patterns)")
                st.write("- Estes Express: 20-30% (Advanced session management)")
                st.write("- Peninsula: 15-25% (Improved content extraction)")
                st.write("- R&L Carriers: 20-30% (Multi-vector tracking)")
                st.write("- **Overall: 15-30% (Enhanced system)**")
        
        except Exception as e:
            st.error(f"❌ Failed to initialize tracker: {e}")
    else:
        st.error("❌ Tracking system not available")
        st.info("Please check the system logs for more details.")
    
    # Tracking interface
    st.markdown("---")
    st.subheader("📦 Track Your Shipment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tracking_number = st.text_input(
            "Enter Tracking Number:",
            placeholder="e.g., 1234567890",
            help="Enter your PRO number or tracking number"
        )
    
    with col2:
        carrier = st.selectbox(
            "Select Carrier:",
            ["Auto-Detect", "Estes Express", "FedEx Freight", "Peninsula Truck Lines", "R&L Carriers"],
            help="Select your carrier or choose Auto-Detect"
        )
    
    # Track button
    if st.button("🔍 Track Shipment", type="primary", disabled=not TRACKING_SYSTEM_AVAILABLE):
        if not tracking_number:
            st.error("Please enter a tracking number")
            return
        
        if not TRACKING_SYSTEM_AVAILABLE:
            st.error("Tracking system not available")
            return
        
        # Show progress
        with st.spinner("🔍 Tracking your shipment..."):
            try:
                # Run async tracking
                result = asyncio.run(tracker.track_shipment(tracking_number, carrier))
                
                # Display results
                if result.get('success'):
                    st.success("✅ Tracking data found!")
                    
                    # Create result display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("📋 Status", result.get('status', 'Unknown'))
                        st.metric("🚚 Carrier", result.get('carrier', 'Unknown'))
                        st.metric("📍 Location", result.get('location', 'Unknown'))
                    
                    with col2:
                        st.metric("🔢 Tracking Number", tracking_number)
                        if 'method' in result:
                            st.metric("⚙️ Method", result['method'])
                        if 'timestamp' in result:
                            import datetime
                            timestamp = datetime.datetime.fromtimestamp(result['timestamp'])
                            st.metric("⏰ Retrieved", timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # Show events if available
                    if result.get('events'):
                        st.subheader("📋 Tracking Events")
                        for event in result['events']:
                            st.write(f"• {event}")
                    
                    # Show raw result in expander
                    with st.expander("🔍 Raw Tracking Data"):
                        st.json(result)
                
                else:
                    st.error(f"❌ Tracking failed: {result.get('error_message', 'Unknown error')}")
                    
                    # Show alternative methods
                    if 'alternatives' in result:
                        st.info("**Alternative Tracking Methods:**")
                        alternatives = result['alternatives']
                        if 'website' in alternatives:
                            st.write(f"🌐 Website: {alternatives['website']}")
                        if 'phone' in alternatives:
                            st.write(f"📞 Phone: {alternatives['phone']}")
                        if 'next_steps' in alternatives:
                            st.write("**Next Steps:**")
                            for step in alternatives['next_steps']:
                                st.write(f"  {step}")
                    
                    # Show raw result for debugging
                    with st.expander("🔍 Debug Information"):
                        st.json(result)
            
            except Exception as e:
                st.error(f"❌ Tracking error: {str(e)}")
                logger.error(f"Tracking error: {e}")
    
    # Instructions
    st.markdown("---")
    st.subheader("📝 Instructions")
    st.markdown("""
    1. **Enter your tracking number** (PRO number) in the input field
    2. **Select your carrier** or choose "Auto-Detect" to try all carriers
    3. **Click "Track Shipment"** to retrieve tracking information
    4. **View results** including status, location, and tracking events
    
    **Supported Carriers:**
    - 🚛 Estes Express (20-30% success rate)
    - 📦 FedEx Freight (15-25% success rate)
    - 🏢 Peninsula Truck Lines (15-25% success rate)
    - 🚚 R&L Carriers (20-30% success rate)
    
    **Note:** Success rates reflect enhanced cloud deployment capabilities.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("**🌐 Enhanced LTL Tracking System** | Cloud-Native with Improved Success Rates")

if __name__ == "__main__":
    main()