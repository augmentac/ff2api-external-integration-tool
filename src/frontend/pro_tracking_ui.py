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

from ..backend.ltl_tracking_client import LTLTrackingClient
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
    
    # Route to appropriate step
    if st.session_state.pro_tracking_step == 1:
        _render_file_upload_step()
    elif st.session_state.pro_tracking_step == 2:
        _render_field_mapping_step()
    elif st.session_state.pro_tracking_step == 3:
        _render_processing_step()
    elif st.session_state.pro_tracking_step == 4:
        _render_results_step()


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
    uploaded_file = st.file_uploader(
        "Choose your tracking file",
        type=['csv', 'xlsx', 'xls'],
        key="pro_tracking_file_uploader",
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
            carrier_info = detect_carrier_from_pro(str(pro))
            if carrier_info:
                st.write(f"{i}. `{pro}` → **{carrier_info['carrier_name']}** ✅")
            else:
                st.write(f"{i}. `{pro}` → **Unknown carrier** ⚠️")
        
        # Show carrier column sample if selected
        if carrier_column != 'Select column...':
            st.write("**Sample carriers from your file:**")
            sample_carriers = df[carrier_column].dropna().head(5).tolist()
            for i, carrier in enumerate(sample_carriers, 1):
                st.write(f"{i}. `{carrier}`")
        
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
    else:
        # Show completed results
        results = st.session_state.pro_tracking_results
        
        # Summary
        total = len(results)
        successful = len([r for r in results if r['success']])
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
    
    pro_column = mappings['pro_column']
    carrier_column = mappings.get('carrier_column')
    
    # Get processing options
    delay = st.session_state.get('pro_tracking_delay', 2)
    max_retries = st.session_state.get('pro_tracking_retries', 2)
    
    # Extract PRO numbers and carriers
    pro_numbers = df[pro_column].dropna().astype(str).tolist()
    carriers = df[carrier_column].dropna().astype(str).tolist() if carrier_column else []
    
    # Ensure carriers list matches PRO numbers length
    if carrier_column and len(carriers) < len(pro_numbers):
        # Pad with None values
        carriers.extend([None] * (len(pro_numbers) - len(carriers)))
    elif not carrier_column:
        carriers = [None] * len(pro_numbers)
    
    # Initialize tracking client
    tracking_client = LTLTrackingClient(
        delay_between_requests=delay,
        max_retries=max_retries
    )
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    try:
        for i, (pro_number, carrier_name) in enumerate(zip(pro_numbers, carriers)):
            # Update progress
            progress = (i / len(pro_numbers))
            progress_bar.progress(progress)
            status_text.text(f"Tracking PRO {i+1}/{len(pro_numbers)}: {pro_number}")
            
            # Track the PRO
            try:
                tracking_result = tracking_client.track_pro_number(pro_number)
                
                # Create result record
                result = {
                    'pro_number': pro_number,
                    'carrier': tracking_result.carrier_name,
                    'status': tracking_result.tracking_status or 'No status available',
                    'location': tracking_result.tracking_location or 'No location available',
                    'timestamp': tracking_result.tracking_timestamp or 'No timestamp available',
                    'success': tracking_result.scrape_success,
                    'error_message': tracking_result.error_message if not tracking_result.scrape_success else None
                }
                
            except Exception as e:
                # Create error result
                result = {
                    'pro_number': pro_number,
                    'carrier': carrier_name or 'Unknown',
                    'status': 'Tracking failed',
                    'location': 'N/A',
                    'timestamp': 'N/A',
                    'success': False,
                    'error_message': str(e)
                }
            
            results.append(result)
            
            # Small delay between requests
            if i < len(pro_numbers) - 1:  # Don't delay after the last request
                time.sleep(0.5)  # Additional small delay for UI responsiveness
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text("Tracking complete!")
        
        # Store results
        st.session_state.pro_tracking_results = results
        
    except Exception as e:
        st.error(f"Error during tracking: {str(e)}")
    
    finally:
        tracking_client.close()





def _reset_pro_tracking_workflow():
    """Reset the PRO tracking workflow to start over"""
    
    # Clear all PRO tracking session state
    keys_to_clear = [
        'pro_tracking_step',
        'pro_tracking_df',
        'pro_tracking_filename',
        'pro_tracking_mappings',
        'pro_tracking_results',
        'pro_tracking_delay',
        'pro_tracking_retries'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to step 1
    st.session_state.pro_tracking_step = 1 