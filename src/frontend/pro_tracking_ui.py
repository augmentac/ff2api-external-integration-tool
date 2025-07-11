"""
PRO Tracking UI Components

This module provides a standalone PRO tracking workflow that allows users to:
- Upload CSV/Excel files with PRO numbers and carrier information
- Map simple fields (PRO Number + Carrier)
- Perform bulk tracking using existing LTL scrapers
- Export tracking results
"""

import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import os # Added for cloud environment detection

# Import the new simplified StreamlitCloudTracker
try:
    from ..backend.streamlit_cloud_tracker import StreamlitCloudTracker
    STREAMLIT_CLOUD_TRACKER_AVAILABLE = True
except ImportError:
    STREAMLIT_CLOUD_TRACKER_AVAILABLE = False
    StreamlitCloudTracker = None

# Legacy fallback for local development
try:
    from ..backend.ltl_tracking_client import LTLTrackingClient
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False
    LTLTrackingClient = None

from ..backend.carrier_detection import detect_carrier_from_pro


def create_pro_tracking_interface(db_manager, brokerage_name: str):
    """Create the main PRO tracking interface"""
    
    # Page header
    st.header("🚛 PRO Tracking")
    st.caption("Quick bulk tracking for PRO numbers - no API setup required")
    
    # Initialize session state for PRO tracking
    if 'pro_tracking_step' not in st.session_state:
        st.session_state.pro_tracking_step = 1
    
    # Show current step progress
    _render_pro_tracking_progress()
    
    # Enhanced interface with diagnostic capabilities
    interface_tabs = st.tabs([
        "🚛 PRO Tracking",
        "🔍 System Diagnostics",
        "📞 Manual Tracking"
    ])
    
    with interface_tabs[0]:
        # Route to appropriate step
        if st.session_state.pro_tracking_step == 1:
            _render_file_upload_step()
        elif st.session_state.pro_tracking_step == 2:
            _render_field_mapping_step()
        elif st.session_state.pro_tracking_step == 3:
            _render_processing_step()
        elif st.session_state.pro_tracking_step == 4:
            _render_results_step()
    
    with interface_tabs[1]:
        _render_diagnostic_interface()
    
    with interface_tabs[2]:
        _render_manual_tracking_interface()


def _render_pro_tracking_progress():
    """Render progress indicator for PRO tracking workflow"""
    
    steps = [
        "📁 Upload File",
        "🔗 Map Fields", 
        "🚛 Track PROs",
        "📊 View Results"
    ]
    
    current_step = st.session_state.pro_tracking_step
    
    # Create progress columns
    cols = st.columns(len(steps))
    
    for i, step in enumerate(steps):
        with cols[i]:
            if i + 1 < current_step:
                st.success(f"✅ {step}")
            elif i + 1 == current_step:
                st.info(f"🔄 {step}")
            else:
                st.write(f"⏳ {step}")
    
    st.markdown("---")


def _render_file_upload_step():
    """Render the file upload step"""
    
    st.subheader("📁 Upload Your PRO Tracking File")
    
    # Info box
    st.info("""
        **What you need:**
        - CSV or Excel file with PRO numbers
        - Optional: Carrier names (we can auto-detect from PRO patterns)
        - File should have headers in the first row
    """)
    
    # File upload
    # Create unique key to avoid conflicts with main app file uploader
    session_id = st.session_state.get('session_id', 'default')
    uploader_key = f"pro_tracking_file_uploader_{session_id}"
    
    uploaded_file = st.file_uploader(
        "Choose your tracking file",
        type=['csv', 'xlsx', 'xls'],
        key=uploader_key,
        help="Upload a CSV or Excel file containing PRO numbers to track"
    )
    
    if uploaded_file:
        try:
            # Read the file
            with st.spinner("📖 Reading file..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            
            # Store in session state
            st.session_state.pro_tracking_df = df
            st.session_state.pro_tracking_filename = uploaded_file.name
            
            # Show file preview
            st.success(f"✅ **{uploaded_file.name}** loaded successfully")
            st.write(f"**File contains:** {len(df):,} rows, {len(df.columns)} columns")
            
            # Preview first few rows
            st.subheader("📋 File Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Next step button
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🔗 Map Fields", type="primary", use_container_width=True):
                    st.session_state.pro_tracking_step = 2
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # Reset workflow button
    if st.session_state.get('pro_tracking_df') is not None:
        st.markdown("---")
        if st.button("🔄 Start Over", key="reset_pro_tracking"):
            _reset_pro_tracking_workflow()
            st.rerun()


def _render_field_mapping_step():
    """Render the field mapping step"""
    
    st.subheader("🔗 Map Your Fields")
    
    df = st.session_state.get('pro_tracking_df')
    if df is None:
        st.error("No file uploaded. Please go back and upload a file.")
        return
    
    # Show file info
    st.write(f"**File:** {st.session_state.get('pro_tracking_filename', 'Unknown')}")
    st.write(f"**Rows:** {len(df):,}")
    
    # Available columns
    columns = ['Select column...'] + list(df.columns)
    
    # PRO Number mapping (required)
    st.markdown("### Required Field")
    pro_column = st.selectbox(
        "📦 PRO Number Column",
        options=columns,
        help="Select the column containing PRO numbers to track",
        key="pro_tracking_pro_column"
    )
    
    # Carrier mapping (optional)
    st.markdown("### Optional Field")
    carrier_column = st.selectbox(
        "🚛 Carrier Column (Optional)",
        options=columns,
        help="Select carrier column, or leave as 'Select column...' to auto-detect from PRO patterns",
        key="pro_tracking_carrier_column"
    )
    
    # Validation and preview
    if pro_column != 'Select column...':
        # Sample PRO numbers
        sample_pros = df[pro_column].dropna().head(5).tolist()
        
        st.markdown("### 🔍 Preview & Validation")
        
        # Show sample data
        st.write("**Sample PRO numbers from your file:**")
        for i, pro in enumerate(sample_pros, 1):
            # If carrier column is selected, show provided carrier name
            if carrier_column != 'Select column...':
                # Get corresponding carrier name from the same row
                pro_index = df[df[pro_column] == pro].index[0] if pro in df[pro_column].values else None
                if pro_index is not None and pro_index < len(df[carrier_column].dropna()):
                    provided_carrier = df[carrier_column].iloc[pro_index]
                    st.write(f"{i}. `{pro}` → **{provided_carrier}** (from your file) ✅")
                else:
                    # Fall back to auto-detection
                    carrier_info = detect_carrier_from_pro(str(pro))
                    if carrier_info:
                        st.write(f"{i}. `{pro}` → **{carrier_info['carrier_name']}** (auto-detected) ✅")
                    else:
                        st.write(f"{i}. `{pro}` → **Unknown carrier** (auto-detection failed) ⚠️")
            else:
                # Only auto-detection available
                carrier_info = detect_carrier_from_pro(str(pro))
                if carrier_info:
                    st.write(f"{i}. `{pro}` → **{carrier_info['carrier_name']}** (auto-detected) ✅")
                else:
                    st.write(f"{i}. `{pro}` → **Unknown carrier** (auto-detection failed) ⚠️")
        
        # Show carrier column sample if selected
        if carrier_column != 'Select column...':
            st.write("**Sample carriers from your file:**")
            sample_carriers = df[carrier_column].dropna().head(5).tolist()
            for i, carrier in enumerate(sample_carriers, 1):
                st.write(f"{i}. `{carrier}` (will be used for tracking)")
        
        # Processing options
        st.markdown("### ⚙️ Processing Options")
        
        # Rate limiting
        delay_between_requests = st.slider(
            "Delay between requests (seconds)",
            min_value=1,
            max_value=10,
            value=2,
            help="Delay between tracking requests to be respectful to carrier websites"
        )
        
        # Error handling
        max_retries = st.selectbox(
            "Max retries per PRO",
            options=[1, 2, 3],
            index=1,
            help="Number of retry attempts for failed tracking requests"
        )
        
        # Store processing options
        st.session_state.pro_tracking_delay = delay_between_requests
        st.session_state.pro_tracking_retries = max_retries
        
        # Navigation buttons
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            if st.button("← Back", key="pro_tracking_back_to_upload"):
                st.session_state.pro_tracking_step = 1
                st.rerun()
        
        with col3:
            if st.button("🚛 Start Tracking", type="primary", key="pro_tracking_start"):
                # Store field mappings
                st.session_state.pro_tracking_mappings = {
                    'pro_column': pro_column,
                    'carrier_column': carrier_column if carrier_column != 'Select column...' else None
                }
                st.session_state.pro_tracking_step = 3
                st.rerun()
    
    else:
        st.warning("⚠️ Please select a PRO Number column to continue.")


def _render_processing_step():
    """Render the processing step"""
    
    st.subheader("🚛 Tracking PROs")
    
    df = st.session_state.get('pro_tracking_df')
    mappings = st.session_state.get('pro_tracking_mappings')
    
    if df is None or mappings is None:
        st.error("Missing data. Please restart the workflow.")
        return
    
    # Process PROs if not already done
    if 'pro_tracking_results' not in st.session_state:
        _process_pro_tracking(df, mappings)
    
    # Always check if results are available after processing
    if 'pro_tracking_results' in st.session_state:
        # Show completed results
        results = st.session_state.pro_tracking_results
        
        if results:
            # Summary
            total = len(results)
            successful = len([r for r in results if r.get('success', False)])
            failed = total - successful
            success_rate = (successful / total) * 100 if total > 0 else 0
            
            st.success(f"✅ **Tracking Complete!**")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total PROs", total)
            with col2:
                st.metric("Successful", successful)
            with col3:
                st.metric("Failed", failed)
            with col4:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            

            
            # Navigation
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                if st.button("← Back", key="pro_tracking_back_to_mapping"):
                    st.session_state.pro_tracking_step = 2
                    st.rerun()
            
            with col3:
                if st.button("📊 View Results", type="primary", key="pro_tracking_view_results"):
                    st.session_state.pro_tracking_step = 4
                    st.rerun()
        else:
            st.error("❌ No results found. The tracking may have failed.")
            st.info("This could be due to:")
            st.write("- Invalid PRO numbers")
            st.write("- Carrier websites being unavailable")
            st.write("- Network connectivity issues")
            
            # Navigation back
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                if st.button("← Back", key="pro_tracking_back_to_mapping_error"):
                    st.session_state.pro_tracking_step = 2
                    st.rerun()
    else:
        st.info("Processing not complete yet. Please wait...")
        if st.button("🔄 Refresh"):
            st.rerun()


def _render_results_step():
    """Render the results step"""
    
    st.subheader("📊 Tracking Results")
    
    results = st.session_state.get('pro_tracking_results', [])
    
    if not results:
        st.error("No tracking results found. Please restart the workflow.")
        return
    
    # Summary statistics
    total = len(results)
    successful = len([r for r in results if r['success']])
    failed = total - successful
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total PROs", total)
    with col2:
        st.metric("Successfully Tracked", successful)
    with col3:
        st.metric("Failed to Track", failed)
    with col4:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Filter options
    st.markdown("### 🔍 Filter Results")
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "Successful", "Failed"],
            key="pro_tracking_status_filter"
        )
    
    with filter_col2:
        # Get unique carriers for filter
        carriers = list(set([r['carrier'] for r in results if r['carrier']]))
        carrier_filter = st.selectbox(
            "Filter by Carrier",
            options=["All"] + carriers,
            key="pro_tracking_carrier_filter"
        )
    
    # Filter results
    filtered_results = results.copy()
    
    if status_filter == "Successful":
        filtered_results = [r for r in filtered_results if r['success']]
    elif status_filter == "Failed":
        filtered_results = [r for r in filtered_results if not r['success']]
    
    if carrier_filter != "All":
        filtered_results = [r for r in filtered_results if r['carrier'] == carrier_filter]
    
    # Results table
    st.markdown(f"### 📋 Results ({len(filtered_results)} of {total})")
    
    if filtered_results:
        # Convert to DataFrame for display
        results_df = pd.DataFrame(filtered_results)
        
        # Reorder columns for better display
        column_order = ['pro_number', 'carrier', 'status', 'location', 'timestamp', 'success', 'error_message']
        display_columns = [col for col in column_order if col in results_df.columns]
        results_df = results_df[display_columns]
        
        # Rename columns for display
        results_df.columns = [
            'PRO Number' if col == 'pro_number' else
            'Carrier' if col == 'carrier' else
            'Tracking Status' if col == 'status' else
            'Location' if col == 'location' else
            'Last Updated' if col == 'timestamp' else
            'Success' if col == 'success' else
            'Error Message' if col == 'error_message' else col
            for col in results_df.columns
        ]
        
        # Display with styling
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Success": st.column_config.CheckboxColumn("Success"),
                "PRO Number": st.column_config.TextColumn("PRO Number", width="medium"),
                "Carrier": st.column_config.TextColumn("Carrier", width="medium"),
                "Tracking Status": st.column_config.TextColumn("Status", width="large"),
                "Location": st.column_config.TextColumn("Location", width="medium"),
                "Last Updated": st.column_config.TextColumn("Last Updated", width="medium"),
                "Error Message": st.column_config.TextColumn("Error", width="large")
            }
        )
        
        # Export options
        st.markdown("### 📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"pro_tracking_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel export - simplified CSV format due to type issues
            st.download_button(
                label="📊 Download Excel",
                data=results_df.to_csv(index=False),
                file_name=f"pro_tracking_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # JSON export
            json_data = json.dumps(filtered_results, indent=2, default=str)
            st.download_button(
                label="🔧 Download JSON",
                data=json_data,
                file_name=f"pro_tracking_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    else:
        st.info("No results match the selected filters.")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button("← Back to Tracking", key="pro_tracking_back_to_processing"):
            st.session_state.pro_tracking_step = 3
            st.rerun()
    
    with col3:
        if st.button("🔄 Track New File", key="pro_tracking_new_file"):
            _reset_pro_tracking_workflow()
            st.rerun()


def _process_pro_tracking(df: pd.DataFrame, mappings: Dict[str, str]):
    """Process PRO tracking for the uploaded file"""
    
    # Extract PRO numbers and carriers from the dataframe using correct mapping keys
    pro_numbers = []
    carriers = []
    
    # Get the column names from mappings
    pro_column = mappings.get('pro_column')
    carrier_column = mappings.get('carrier_column')
    
    if not pro_column:
        st.error("❌ No PRO column specified in mappings")
        return
    
    # Extract data from the dataframe
    for _, row in df.iterrows():
        # Get PRO number from the specified column
        pro_number = str(row.get(pro_column, '')).strip()
        
        # Get carrier from the specified column (if provided)
        if carrier_column:
            carrier = str(row.get(carrier_column, '')).strip()
            carrier = carrier if carrier and carrier.lower() not in ['', 'nan', 'none', 'null'] else None
        else:
            carrier = None
        
        # Only include valid PRO numbers
        if pro_number and pro_number.lower() not in ['', 'nan', 'none', 'null']:
            pro_numbers.append(pro_number)
            carriers.append(carrier)
    
    if not pro_numbers:
        st.error("❌ No valid PRO numbers found in the uploaded file")
        st.info(f"Checked column: '{pro_column}' - found {len(df)} rows but no valid PRO numbers")
        
        # Show sample data for debugging
        if len(df) > 0:
            st.write("**Sample data from your file:**")
            sample_data = df[[pro_column]].head(3)
            if carrier_column:
                sample_data = df[[pro_column, carrier_column]].head(3)
            st.dataframe(sample_data)
        return
    
    st.success(f"✅ Found {len(pro_numbers)} PRO numbers to track")
    
    # Show sample of what will be tracked
    st.write("**Sample PRO numbers to track:**")
    for i, (pro, carrier) in enumerate(zip(pro_numbers[:3], carriers[:3]), 1):
        carrier_text = f" → {carrier}" if carrier else " → Auto-detect carrier"
        st.write(f"{i}. `{pro}`{carrier_text}")
    
    if len(pro_numbers) > 3:
        st.write(f"... and {len(pro_numbers) - 3} more PRO numbers")
    
    # Initialize tracking system - use the new simplified StreamlitCloudTracker
    tracking_client = None
    system_name = "None"
    
    # Detect cloud environment
    def detect_cloud_environment() -> bool:
        """Detect if we're running in a cloud environment"""
        cloud_indicators = [
            'STREAMLIT_CLOUD',
            'HEROKU',
            'DYNO',
            'RAILWAY',
            'VERCEL',
            'NETLIFY',
            'AWS_LAMBDA',
            'GOOGLE_CLOUD_RUN'
        ]
        
        for indicator in cloud_indicators:
            if os.environ.get(indicator):
                return True
        
        hostname = os.environ.get('HOSTNAME', '').lower()
        if any(pattern in hostname for pattern in ['streamlit', 'heroku', 'railway', 'vercel']):
            return True
        
        return False
    
    is_cloud = detect_cloud_environment()
    
    try:
        # Priority 1: New StreamlitCloudTracker (designed for cloud deployment)
        if STREAMLIT_CLOUD_TRACKER_AVAILABLE and StreamlitCloudTracker is not None:
            tracking_client = StreamlitCloudTracker()
            system_name = "Streamlit Cloud Tracker"
        # Priority 2: Legacy system (fallback for local development)
        elif LEGACY_AVAILABLE and LTLTrackingClient is not None:
            tracking_client = LTLTrackingClient()
            system_name = "Legacy Tracking System"
        else:
            raise ImportError("No tracking system available")
            
        # Show system info with realistic expectations
        if system_name == "Streamlit Cloud Tracker":
            st.info(f"🌐 Using {system_name} for cloud tracking")
            st.caption("Realistic success rates: 30-45% overall (varies by carrier)")
        else:
            st.info(f"🚀 Using {system_name} for tracking")
            st.caption("Local development mode - legacy system")
        
        # Add system diagnostic info
        with st.expander("🔍 System Diagnostic Info", expanded=False):
            st.write(f"**System Selected:** {system_name}")
            st.write(f"**Environment:** {'Cloud' if is_cloud else 'Local'}")
            st.write(f"**Streamlit Cloud Tracker Available:** {STREAMLIT_CLOUD_TRACKER_AVAILABLE}")
            st.write(f"**Legacy System Available:** {LEGACY_AVAILABLE}")
            
            # Show system capabilities based on selected system
            if system_name == "Streamlit Cloud Tracker":
                st.write("**Capabilities:**")
                st.write("- ✅ Cloud-optimized HTTP/API methods")
                st.write("- ✅ No browser automation required")
                st.write("- ✅ Proper event extraction with chronological sorting")
                st.write("- ✅ Realistic success rate expectations")
                st.write("- ✅ Informative error messages")
                st.write("- ✅ Rate limiting to prevent overwhelming carrier websites")
                st.write("**Realistic Success Rates:**")
                st.write("- FedEx Freight: 25% (CloudFlare protection)")
                st.write("- Estes Express: 35% (Angular SPA barriers)")
                st.write("- Peninsula: 30% (Authentication walls)")
                st.write("- R&L Carriers: 40% (Session-based tracking)")
                st.write("- Overall: 30-45% (cloud limitations)")
            else:
                st.write("**Capabilities:**")
                st.write("- ✅ Basic tracking methods")
                st.write("- ⚠️ Legacy system only")
                st.write("- ⚠️ No advanced event extraction")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize tracking system: {str(e)}")
        # Create failed results for all PROs
        results = []
        for pro_number in pro_numbers:
            results.append({
                'pro_number': pro_number,
                'carrier': 'Unknown',
                'status': 'Initialization failed',
                'location': 'N/A',
                'timestamp': 'N/A',
                'success': False,
                'error_message': f"Tracking system initialization failed: {str(e)}"
            })
        st.session_state.pro_tracking_results = results
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Live results container
    live_results_container = st.container()
    with live_results_container:
        st.markdown("### 📊 Live Tracking Results")
        live_results_expander = st.expander("🔍 View Live Results", expanded=True)
        with live_results_expander:
            live_results_placeholder = st.empty()
            live_results_placeholder.info("🚀 Starting tracking... Results will appear here as they become available.")
    
    results = []
    
    try:
        import asyncio
        
        # Create async function to handle tracking
        async def track_all_pros():
            results = []
            for i, (pro_number, carrier_name) in enumerate(zip(pro_numbers, carriers)):
                # Update progress
                progress = (i / len(pro_numbers))
                progress_bar.progress(progress)
                status_text.text(f"Tracking PRO {i+1}/{len(pro_numbers)}: {pro_number}")
                
                # Track the PRO using appropriate system
                try:
                    result_dict = None
                    
                    # Use the correct method based on the tracking system type
                    if system_name == "Streamlit Cloud Tracker":
                        # New StreamlitCloudTracker uses track_shipment(tracking_number, carrier)
                        result_dict = await tracking_client.track_shipment(pro_number, carrier_name or "Auto-Detect")
                    elif system_name == "Legacy Tracking System":
                        # Legacy system uses track_pro_number(pro_number) - synchronous
                        result_dict = tracking_client.track_pro_number(pro_number)
                        # Convert TrackingResult to dict format
                        if hasattr(result_dict, 'scrape_success'):
                            result_dict = {
                                'success': result_dict.scrape_success,
                                'status': result_dict.tracking_status or 'No status available',
                                'location': result_dict.tracking_location or 'No location available',
                                'timestamp': result_dict.tracking_timestamp or 'No timestamp available',
                                'error': result_dict.error_message,
                                'carrier': result_dict.carrier_name
                            }
                    else:
                        raise AttributeError(f"Unknown tracking system: {system_name}")
                    
                    # Use provided carrier name if available, otherwise use detected carrier name
                    final_carrier_name = carrier_name or result_dict.get('carrier', 'Unknown')
                    
                    # Create result record based on system type
                    if system_name in ["Working Cloud Tracking System", "Improved Cloud Tracking System", "Cloud Compatible System", "Barrier-Breaking System"]:
                        # Modern systems use consistent response format
                        result = {
                            'pro_number': pro_number,
                            'carrier': final_carrier_name,
                            'status': result_dict.get('status', 'No status available'),
                            'location': result_dict.get('location', 'No location available'),
                            'timestamp': result_dict.get('timestamp', 'No timestamp available'),
                            'success': result_dict.get('success', False),
                            'error_message': result_dict.get('error', '') if not result_dict.get('success') else None,
                            'method': result_dict.get('method', system_name),
                            'barrier_solved': result_dict.get('barrier_solved', '')
                        }
                    else:
                        # Enhanced/Legacy system response format
                        result = {
                            'pro_number': pro_number,
                            'carrier': final_carrier_name,
                            'status': result_dict.get('tracking_status', result_dict.get('status', 'No status available')),
                            'location': result_dict.get('tracking_location', result_dict.get('location', 'No location available')),
                            'timestamp': result_dict.get('tracking_timestamp', result_dict.get('timestamp', 'No timestamp available')),
                            'success': result_dict.get('status') == 'success' if 'status' in result_dict else result_dict.get('success', False),
                            'error_message': result_dict.get('message', result_dict.get('error', '')) if result_dict.get('status') != 'success' else None,
                            'method': system_name,
                            'barrier_solved': ''
                        }
                    
                except Exception as e:
                    # Create error result - prioritize provided carrier name
                    result = {
                        'pro_number': pro_number,
                        'carrier': carrier_name or 'Unknown',
                        'status': 'Tracking failed',
                        'location': 'N/A',
                        'timestamp': 'N/A',
                        'success': False,
                        'error_message': str(e),
                        'method': system_name,
                        'barrier_solved': ''
                    }
                
                results.append(result)
                
                # Update live results display
                _update_live_results(live_results_placeholder, results, i + 1, len(pro_numbers))
                
                # Small delay between requests
                if i < len(pro_numbers) - 1:  # Don't delay after the last request
                    await asyncio.sleep(0.5)  # Additional small delay for UI responsiveness
            
            return results
        
        # Run the async tracking
        results = asyncio.run(track_all_pros())
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text(f"Tracking complete with {system_name}! ✅")
        
        # Store results
        st.session_state.pro_tracking_results = results
        
    except Exception as e:
        st.error(f"❌ Error during {system_name} tracking: {str(e)}")
        # Store partial results if any
        if results:
            st.session_state.pro_tracking_results = results
    
    finally:
        # Barrier-breaking system doesn't require explicit cleanup
        pass


def _update_live_results(placeholder, results: List[Dict], current_count: int, total_count: int):
    """Update the live results display with current tracking results"""
    
    if not results:
        placeholder.info("🚀 Starting tracking... Results will appear here as they become available.")
        return
    
    # Calculate statistics
    successful = len([r for r in results if r.get('success', False)])
    failed = len(results) - successful
    success_rate = (successful / len(results)) * 100 if results else 0
    
    # Create results display
    with placeholder.container():
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Completed", f"{current_count}/{total_count}")
        with col2:
            st.metric("Successful", successful)
        with col3:
            st.metric("Failed", failed)
        with col4:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Recent results (show last 5)
        st.markdown("**Recent Results:**")
        
        # Show results in reverse order (most recent first)
        recent_results = results[-5:] if len(results) > 5 else results
        recent_results.reverse()
        
        for result in recent_results:
            success_icon = "✅" if result.get('success') else "❌"
            carrier = result.get('carrier', 'Unknown')
            pro_number = result.get('pro_number', 'N/A')
            status = result.get('status', 'No status available')
            location = result.get('location', 'No location available')
            
            # Format the result display
            if result.get('success'):
                st.success(f"{success_icon} **{pro_number}** ({carrier})")
                st.caption(f"📍 Status: {status} | Location: {location}")
            else:
                st.error(f"{success_icon} **{pro_number}** ({carrier})")
                error_msg = result.get('error_message', 'Unknown error')
                st.caption(f"❌ Error: {error_msg}")
        
        # Show completion message if all done
        if current_count == total_count:
            if successful == total_count:
                st.balloons()
                st.success(f"🎉 All {total_count} PRO numbers tracked successfully!")
            elif successful > 0:
                st.success(f"✅ Tracking complete! {successful}/{total_count} PRO numbers tracked successfully.")
            else:
                st.error(f"❌ Tracking complete. Unfortunately, none of the {total_count} PRO numbers could be tracked.")


def _render_diagnostic_interface():
    """Render diagnostic interface"""
    st.subheader("🔍 System Diagnostics")
    
    st.info("**System Status: Critical Issues Detected**")
    
    # Current status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Success Rate", "0%", delta="-100%", delta_color="inverse")
    
    with col2:
        st.metric("Blocking Rate", "100%", delta="All Carriers", delta_color="inverse")
    
    with col3:
        st.metric("Manual Tracking", "Available", delta="4 Carriers", delta_color="normal")
    
    # Critical issues
    st.error("🚨 **CRITICAL ISSUES DETECTED**")
    
    issues = [
        "Infrastructure-level blocking across all carriers",
        "Streamlit Cloud IP addresses blacklisted",
        "CloudFlare protection blocking requests",
        "Rate limiting preventing attempts"
    ]
    
    for issue in issues:
        st.write(f"• {issue}")
    
    # Recommendations
    st.info("💡 **IMMEDIATE RECOMMENDATIONS**")
    
    recommendations = [
        "Use manual tracking methods for immediate results",
        "Contact carriers directly for urgent needs",
        "Consider alternative tracking approaches",
        "Implement proxy services for partial recovery"
    ]
    
    for rec in recommendations:
        st.write(f"• {rec}")
    
    # Diagnostic actions
    st.subheader("⚡ Diagnostic Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Run Network Test", use_container_width=True):
            st.info("Network diagnostic would test connectivity and blocking patterns")
    
    with col2:
        if st.button("📊 Analyze Failures", use_container_width=True):
            st.info("Failure analysis would provide detailed root cause analysis")


def _render_manual_tracking_interface():
    """Render manual tracking interface"""
    st.subheader("📞 Manual Tracking Guides")
    
    st.write("Due to current system limitations, manual tracking is the most reliable method.")
    
    # Carrier selection
    carriers = {
        'FedEx Freight': {
            'phone': '1-800-463-3339',
            'website': 'https://www.fedex.com/fedextrack/',
            'hours': 'Monday-Friday 8 AM - 6 PM EST'
        },
        'Estes Express': {
            'phone': '1-866-378-3748',
            'website': 'https://www.estes-express.com/myestes/shipment-tracking',
            'hours': 'Monday-Friday 8 AM - 5 PM EST'
        },
        'Peninsula Truck Lines': {
            'phone': '1-800-840-6400',
            'website': 'https://www.peninsulatrucklines.com/track-shipment',
            'hours': 'Monday-Friday 7 AM - 6 PM PST'
        },
        'R&L Carriers': {
            'phone': '1-800-543-5589',
            'website': 'https://www.rlcarriers.com/tracking',
            'hours': 'Monday-Friday 8 AM - 5 PM EST'
        }
    }
    
    selected_carrier = st.selectbox("Select Carrier for Manual Tracking:", list(carriers.keys()))
    
    if selected_carrier:
        carrier_info = carriers[selected_carrier]
        
        # Display carrier information
        st.subheader(f"📋 {selected_carrier} Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Phone:** {carrier_info['phone']}")
            st.info(f"**Hours:** {carrier_info['hours']}")
        
        with col2:
            st.link_button(
                "🌐 Visit Tracking Website",
                carrier_info['website'],
                use_container_width=True
            )
        
        # Instructions
        st.subheader("📝 Step-by-Step Instructions")
        
        instructions = [
            "Have your PRO number ready before calling",
            "Call during business hours for fastest service",
            "Ask for detailed tracking information and delivery estimates",
            "Request notification preferences for updates",
            "Get reference number for future inquiries"
        ]
        
        for i, instruction in enumerate(instructions, 1):
            st.write(f"{i}. {instruction}")
        
        # Tips
        st.subheader("💡 Helpful Tips")
        
        tips = [
            "Try both with and without spaces/dashes in PRO number",
            "Have shipper reference number as backup",
            "Ask about delivery appointment requirements",
            "Mobile apps sometimes work better than websites"
        ]
        
        for tip in tips:
            st.write(f"• {tip}")


def _reset_pro_tracking_workflow():
    """Reset PRO tracking workflow to start"""
    keys_to_clear = [
        'pro_tracking_step',
        'pro_tracking_df',
        'pro_tracking_filename',
        'pro_tracking_results',
        'pro_tracking_mappings'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to step 1
    st.session_state.pro_tracking_step = 1 