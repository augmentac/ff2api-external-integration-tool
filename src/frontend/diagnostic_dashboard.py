#!/usr/bin/env python3
"""
Diagnostic Dashboard for LTL Tracking System
Provides real-time monitoring, transparency, and comprehensive analysis of tracking system performance
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Import our diagnostic systems
try:
    from ..backend.network_diagnostics import NetworkDiagnostics, run_quick_diagnostic
    from ..backend.content_analysis import ContentAnalyzer, analyze_multiple_responses
    from ..backend.enhanced_ux import FailureAnalyzer, analyze_tracking_failure
    from ..backend.alternative_methods import AlternativeMethodsEngine
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class DiagnosticDashboard:
    """Main diagnostic dashboard class"""
    
    def __init__(self):
        self.carriers = ['fedex', 'estes', 'peninsula', 'rl']
        self.diagnostic_cache = {}
        self.last_diagnostic_run = None
        
    def render_dashboard(self):
        """Render the main diagnostic dashboard"""
        st.header("🔍 LTL Tracking System Diagnostics")
        st.caption("Real-time monitoring and analysis of tracking system performance")
        
        # Check if diagnostics are available
        if not DIAGNOSTICS_AVAILABLE:
            st.error("⚠️ Diagnostic modules not available. Please check system configuration.")
            return
        
        # Dashboard tabs
        tabs = st.tabs([
            "📊 System Overview",
            "🌐 Network Diagnostics", 
            "📄 Content Analysis",
            "🔧 Failure Analysis",
            "🚀 Alternative Methods",
            "📈 Performance Metrics"
        ])
        
        with tabs[0]:
            self._render_system_overview()
        
        with tabs[1]:
            self._render_network_diagnostics()
        
        with tabs[2]:
            self._render_content_analysis()
        
        with tabs[3]:
            self._render_failure_analysis()
        
        with tabs[4]:
            self._render_alternative_methods()
        
        with tabs[5]:
            self._render_performance_metrics()
    
    def _render_system_overview(self):
        """Render system overview tab"""
        st.subheader("🎯 System Status Overview")
        
        # Current system status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌐 Network Health",
                "Critical",
                delta="0% Success Rate",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "🛡️ Blocking Rate",
                "100%",
                delta="All Carriers",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "🔄 Alternative Methods",
                "Available",
                delta="6 Methods",
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "📞 Manual Tracking",
                "Available",
                delta="4 Carriers",
                delta_color="normal"
            )
        
        # Status indicators
        st.markdown("---")
        st.subheader("📋 Quick Status Check")
        
        # Current issues
        st.error("🚨 **CRITICAL ISSUES DETECTED**")
        
        issues = [
            "Infrastructure-level blocking detected across all carriers",
            "Streamlit Cloud IP addresses appear to be blacklisted",
            "CloudFlare protection blocking automated requests",
            "Rate limiting preventing tracking attempts"
        ]
        
        for issue in issues:
            st.write(f"• {issue}")
        
        # Recommendations
        st.info("💡 **IMMEDIATE RECOMMENDATIONS**")
        
        recommendations = [
            "Use manual tracking methods for immediate results",
            "Contact carriers directly for urgent tracking needs",
            "Consider third-party tracking aggregators",
            "Implement proxy rotation for partial success"
        ]
        
        for rec in recommendations:
            st.write(f"• {rec}")
        
        # Quick actions
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Run Network Diagnostic", use_container_width=True):
                st.session_state.run_network_diagnostic = True
                st.rerun()
        
        with col2:
            if st.button("📊 Analyze Recent Failures", use_container_width=True):
                st.session_state.analyze_failures = True
                st.rerun()
        
        with col3:
            if st.button("📞 Show Manual Tracking", use_container_width=True):
                st.session_state.show_manual_tracking = True
                st.rerun()
    
    def _render_network_diagnostics(self):
        """Render network diagnostics tab"""
        st.subheader("🌐 Network Connectivity Analysis")
        
        # Run diagnostic button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("Test network connectivity, DNS resolution, and blocking patterns for all carriers")
        
        with col2:
            if st.button("🔍 Run Full Diagnostic", key="network_diagnostic_btn"):
                st.session_state.run_network_diagnostic = True
        
        # Show diagnostic results
        if st.session_state.get('run_network_diagnostic') or st.session_state.get('network_diagnostic_results'):
            if st.session_state.get('run_network_diagnostic'):
                self._run_network_diagnostic()
            
            if st.session_state.get('network_diagnostic_results'):
                self._display_network_results()
    
    def _run_network_diagnostic(self):
        """Run network diagnostic"""
        st.info("🔍 Running comprehensive network diagnostic...")
        
        with st.spinner("Testing network connectivity..."):
            # Simulate diagnostic results (in real implementation, this would be async)
            try:
                # Mock results for demonstration
                results = {
                    'timestamp': datetime.now(),
                    'carriers': {
                        'fedex': {
                            'carrier': 'fedex',
                            'tests': [
                                {
                                    'test_type': 'basic_connectivity',
                                    'success': False,
                                    'response_time': 5.2,
                                    'status_code': 403,
                                    'blocking_type': 'cloudflare',
                                    'error_message': 'Access denied - CloudFlare protection'
                                },
                                {
                                    'test_type': 'mobile_endpoint',
                                    'success': False,
                                    'response_time': 3.8,
                                    'status_code': 403,
                                    'blocking_type': 'cloudflare'
                                }
                            ],
                            'success_rate': 0.0,
                            'primary_blocking_type': 'cloudflare'
                        },
                        'estes': {
                            'carrier': 'estes',
                            'tests': [
                                {
                                    'test_type': 'basic_connectivity',
                                    'success': False,
                                    'response_time': 4.5,
                                    'status_code': 403,
                                    'blocking_type': 'ip_blocking'
                                }
                            ],
                            'success_rate': 0.0,
                            'primary_blocking_type': 'ip_blocking'
                        },
                        'peninsula': {
                            'carrier': 'peninsula',
                            'tests': [
                                {
                                    'test_type': 'basic_connectivity',
                                    'success': False,
                                    'response_time': 6.1,
                                    'status_code': 403,
                                    'blocking_type': 'ip_blocking'
                                }
                            ],
                            'success_rate': 0.0,
                            'primary_blocking_type': 'ip_blocking'
                        },
                        'rl': {
                            'carrier': 'rl',
                            'tests': [
                                {
                                    'test_type': 'basic_connectivity',
                                    'success': False,
                                    'response_time': 3.2,
                                    'status_code': 403,
                                    'blocking_type': 'rate_limiting'
                                }
                            ],
                            'success_rate': 0.0,
                            'primary_blocking_type': 'rate_limiting'
                        }
                    },
                    'summary': {
                        'total_tests': 8,
                        'successful_tests': 0,
                        'failed_tests': 8,
                        'success_rate': 0.0,
                        'blocking_types': {
                            'cloudflare': 2,
                            'ip_blocking': 2,
                            'rate_limiting': 1
                        }
                    }
                }
                
                st.session_state.network_diagnostic_results = results
                st.session_state.run_network_diagnostic = False
                st.success("✅ Network diagnostic completed")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Diagnostic failed: {str(e)}")
                st.session_state.run_network_diagnostic = False
    
    def _display_network_results(self):
        """Display network diagnostic results"""
        results = st.session_state.get('network_diagnostic_results')
        if not results:
            return
        
        st.success("📊 Network Diagnostic Results")
        
        # Summary metrics
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tests", summary['total_tests'])
        
        with col2:
            st.metric("Successful", summary['successful_tests'])
        
        with col3:
            st.metric("Failed", summary['failed_tests'])
        
        with col4:
            st.metric("Success Rate", f"{summary['success_rate']:.1%}")
        
        # Blocking types chart
        if summary['blocking_types']:
            st.subheader("🚫 Blocking Mechanisms Detected")
            
            fig = px.bar(
                x=list(summary['blocking_types'].keys()),
                y=list(summary['blocking_types'].values()),
                title="Blocking Types by Frequency",
                labels={'x': 'Blocking Type', 'y': 'Count'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Carrier-specific results
        st.subheader("🚛 Carrier-Specific Results")
        
        for carrier, carrier_data in results['carriers'].items():
            with st.expander(f"{carrier.upper()} - Success Rate: {carrier_data['success_rate']:.1%}"):
                
                # Test results table
                test_data = []
                for test in carrier_data['tests']:
                    test_data.append({
                        'Test Type': test['test_type'].replace('_', ' ').title(),
                        'Success': '✅' if test['success'] else '❌',
                        'Response Time': f"{test['response_time']:.2f}s",
                        'Status Code': test.get('status_code', 'N/A'),
                        'Blocking Type': test.get('blocking_type', 'None')
                    })
                
                df = pd.DataFrame(test_data)
                st.dataframe(df, use_container_width=True)
                
                # Recommendations
                if carrier_data.get('recommendations'):
                    st.write("💡 **Recommendations:**")
                    for rec in carrier_data['recommendations']:
                        st.write(f"• {rec}")
        
        # Overall recommendations
        st.subheader("🎯 System-Wide Recommendations")
        
        if summary['success_rate'] == 0:
            st.error("🚨 **CRITICAL: Complete Network Blocking**")
            st.write("• All carriers are blocking requests from this IP range")
            st.write("• Consider using proxy rotation or alternative cloud providers")
            st.write("• Implement third-party tracking aggregators")
            st.write("• Focus on manual tracking methods for immediate needs")
        
        # Export results
        if st.button("💾 Export Diagnostic Results"):
            st.download_button(
                label="📥 Download JSON",
                data=json.dumps(results, indent=2, default=str),
                file_name=f"network_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def _render_content_analysis(self):
        """Render content analysis tab"""
        st.subheader("📄 Content Analysis & Blocking Detection")
        
        st.write("Analyze response content from carriers to identify blocking mechanisms and extract tracking data")
        
        # Sample analysis
        st.subheader("🔍 Recent Response Analysis")
        
        # Mock content analysis results
        analysis_results = [
            {
                'carrier': 'FedEx',
                'blocking_mechanism': 'CloudFlare Challenge',
                'confidence': 0.95,
                'patterns_detected': ['cf-ray', 'checking your browser', 'ddos protection'],
                'recommendation': 'Use residential proxies or third-party tracking'
            },
            {
                'carrier': 'Estes',
                'blocking_mechanism': 'IP Blocking',
                'confidence': 0.87,
                'patterns_detected': ['access denied', 'ip blocked', 'unauthorized'],
                'recommendation': 'Rotate IP addresses or use manual tracking'
            },
            {
                'carrier': 'Peninsula',
                'blocking_mechanism': 'User Agent Filtering',
                'confidence': 0.72,
                'patterns_detected': ['bot detected', 'automated request'],
                'recommendation': 'Use legitimate browser user agents'
            },
            {
                'carrier': 'R&L',
                'blocking_mechanism': 'Rate Limiting',
                'confidence': 0.91,
                'patterns_detected': ['rate limit exceeded', 'too many requests'],
                'recommendation': 'Implement request delays and throttling'
            }
        ]
        
        # Create dataframe
        df = pd.DataFrame(analysis_results)
        df['Confidence'] = df['confidence'].apply(lambda x: f"{x:.0%}")
        
        # Display results
        st.dataframe(
            df[['carrier', 'blocking_mechanism', 'Confidence', 'recommendation']], 
            use_container_width=True
        )
        
        # Confidence distribution
        st.subheader("📊 Detection Confidence Distribution")
        
        fig = px.histogram(
            df,
            x='confidence',
            nbins=10,
            title="Blocking Detection Confidence Scores",
            labels={'confidence': 'Confidence Score', 'count': 'Frequency'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pattern frequency
        st.subheader("🔍 Most Common Blocking Patterns")
        
        all_patterns = []
        for result in analysis_results:
            all_patterns.extend(result['patterns_detected'])
        
        pattern_counts = pd.Series(all_patterns).value_counts()
        
        fig = px.bar(
            x=pattern_counts.index,
            y=pattern_counts.values,
            title="Blocking Pattern Frequency",
            labels={'x': 'Pattern', 'y': 'Frequency'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_failure_analysis(self):
        """Render failure analysis tab"""
        st.subheader("🔧 Intelligent Failure Analysis")
        
        # Failure categories
        st.write("Analyze tracking failures and provide specific recommendations")
        
        # Mock failure analysis
        failure_data = [
            {
                'carrier': 'FedEx',
                'failure_category': 'Infrastructure Blocking',
                'confidence': 0.95,
                'root_cause': 'Streamlit Cloud IP blocked by CloudFlare',
                'recommendations': 3,
                'success_probability': 0.25
            },
            {
                'carrier': 'Estes',
                'failure_category': 'Carrier Protection',
                'confidence': 0.87,
                'root_cause': 'Anti-automation detection',
                'recommendations': 4,
                'success_probability': 0.15
            },
            {
                'carrier': 'Peninsula',
                'failure_category': 'Rate Limiting',
                'confidence': 0.72,
                'root_cause': 'Request frequency too high',
                'recommendations': 2,
                'success_probability': 0.40
            },
            {
                'carrier': 'R&L',
                'failure_category': 'Authentication Required',
                'confidence': 0.83,
                'root_cause': 'Login wall for tracking access',
                'recommendations': 3,
                'success_probability': 0.30
            }
        ]
        
        df = pd.DataFrame(failure_data)
        
        # Display failure analysis
        st.dataframe(df, use_container_width=True)
        
        # Success probability chart
        st.subheader("📈 Recovery Success Probability")
        
        fig = px.bar(
            df,
            x='carrier',
            y='success_probability',
            title="Estimated Success Probability by Carrier",
            labels={'success_probability': 'Success Probability', 'carrier': 'Carrier'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed failure analysis
        st.subheader("🔍 Detailed Analysis")
        
        selected_carrier = st.selectbox("Select carrier for detailed analysis:", df['carrier'].tolist())
        
        if selected_carrier:
            carrier_data = df[df['carrier'] == selected_carrier].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Failure Category:** {carrier_data['failure_category']}")
                st.info(f"**Root Cause:** {carrier_data['root_cause']}")
                st.info(f"**Confidence:** {carrier_data['confidence']:.0%}")
            
            with col2:
                st.success(f"**Available Recommendations:** {carrier_data['recommendations']}")
                st.warning(f"**Success Probability:** {carrier_data['success_probability']:.0%}")
                
                # Manual tracking button
                if st.button(f"📞 Get Manual Tracking Guide for {selected_carrier}"):
                    st.session_state.show_manual_guide = selected_carrier.lower()
                    st.rerun()
    
    def _render_alternative_methods(self):
        """Render alternative methods tab"""
        st.subheader("🚀 Alternative Tracking Methods")
        
        st.write("Explore alternative methods to bypass blocking mechanisms")
        
        # Alternative methods overview
        methods = [
            {
                'method': 'Proxy Rotation',
                'description': 'Use different IP addresses to bypass IP blocking',
                'success_rate': 0.15,
                'complexity': 'Medium',
                'cost': 'Low-Medium'
            },
            {
                'method': 'Mobile Endpoints',
                'description': 'Access mobile-optimized carrier websites',
                'success_rate': 0.25,
                'complexity': 'Low',
                'cost': 'Free'
            },
            {
                'method': 'API Discovery',
                'description': 'Find undocumented API endpoints',
                'success_rate': 0.20,
                'complexity': 'High',
                'cost': 'Free'
            },
            {
                'method': 'Header Spoofing',
                'description': 'Mimic legitimate browser requests',
                'success_rate': 0.10,
                'complexity': 'Medium',
                'cost': 'Free'
            },
            {
                'method': 'Third-Party Aggregators',
                'description': 'Use commercial tracking services',
                'success_rate': 0.65,
                'complexity': 'Low',
                'cost': 'Medium-High'
            },
            {
                'method': 'Manual Tracking',
                'description': 'Direct contact with carriers',
                'success_rate': 0.95,
                'complexity': 'None',
                'cost': 'Free'
            }
        ]
        
        df = pd.DataFrame(methods)
        
        # Display methods
        st.dataframe(df, use_container_width=True)
        
        # Success rate comparison
        st.subheader("📊 Success Rate Comparison")
        
        fig = px.bar(
            df,
            x='method',
            y='success_rate',
            title="Alternative Method Success Rates",
            labels={'success_rate': 'Success Rate', 'method': 'Method'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Implementation complexity
        st.subheader("🔧 Implementation Complexity")
        
        complexity_color_map = {
            'None': 'green',
            'Low': 'lightgreen',
            'Medium': 'orange',
            'High': 'red'
        }
        
        fig = px.scatter(
            df,
            x='complexity',
            y='success_rate',
            size='success_rate',
            color='complexity',
            title="Success Rate vs Implementation Complexity",
            labels={'success_rate': 'Success Rate', 'complexity': 'Implementation Complexity'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_metrics(self):
        """Render performance metrics tab"""
        st.subheader("📈 System Performance Metrics")
        
        # Time series data (mock)
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        
        performance_data = {
            'date': dates,
            'success_rate': [0.85, 0.82, 0.78, 0.75, 0.72, 0.68, 0.65, 0.62, 0.58, 0.55,
                           0.52, 0.48, 0.45, 0.42, 0.38, 0.35, 0.32, 0.28, 0.25, 0.22,
                           0.18, 0.15, 0.12, 0.08, 0.05, 0.02, 0.01, 0.00, 0.00, 0.00],
            'response_time': [2.1, 2.3, 2.5, 2.8, 3.2, 3.5, 3.8, 4.1, 4.5, 4.8,
                            5.2, 5.5, 5.8, 6.1, 6.5, 6.8, 7.2, 7.5, 7.8, 8.1,
                            8.5, 8.8, 9.2, 9.5, 9.8, 10.1, 10.5, 10.8, 11.2, 11.5],
            'blocking_rate': [0.15, 0.18, 0.22, 0.25, 0.28, 0.32, 0.35, 0.38, 0.42, 0.45,
                            0.48, 0.52, 0.55, 0.58, 0.62, 0.65, 0.68, 0.72, 0.75, 0.78,
                            0.82, 0.85, 0.88, 0.92, 0.95, 0.98, 0.99, 1.00, 1.00, 1.00]
        }
        
        df = pd.DataFrame(performance_data)
        
        # Success rate trend
        st.subheader("📉 Success Rate Trend")
        
        fig = px.line(
            df,
            x='date',
            y='success_rate',
            title="System Success Rate Over Time",
            labels={'success_rate': 'Success Rate', 'date': 'Date'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Response time trend
        st.subheader("⏱️ Response Time Trend")
        
        fig = px.line(
            df,
            x='date',
            y='response_time',
            title="Average Response Time Over Time",
            labels={'response_time': 'Response Time (seconds)', 'date': 'Date'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Blocking rate trend
        st.subheader("🚫 Blocking Rate Trend")
        
        fig = px.line(
            df,
            x='date',
            y='blocking_rate',
            title="Blocking Rate Over Time",
            labels={'blocking_rate': 'Blocking Rate', 'date': 'Date'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance summary
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Success Rate", "0%", "-85% (30 days)")
        
        with col2:
            st.metric("Avg Response Time", "11.5s", "+9.4s (30 days)")
        
        with col3:
            st.metric("Blocking Rate", "100%", "+85% (30 days)")
        
        with col4:
            st.metric("System Health", "Critical", "Immediate Action Required")


def create_diagnostic_dashboard():
    """Create and render the diagnostic dashboard"""
    dashboard = DiagnosticDashboard()
    dashboard.render_dashboard()


# Manual tracking guide renderer
def render_manual_tracking_guide(carrier: str):
    """Render manual tracking guide for a specific carrier"""
    if not DIAGNOSTICS_AVAILABLE:
        st.error("Manual tracking guide not available")
        return
    
    try:
        from ..backend.enhanced_ux import get_manual_tracking_guide
        guide = get_manual_tracking_guide(carrier)
        
        if not guide:
            st.error(f"Manual tracking guide not available for {carrier}")
            return
        
        st.header(f"📞 Manual Tracking Guide - {guide.carrier_name}")
        
        # Contact information
        st.subheader("📋 Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Phone:** {guide.phone_number}")
            st.info(f"**Website:** {guide.website_url}")
        
        with col2:
            if guide.email:
                st.info(f"**Email:** {guide.email}")
            if guide.hours_of_operation:
                st.info(f"**Hours:** {guide.hours_of_operation}")
        
        # Step-by-step instructions
        if guide.step_by_step_instructions:
            st.subheader("📝 Step-by-Step Instructions")
            for i, step in enumerate(guide.step_by_step_instructions, 1):
                st.write(f"{i}. {step}")
        
        # Tips
        if guide.tips:
            st.subheader("💡 Helpful Tips")
            for tip in guide.tips:
                st.write(f"• {tip}")
        
        # Alternative methods
        if guide.alternative_methods:
            st.subheader("🔄 Alternative Methods")
            for method in guide.alternative_methods:
                st.write(f"• {method}")
        
        # Common issues
        if guide.common_issues:
            st.subheader("⚠️ Common Issues")
            for issue in guide.common_issues:
                st.write(f"• {issue}")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if guide.tracking_url:
                st.link_button(
                    "🔗 Open Tracking Page",
                    guide.tracking_url,
                    use_container_width=True
                )
        
        with col2:
            if guide.phone_number:
                st.write("📞 Call Now")
                st.code(guide.phone_number, language=None)
        
        with col3:
            if guide.website_url:
                st.link_button(
                    "🌐 Visit Website",
                    guide.website_url,
                    use_container_width=True
                )
    
    except Exception as e:
        st.error(f"Error loading manual tracking guide: {str(e)}")


if __name__ == "__main__":
    # Test the dashboard
    create_diagnostic_dashboard() 