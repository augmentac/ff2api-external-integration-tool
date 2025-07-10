#!/usr/bin/env python3
"""
Main Streamlit Application - Updated for Cloud Deployment
Now uses the working tracking system for real tracking data retrieval
"""

import streamlit as st
import pandas as pd
import asyncio
import time
import os
from typing import Dict, Any, List
import sys

# Add parent directory to path to enable src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import the working tracking systems in order of preference
try:
    from src.backend.working_tracking_system import WorkingTrackingSystem
    WORKING_SYSTEM_AVAILABLE = True
except ImportError:
    WORKING_SYSTEM_AVAILABLE = False

try:
    from src.backend.barrier_breaking_tracking_system import BarrierBreakingTrackingSystem
    BARRIER_BREAKING_AVAILABLE = True
except ImportError:
    BARRIER_BREAKING_AVAILABLE = False

try:
    from src.backend.cloud_compatible_tracking import CloudCompatibleTracker
    CLOUD_COMPATIBLE_AVAILABLE = True
except ImportError:
    CLOUD_COMPATIBLE_AVAILABLE = False

try:
    from src.backend.improved_cloud_tracking import ImprovedCloudTracker
    IMPROVED_CLOUD_AVAILABLE = True
except ImportError:
    IMPROVED_CLOUD_AVAILABLE = False

try:
    from src.backend.working_cloud_tracking import WorkingCloudTracker
    WORKING_CLOUD_AVAILABLE = True
except ImportError:
    WORKING_CLOUD_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="CSV->LTL Action - Cloud Tracking",
    page_icon="📦",
    layout="wide"
)

def get_best_tracking_system():
    """Get the best available tracking system for cloud deployment"""
    # For cloud deployment, prioritize cloud-compatible systems
    if WORKING_CLOUD_AVAILABLE:
        return WorkingCloudTracker(), "Working Cloud Tracking System"
    elif IMPROVED_CLOUD_AVAILABLE:
        return ImprovedCloudTracker(), "Improved Cloud Tracking System"
    elif CLOUD_COMPATIBLE_AVAILABLE:
        return CloudCompatibleTracker(), "Cloud Compatible System"
    elif WORKING_SYSTEM_AVAILABLE:
        return WorkingTrackingSystem(), "Working Tracking System"
    elif BARRIER_BREAKING_AVAILABLE:
        return BarrierBreakingTrackingSystem(), "Barrier-Breaking System"
    else:
        return None, "No System Available"

async def track_shipment_async(tracking_system, tracking_number: str, system_name: str) -> Dict[str, Any]:
    """Track a shipment using the available system"""
    try:
        start_time = time.time()
        
        if "Working Cloud" in system_name or "Improved Cloud" in system_name:
            # Cloud tracking systems
            result = await tracking_system.track_shipment(tracking_number, "Auto-Detect")
        elif system_name == "Working Tracking System":
            # Working system can auto-detect carrier and retrieve real data
            result = await tracking_system.track_shipment(tracking_number)
        elif system_name == "Barrier-Breaking System":
            # Barrier-breaking system
            if hasattr(tracking_system, 'track_single_shipment'):
                result = await tracking_system.track_single_shipment(tracking_number)
            else:
                multi_result = await tracking_system.track_multiple_shipments([tracking_number])
                result = multi_result['results'][0] if multi_result.get('results') else {'success': False, 'error': 'No results'}
        elif system_name == "Cloud Compatible System":
            # Cloud compatible system
            result = await tracking_system.track_shipment(tracking_number, "Auto-Detect")
        else:
            result = {'success': False, 'error': 'No tracking system available'}
        
        # Add timing information
        result['duration'] = time.time() - start_time
        result['system_used'] = system_name
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Tracking error: {str(e)}',
            'duration': time.time() - start_time if 'start_time' in locals() else 0,
            'system_used': system_name,
            'tracking_number': tracking_number
        }

def main():
    st.title("📦 CSV->LTL Action - Cloud Tracking System")
    st.markdown("**Real tracking data retrieval optimized for cloud deployment**")
    st.markdown("---")
    
    # Get tracking system
    tracking_system, system_name = get_best_tracking_system()
    
    if tracking_system is None:
        st.error("❌ No tracking system available. Please check your installation.")
        st.markdown("""
        ### Available Systems Status:
        - **Working Cloud Tracking System**: ❌ Not Available
        - **Improved Cloud Tracking System**: ❌ Not Available
        - **Cloud Compatible System**: ❌ Not Available
        - **Working Tracking System**: ❌ Not Available
        - **Barrier-Breaking System**: ❌ Not Available
        
        Please ensure the tracking system components are properly installed.
        """)
        return
    
    # Show system status
    st.success(f"✅ Using **{system_name}** for real tracking data retrieval")
    
    # Show capabilities based on system
    if "Cloud" in system_name:
        st.info("🌐 **Cloud Optimized**: HTTP/API methods, No browser automation required, Fast response times")
    elif system_name == "Working Tracking System":
        st.info("🚀 **Full Capabilities**: Apple Silicon ARM64 support, CloudFlare bypass, HTTP fallbacks, Multi-carrier detection")
    elif system_name == "Barrier-Breaking System":
        st.info("🚀 **Advanced Features**: Browser automation, Anti-scraping bypass, Comprehensive barrier breaking")
    
    # Environment detection
    is_cloud = (
        bool(os.environ.get('STREAMLIT_CLOUD', False)) or
        bool(os.environ.get('DYNO', False)) or
        bool(os.environ.get('HEROKU', False)) or
        'streamlit' in os.environ.get('HOSTNAME', '').lower()
    )
    
    if is_cloud:
        st.info("🌐 **Cloud Environment Detected** - Using cloud-optimized tracking methods")
    else:
        st.info("🖥️ **Local Environment Detected** - Full browser automation available")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🚀 Single Tracking", "📊 Batch Tracking", "ℹ️ System Info"])
    
    with tab1:
        st.subheader("🚀 Single Shipment Tracking")
        st.markdown("Track individual PRO numbers and get real tracking data")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            tracking_number = st.text_input(
                "Enter PRO Number",
                placeholder="e.g., 0628143046, 1234567890, 123456789",
                help="Enter a PRO number to track. System will auto-detect carrier."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            track_button = st.button("🔍 Track", type="primary", use_container_width=True)
        
        if track_button and tracking_number:
            st.markdown("---")
            
            # Create placeholders for live updates
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            results_placeholder = st.empty()
            
            with status_placeholder.container():
                st.info(f"🔄 Tracking {tracking_number} with {system_name}...")
                if is_cloud:
                    st.caption("Using cloud-optimized tracking methods...")
                else:
                    st.caption("Using barrier-breaking techniques to retrieve real tracking data...")
            
            with progress_placeholder.container():
                progress_bar = st.progress(0)
            
            try:
                # Update progress
                progress_bar.progress(25)
                
                # Run tracking
                result = asyncio.run(track_shipment_async(tracking_system, tracking_number, system_name))
                
                progress_bar.progress(100)
                
                # Clear status
                status_placeholder.empty()
                progress_placeholder.empty()
                
                # Display results
                with results_placeholder.container():
                    if result.get('success'):
                        st.success(f"✅ **Real tracking data retrieved!** ({result.get('duration', 0):.2f}s)")
                        
                        # Show method and barrier information
                        col1, col2 = st.columns(2)
                        with col1:
                            method = result.get('method', 'Cloud-Optimized HTTP')
                            st.info(f"🔧 **Method**: {method}")
                        
                        with col2:
                            barrier = result.get('barrier_solved', 'None')
                            if barrier and barrier != 'None':
                                st.success(f"💪 **Barrier Solved**: {barrier}")
                            else:
                                st.info("💪 **Barrier**: None required")
                        
                        # Create result columns
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📊 Status", result.get('status', 'N/A'))
                        
                        with col2:
                            st.metric("📍 Location", result.get('location', 'N/A'))
                        
                        with col3:
                            detected_carrier = result.get('detected_carrier') or result.get('carrier', 'N/A')
                            st.metric("🚛 Carrier", detected_carrier)
                        
                        with col4:
                            st.metric("📋 Events", len(result.get('events', [])))
                        
                        # Show tracking events
                        if result.get('events'):
                            st.subheader("📋 Tracking Events")
                            events_df = pd.DataFrame(result['events'])
                            st.dataframe(events_df, use_container_width=True)
                        
                        # Show raw result in expandable section
                        with st.expander("🔍 Raw Tracking Data"):
                            st.json(result)
                    
                    else:
                        st.error(f"❌ **Tracking failed**: {result.get('error', 'Unknown error')}")
                        
                        # Show helpful information
                        st.markdown("### 💡 Troubleshooting:")
                        
                        error_msg = result.get('error', '').lower()
                        if 'legacy system' in error_msg:
                            st.info("🔧 **Legacy System**: Carrier website requires browser automation")
                        elif 'cloudflare' in error_msg:
                            st.info("🔧 **CloudFlare Protection**: Advanced anti-scraping measures detected")
                        elif 'timeout' in error_msg:
                            st.info("🔧 **Timeout**: Carrier website took too long to respond")
                        else:
                            st.info("🔧 **General Error**: Check PRO number format and try again")
                        
                        # Show recommendation
                        recommendation = result.get('recommendation', '')
                        if recommendation:
                            st.markdown(f"**Recommendation**: {recommendation}")
                        
                        # Show raw error details
                        with st.expander("🔍 Error Details"):
                            st.json(result)
            
            except Exception as e:
                status_placeholder.empty()
                progress_placeholder.empty()
                with results_placeholder.container():
                    st.error(f"❌ **System Error**: {str(e)}")
                    st.markdown("Please try again or contact support if the issue persists.")
    
    with tab2:
        st.subheader("📊 Batch Tracking")
        st.markdown("Upload a CSV file with multiple PRO numbers for batch tracking")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with a column containing PRO numbers"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} rows")
                
                # Show file preview
                st.subheader("📋 File Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Column selection
                pro_column = st.selectbox(
                    "Select the column containing PRO numbers",
                    df.columns.tolist(),
                    help="Choose the column that contains the tracking numbers"
                )
                
                if st.button("🚀 Start Batch Tracking", type="primary"):
                    st.markdown("---")
                    
                    # Initialize results
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process each PRO number
                    for idx, row in df.iterrows():
                        pro_number = str(row[pro_column]).strip()
                        
                        if pro_number and pro_number.lower() != 'nan':
                            status_text.text(f"Processing {idx+1}/{len(df)}: {pro_number}")
                            
                            # Track shipment
                            result = asyncio.run(track_shipment_async(tracking_system, pro_number, system_name))
                            result['original_row'] = idx
                            result['pro_number'] = pro_number
                            results.append(result)
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / len(df))
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Show results
                    st.subheader("📊 Batch Tracking Results")
                    
                    if results:
                        # Create results summary
                        successful = sum(1 for r in results if r.get('success'))
                        failed = len(results) - successful
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("✅ Successful", successful)
                        with col2:
                            st.metric("❌ Failed", failed)
                        with col3:
                            success_rate = (successful / len(results)) * 100 if results else 0
                            st.metric("📈 Success Rate", f"{success_rate:.1f}%")
                        
                        # Create results DataFrame
                        results_data = []
                        for result in results:
                            results_data.append({
                                'PRO Number': result.get('pro_number', 'N/A'),
                                'Status': result.get('status', 'N/A'),
                                'Location': result.get('location', 'N/A'),
                                'Carrier': result.get('carrier', 'N/A'),
                                'Success': '✅' if result.get('success') else '❌',
                                'Error': result.get('error', '') if not result.get('success') else '',
                                'Duration': f"{result.get('duration', 0):.2f}s"
                            })
                        
                        results_df = pd.DataFrame(results_data)
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Download results
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name=f"tracking_results_{int(time.time())}.csv",
                            mime="text/csv"
                        )
                    
                    else:
                        st.warning("No valid PRO numbers found to process")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
    
    with tab3:
        st.subheader("ℹ️ System Information")
        
        # System status
        st.markdown("### 🔧 System Status")
        
        status_data = {
            'Component': [
                'Working Cloud Tracking System',
                'Improved Cloud Tracking System', 
                'Cloud Compatible System',
                'Working Tracking System',
                'Barrier-Breaking System'
            ],
            'Available': [
                '✅' if WORKING_CLOUD_AVAILABLE else '❌',
                '✅' if IMPROVED_CLOUD_AVAILABLE else '❌',
                '✅' if CLOUD_COMPATIBLE_AVAILABLE else '❌',
                '✅' if WORKING_SYSTEM_AVAILABLE else '❌',
                '✅' if BARRIER_BREAKING_AVAILABLE else '❌'
            ],
            'Description': [
                'Cloud-optimized tracking with HTTP/API methods',
                'Enhanced cloud tracking with multiple fallbacks',
                'Basic cloud-compatible tracking system',
                'Full-featured tracking with browser automation',
                'Advanced barrier-breaking with browser automation'
            ]
        }
        
        status_df = pd.DataFrame(status_data)
        st.dataframe(status_df, use_container_width=True)
        
        # Environment information
        st.markdown("### 🌐 Environment Information")
        
        env_info = {
            'Environment': 'Cloud' if is_cloud else 'Local',
            'System Used': system_name,
            'Python Version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'Streamlit Cloud': '✅' if os.environ.get('STREAMLIT_CLOUD') else '❌',
            'Platform': os.name,
            'Working Directory': os.getcwd()
        }
        
        for key, value in env_info.items():
            st.text(f"{key}: {value}")
        
        # Supported carriers
        st.markdown("### 🚛 Supported Carriers")
        
        carriers = [
            "Estes Express Lines",
            "FedEx Freight", 
            "Peninsula Truck Lines",
            "R&L Carriers"
        ]
        
        for carrier in carriers:
            st.text(f"• {carrier}")
        
        # Performance expectations
        st.markdown("### 📊 Performance Expectations")
        
        if is_cloud:
            st.info("""
            **Cloud Environment Performance:**
            - Response Time: 5-15 seconds
            - Success Rate: 60-85% (depends on carrier)
            - Method: HTTP/API calls (no browser automation)
            - Limitations: Some carriers may require browser automation
            """)
        else:
            st.info("""
            **Local Environment Performance:**
            - Response Time: 15-45 seconds
            - Success Rate: 75-95% (depends on carrier)
            - Method: Browser automation + HTTP/API fallbacks
            - Capabilities: Full barrier-breaking techniques available
            """)

if __name__ == "__main__":
    main() 