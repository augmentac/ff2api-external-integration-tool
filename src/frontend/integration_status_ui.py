"""
Integration Status Dashboard UI Components

This module provides the UI components for displaying integration status,
health metrics, and recent activity instead of the self-service integration management.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from ..backend.integration_status import IntegrationStatusService, IntegrationStatus, SystemOverview


def create_integration_status_dashboard(db_manager, brokerage_name: str):
    """Create the main integration status dashboard"""
    
    # Initialize status service
    status_service = IntegrationStatusService(db_manager)
    
    # Page header
    st.header("📊 Integration Status Dashboard")
    st.caption("Monitor the health and performance of all your integrations")
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh", key="refresh_all_statuses"):
            status_service.refresh_all_statuses(brokerage_name)
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
        if auto_refresh:
            # Auto-refresh every 30 seconds
            st.rerun()
    
    # Get system overview
    system_overview = status_service.get_system_overview(brokerage_name)
    
    # System overview cards
    _render_system_overview_cards(system_overview)
    
    # Get all integration statuses
    all_statuses = status_service.get_all_integration_statuses(brokerage_name)
    
    # Create tabs for different integration types
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔗 API Integrations", 
        "🕷️ Web Scrapers", 
        "📊 Performance Metrics",
        "📈 Recent Activity"
    ])
    
    with tab1:
        api_statuses = [s for s in all_statuses if s.type not in ['web_scraper', 'web_scraper_legacy', 'database']]
        _render_api_integrations_status(api_statuses)
    
    with tab2:
        web_scraper_statuses = [s for s in all_statuses if s.type in ['web_scraper', 'web_scraper_legacy']]
        _render_web_scrapers_status(web_scraper_statuses)
    
    with tab3:
        _render_performance_metrics(all_statuses, system_overview)
    
    with tab4:
        recent_activity = status_service.get_recent_activity(brokerage_name)
        _render_recent_activity(recent_activity)
    
    # Database status at bottom
    db_status = [s for s in all_statuses if s.type == 'database']
    if db_status:
        st.markdown("---")
        _render_database_status(db_status[0])
    
    # Cleanup
    status_service.close()


def _render_system_overview_cards(overview: SystemOverview):
    """Render the system overview cards"""
    
    # Status color mapping
    status_colors = {
        'healthy': '🟢',
        'degraded': '🟡',
        'failed': '🔴',
        'unknown': '⚫'
    }
    
    # Main status card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, 
                {'#10b981' if overview.overall_status == 'healthy' else 
                 '#f59e0b' if overview.overall_status == 'degraded' else
                 '#ef4444' if overview.overall_status == 'failed' else '#6b7280'} 0%, 
                {'#065f46' if overview.overall_status == 'healthy' else 
                 '#92400e' if overview.overall_status == 'degraded' else
                 '#991b1b' if overview.overall_status == 'failed' else '#374151'} 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="margin: 0 0 0.5rem 0; display: flex; align-items: center; gap: 0.5rem;">
                {status_colors.get(overview.overall_status, '⚫')} System Status: {overview.overall_status.title()}
            </h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                {overview.total_integrations} integrations monitored • 
                {overview.total_requests_today} requests today • 
                Last updated: {overview.last_updated.strftime('%H:%M:%S')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🟢 Healthy",
            value=overview.healthy_integrations,
            delta=f"{overview.healthy_integrations}/{overview.total_integrations}"
        )
    
    with col2:
        st.metric(
            label="🟡 Degraded",
            value=overview.degraded_integrations,
            delta=f"{overview.degraded_integrations}/{overview.total_integrations}"
        )
    
    with col3:
        st.metric(
            label="🔴 Failed",
            value=overview.failed_integrations,
            delta=f"{overview.failed_integrations}/{overview.total_integrations}"
        )
    
    with col4:
        success_rate = (overview.total_successes_today / overview.total_requests_today * 100) if overview.total_requests_today > 0 else 0
        st.metric(
            label="📈 Success Rate",
            value=f"{success_rate:.1f}%",
            delta=f"{overview.total_successes_today}/{overview.total_requests_today}"
        )


def _render_api_integrations_status(api_statuses: List[IntegrationStatus]):
    """Render API integrations status section"""
    
    if not api_statuses:
        st.info("🔗 No API integrations configured yet.")
        st.markdown("""
            **What are API Integrations?**
            - Direct connections to external freight APIs
            - Real-time data exchange with carriers
            - Automated pricing and booking systems
            - Electronic data interchange (EDI) connections
        """)
        return
    
    st.subheader("🔗 API Integrations Status")
    
    # Create grid layout
    cols = st.columns(2)
    
    for idx, status in enumerate(api_statuses):
        with cols[idx % 2]:
            _render_integration_status_card(status)


def _render_web_scrapers_status(web_scraper_statuses: List[IntegrationStatus]):
    """Render web scrapers status section"""
    
    st.subheader("🕷️ LTL Carrier Tracking Status")
    
    # Separate priority and legacy carriers
    priority_carriers = [s for s in web_scraper_statuses if s.type == 'web_scraper']
    legacy_carriers = [s for s in web_scraper_statuses if s.type == 'web_scraper_legacy']
    
    if priority_carriers:
        st.markdown("#### 🎯 Priority Carriers")
        st.caption("These are your main LTL carriers with enhanced tracking capabilities")
        
        # Create grid for priority carriers
        cols = st.columns(2)
        
        for idx, status in enumerate(priority_carriers):
            with cols[idx % 2]:
                _render_carrier_status_card(status)
    
    if legacy_carriers:
        st.markdown("#### 📚 Legacy Carriers")
        for status in legacy_carriers:
            _render_legacy_carrier_status_card(status)


def _render_integration_status_card(status: IntegrationStatus):
    """Render a single integration status card"""
    
    # Status color and icon
    status_config = {
        'healthy': {'color': '#10b981', 'icon': '✅', 'bg': '#ecfdf5'},
        'degraded': {'color': '#f59e0b', 'icon': '⚠️', 'bg': '#fffbeb'},
        'failed': {'color': '#ef4444', 'icon': '❌', 'bg': '#fef2f2'},
        'unknown': {'color': '#6b7280', 'icon': '❓', 'bg': '#f9fafb'}
    }
    
    config = status_config.get(status.status, status_config['unknown'])
    
    # Format last activity
    last_activity = "Never"
    if status.last_success:
        last_activity = status.last_success.strftime('%H:%M:%S')
    elif status.last_failure:
        last_activity = f"Failed at {status.last_failure.strftime('%H:%M:%S')}"
    
    # Success rate display
    success_rate_display = f"{status.success_rate:.1f}%" if status.success_rate is not None else "N/A"
    
    # Response time display
    response_time_display = f"{status.response_time:.2f}s" if status.response_time is not None else "N/A"
    
    st.markdown(f"""
        <div style="
            background: {config['bg']};
            border: 1px solid {config['color']};
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">{config['icon']}</span>
                <strong style="color: {config['color']}; font-size: 1.1rem;">{status.name}</strong>
            </div>
            
            <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">
                <strong>Type:</strong> {status.type.replace('_', ' ').title()}
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem;">
                <div><strong>Success Rate:</strong> {success_rate_display}</div>
                <div><strong>Response Time:</strong> {response_time_display}</div>
                <div><strong>Today:</strong> {status.daily_successes}/{status.daily_requests}</div>
                <div><strong>Last Activity:</strong> {last_activity}</div>
            </div>
            
            {f'<div style="margin-top: 0.5rem; padding: 0.5rem; background: #fee2e2; border-radius: 4px; font-size: 0.8rem; color: #991b1b;"><strong>Error:</strong> {status.error_message}</div>' if status.error_message else ''}
        </div>
    """, unsafe_allow_html=True)


def _render_carrier_status_card(status: IntegrationStatus):
    """Render a carrier status card with enhanced details"""
    
    # Status color and icon
    status_config = {
        'healthy': {'color': '#10b981', 'icon': '✅', 'bg': '#ecfdf5'},
        'degraded': {'color': '#f59e0b', 'icon': '⚠️', 'bg': '#fffbeb'},
        'failed': {'color': '#ef4444', 'icon': '❌', 'bg': '#fef2f2'},
        'unknown': {'color': '#6b7280', 'icon': '❓', 'bg': '#f9fafb'}
    }
    
    config = status_config.get(status.status, status_config['unknown'])
    
    # Get carrier specific icon
    carrier_icons = {
        'FedEx Freight': '📦',
        'R+L Carriers': '🚛',
        'Estes Express': '🚚',
        'TForce Freight': '🚐',
        'Peninsula Truck Lines': '🚌'
    }
    
    carrier_icon = carrier_icons.get(status.name, '🚛')
    
    # Format statistics
    success_rate_display = f"{status.success_rate:.1f}%" if status.success_rate is not None else "N/A"
    response_time_display = f"{status.response_time:.2f}s" if status.response_time is not None else "N/A"
    
    st.markdown(f"""
        <div style="
            background: {config['bg']};
            border: 1px solid {config['color']};
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">{carrier_icon}</span>
                <strong style="color: {config['color']}; font-size: 1.1rem;">{status.name}</strong>
                <span style="font-size: 0.9rem; margin-left: auto;">{config['icon']}</span>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.85rem;">
                <div><strong>Tracked Today:</strong> {status.daily_successes}</div>
                <div><strong>Success Rate:</strong> {success_rate_display}</div>
                <div><strong>Response Time:</strong> {response_time_display}</div>
                <div><strong>Failed:</strong> {status.daily_failures}</div>
            </div>
            
            {f'<div style="margin-top: 0.5rem; padding: 0.5rem; background: #fee2e2; border-radius: 4px; font-size: 0.8rem; color: #991b1b;"><strong>Issue:</strong> {status.error_message}</div>' if status.error_message else ''}
        </div>
    """, unsafe_allow_html=True)


def _render_legacy_carrier_status_card(status: IntegrationStatus):
    """Render legacy carrier status card"""
    
    st.markdown(f"""
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem;">📚</span>
                <strong style="color: #475569; font-size: 1.1rem;">{status.name}</strong>
                <span style="font-size: 0.9rem; margin-left: auto;">✅</span>
            </div>
            
            <div style="font-size: 0.9rem; color: #64748b;">
                Additional carriers available for expansion. These carriers are ready to be configured
                when needed for specific customer requirements.
            </div>
        </div>
    """, unsafe_allow_html=True)


def _render_database_status(status: IntegrationStatus):
    """Render database status section"""
    
    st.subheader("🗄️ Database Status")
    
    status_config = {
        'healthy': {'color': '#10b981', 'icon': '✅', 'bg': '#ecfdf5'},
        'failed': {'color': '#ef4444', 'icon': '❌', 'bg': '#fef2f2'}
    }
    
    config = status_config.get(status.status, status_config['failed'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔗 Connection",
            value=f"{config['icon']} {status.status.title()}",
            delta=f"{status.response_time:.3f}s" if status.response_time else "N/A"
        )
    
    with col2:
        st.metric(
            label="📝 Records Today",
            value=status.daily_requests,
            delta=f"{status.daily_successes} successful"
        )
    
    with col3:
        st.metric(
            label="📈 Success Rate",
            value=f"{status.success_rate:.1f}%" if status.success_rate else "N/A",
            delta=f"{status.daily_failures} failed" if status.daily_failures > 0 else "No failures"
        )
    
    with col4:
        st.metric(
            label="🕐 Last Check",
            value=status.last_check.strftime('%H:%M:%S'),
            delta="Real-time"
        )


def _render_performance_metrics(all_statuses: List[IntegrationStatus], overview: SystemOverview):
    """Render performance metrics and charts"""
    
    st.subheader("📊 Performance Metrics")
    
    # Create performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        _render_status_distribution_chart(all_statuses)
    
    with col2:
        _render_daily_activity_chart(all_statuses)
    
    # Response time metrics
    _render_response_time_metrics(all_statuses)
    
    # Success rate table
    _render_success_rate_table(all_statuses)


def _render_status_distribution_chart(all_statuses: List[IntegrationStatus]):
    """Render status distribution chart"""
    
    # Count statuses
    status_counts = {}
    for status in all_statuses:
        status_counts[status.status] = status_counts.get(status.status, 0) + 1
    
    if not status_counts:
        st.info("No data available for status distribution")
        return
    
    st.markdown("**Integration Status Distribution**")
    
    # Create simple bar chart using streamlit
    df = pd.DataFrame({'Status': list(status_counts.keys()), 'Count': list(status_counts.values())})
    st.bar_chart(df.set_index('Status'))


def _render_daily_activity_chart(all_statuses: List[IntegrationStatus]):
    """Render daily activity bar chart"""
    
    # Prepare data
    chart_data = []
    
    for status in all_statuses:
        if status.daily_requests > 0:  # Only show active integrations
            chart_data.append({
                'Integration': status.name[:20],  # Truncate long names
                'Successes': status.daily_successes,
                'Failures': status.daily_failures
            })
    
    if not chart_data:
        st.info("No activity data available for today")
        return
    
    st.markdown("**Today's Activity by Integration**")
    
    # Create DataFrame and display as chart
    df = pd.DataFrame(chart_data)
    df = df.set_index('Integration')
    st.bar_chart(df)


def _render_response_time_metrics(all_statuses: List[IntegrationStatus]):
    """Render response time metrics"""
    
    st.markdown("#### ⏱️ Response Time Analysis")
    
    # Filter statuses with response times
    response_times = [(s.name, s.response_time) for s in all_statuses if s.response_time is not None]
    
    if not response_times:
        st.info("No response time data available")
        return
    
    # Create columns for metrics
    cols = st.columns(len(response_times))
    
    for idx, (name, response_time) in enumerate(response_times):
        with cols[idx]:
            # Determine color based on response time
            color = "#10b981" if response_time < 1.0 else "#f59e0b" if response_time < 3.0 else "#ef4444"
            
            st.metric(
                label=f"⏱️ {name[:15]}",
                value=f"{response_time:.2f}s",
                delta="Fast" if response_time < 1.0 else "Slow" if response_time > 3.0 else "OK"
            )


def _render_success_rate_table(all_statuses: List[IntegrationStatus]):
    """Render success rate table"""
    
    st.markdown("#### 📈 Success Rate Summary")
    
    # Prepare data for table
    table_data = []
    for status in all_statuses:
        if status.daily_requests > 0:
            table_data.append({
                'Integration': status.name,
                'Type': status.type.replace('_', ' ').title(),
                'Status': status.status.title(),
                'Requests': status.daily_requests,
                'Successes': status.daily_successes,
                'Failures': status.daily_failures,
                'Success Rate': f"{status.success_rate:.1f}%" if status.success_rate is not None else "N/A"
            })
    
    if not table_data:
        st.info("No activity data available for success rate analysis")
        return
    
    # Create DataFrame and display
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_recent_activity(recent_activity: List[Dict]):
    """Render recent activity timeline"""
    
    st.subheader("📈 Recent Activity")
    
    if not recent_activity:
        st.info("No recent activity to display")
        return
    
    # Activity timeline
    st.markdown("#### 🕐 Activity Timeline (Last 24 Hours)")
    
    for activity in recent_activity[:20]:  # Show last 20 activities
        timestamp = datetime.fromisoformat(activity['timestamp']).strftime('%H:%M:%S')
        
        # Status icon
        status_icon = "✅" if activity['status'] == 'success' else "❌"
        
        # Type icon
        type_icon = "🔗" if activity['type'] == 'API' else "🕷️"
        
        # Response time
        response_time = f" ({activity['response_time']:.2f}s)" if activity['response_time'] else ""
        
        # Error message
        error_msg = f" - {activity['error_message']}" if activity['error_message'] and activity['status'] != 'success' else ""
        
        st.markdown(f"""
            <div style="
                padding: 0.5rem;
                margin: 0.25rem 0;
                background: {'#f0f9ff' if activity['status'] == 'success' else '#fef2f2'};
                border-left: 3px solid {'#10b981' if activity['status'] == 'success' else '#ef4444'};
                border-radius: 0 4px 4px 0;
                font-size: 0.9rem;
            ">
                <strong>{timestamp}</strong> {type_icon} {status_icon} 
                <strong>{activity['integration_name']}</strong>{response_time}{error_msg}
            </div>
        """, unsafe_allow_html=True)
    
    # Activity summary
    if len(recent_activity) > 20:
        st.caption(f"Showing 20 of {len(recent_activity)} recent activities")


def _get_status_color(status: str) -> str:
    """Get color for status"""
    colors = {
        'healthy': '#10b981',
        'degraded': '#f59e0b', 
        'failed': '#ef4444',
        'unknown': '#6b7280'
    }
    return colors.get(status, '#6b7280') 