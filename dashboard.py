"""
Content Amplifier - Combined Control & Visualization Dashboard
Run your entire content pipeline and monitor results in real-time
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import sys
import traceback

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import modules
try:
    from src.gap_detector import GapDetector
    from src.content_analyzer import ContentAnalyzer
    from src.content_generator import ContentGenerator
    from src.distribution_manager_v2 import DistributionManagerV2
    from src.affiliate_manager import AffiliateManager
    from src.revenue_tracker import RevenueTracker
    from src.orchestrator import ContentAmplifierOrchestrator
    from src.utils import (
        load_json, save_json, format_currency, format_number, 
        format_percentage, format_date, days_ago, ensure_directory
    )
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Content Amplifier - Control Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'system_mode' not in st.session_state:
    st.session_state.system_mode = 'demo'
if 'last_operation' not in st.session_state:
    st.session_state.last_operation = None
if 'operation_result' not in st.session_state:
    st.session_state.operation_result = None

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.1em;
        opacity: 0.9;
    }
    .status-success {
        color: #10b981;
        font-weight: bold;
    }
    .status-warning {
        color: #f59e0b;
        font-weight: bold;
    }
    .status-error {
        color: #ef4444;
        font-weight: bold;
    }
    .status-info {
        color: #3b82f6;
        font-weight: bold;
    }
    .platform-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        font-size: 0.9em;
        font-weight: bold;
    }
    .badge-stackoverflow {
        background: #f48024;
        color: white;
    }
    .badge-reddit {
        background: #ff4500;
        color: white;
    }
    .badge-devto {
        background: #0a0a0a;
        color: white;
    }
    .badge-twitter {
        background: #1da1f2;
        color: white;
    }
    .badge-medium {
        background: #00ab6c;
        color: white;
    }
    .badge-linkedin {
        background: #0077b5;
        color: white;
    }
    .operation-log {
        background: #1e1e1e;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        max-height: 300px;
        overflow-y: auto;
        margin: 10px 0;
    }
    .action-button {
        width: 100%;
        padding: 15px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def initialize_orchestrator(demo_mode: bool = True):
    """Initialize the orchestrator"""
    try:
        if st.session_state.orchestrator is None:
            with st.spinner("Initializing Content Amplifier..."):
                st.session_state.orchestrator = ContentAmplifierOrchestrator(
                    demo_mode=demo_mode
                )
                st.session_state.system_mode = 'demo' if demo_mode else 'production'
            return True
        return True
    except Exception as e:
        st.error(f"Failed to initialize orchestrator: {e}")
        return False

@st.cache_data(ttl=60)
def load_gaps_data():
    """Load gap detection results"""
    gaps_file = 'data/gaps/gaps.json'
    if os.path.exists(gaps_file):
        return load_json(gaps_file, {'top_opportunities': [], 'gaps': {}})
    return {'top_opportunities': [], 'gaps': {}}

@st.cache_data(ttl=60)
def load_briefs_data():
    """Load content briefs"""
    briefs_file = 'data/briefs/content_briefs.json'
    if os.path.exists(briefs_file):
        return load_json(briefs_file, [])
    return []

@st.cache_data(ttl=60)
def load_revenue_data():
    """Load revenue tracking data"""
    tracker = RevenueTracker()
    return {
        'tracker': tracker,
        'total_revenue': tracker.get_total_revenue(),
        'revenue_7d': tracker.get_total_revenue(7),
        'revenue_30d': tracker.get_total_revenue(30),
        'by_platform': tracker.get_revenue_by_platform(30),
        'by_type': tracker.get_revenue_by_type(30),
        'top_content': tracker.get_top_performing_content(10),
        'daily_revenue': tracker.get_daily_revenue(30)
    }

@st.cache_data(ttl=60)
def load_system_state():
    """Load system state"""
    state_file = 'system_state.json'
    if os.path.exists(state_file):
        return load_json(state_file, {})
    return {
        'last_scan': None,
        'gaps_found': 0,
        'content_created': 0,
        'content_distributed': 0,
        'total_revenue': 0
    }

def render_platform_badge(platform: str):
    """Render platform badge"""
    return f'<span class="platform-badge badge-{platform.lower()}">{platform.upper()}</span>'

def display_operation_result(result: Dict):
    """Display operation result in a formatted way"""
    if result.get('success'):
        st.success(f"✅ Operation completed successfully!")
    else:
        st.error(f"❌ Operation failed: {result.get('error', 'Unknown error')}")
    
    # Show details in expander
    with st.expander("View Operation Details"):
        st.json(result)

# ============================================================================
# SIDEBAR - SYSTEM CONTROL
# ============================================================================

with st.sidebar:
    st.title("🚀 Control Center")
    st.markdown("---")
    
    # System Mode Toggle
    st.subheader("System Mode")
    current_mode = st.session_state.system_mode
    
    mode_col1, mode_col2 = st.columns(2)
    
    with mode_col1:
        if st.button("🎮 Demo Mode", 
                    type="primary" if current_mode == 'demo' else "secondary",
                    width="stretch"):
            st.session_state.orchestrator = None
            initialize_orchestrator(demo_mode=True)
            st.rerun()
    
    with mode_col2:
        if st.button("⚡ Production", 
                    type="primary" if current_mode == 'production' else "secondary",
                    width="stretch"):
            st.session_state.orchestrator = None
            initialize_orchestrator(demo_mode=False)
            st.rerun()
    
    if current_mode == 'demo':
        st.info("🎮 Demo Mode: Using simulated data")
    else:
        st.warning("⚡ Production Mode: Real API calls")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🎯 Control Panel", "📊 Dashboard", "🔍 Gap Detection", 
         "📝 Content Pipeline", "📤 Distribution", "💰 Revenue Analytics"]
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.subheader("Quick Stats")
    state = load_system_state()
    
    st.metric("Gaps Found", format_number(state.get('gaps_found', 0)))
    st.metric("Content Created", format_number(state.get('content_created', 0)))
    st.metric("Distributed", format_number(state.get('content_distributed', 0)))
    
    revenue_data = load_revenue_data()
    st.metric("Total Revenue", format_currency(revenue_data['total_revenue']))
    
    st.markdown("---")
    
    # Last updated
    if state.get('last_scan'):
        last_scan = state['last_scan']
        days = days_ago(last_scan)
        st.caption(f"Last scan: {days} days ago")
    else:
        st.caption("No scan data available")
    
    # Refresh button
    if st.button("🔄 Refresh Data", width="stretch" ):
        st.cache_data.clear()
        st.rerun()

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Initialize orchestrator if not done
if st.session_state.orchestrator is None:
    initialize_orchestrator(demo_mode=(st.session_state.system_mode == 'demo'))

# Control Panel Page
if page == "🎯 Control Panel":
    st.title("🎯 System Control Panel")
    st.markdown("Execute operations and monitor the content pipeline")
    
    # Operation status
    if st.session_state.last_operation:
        st.info(f"Last operation: {st.session_state.last_operation}")
        if st.session_state.operation_result:
            display_operation_result(st.session_state.operation_result)
    
    st.markdown("---")
    
    # Main Operations
    st.subheader("🚀 Main Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Full Pipeline")
        st.markdown("Run the complete workflow from gap detection to distribution")
        
        if st.button("▶️ Run Full Pipeline", key="full_pipeline", width="stretch"):
            with st.spinner("Running full pipeline..."):
                try:
                    result = st.session_state.orchestrator.run_full_pipeline(manual_mode=True)
                    st.session_state.last_operation = "Full Pipeline"
                    st.session_state.operation_result = result
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Pipeline error: {e}")
                    st.code(traceback.format_exc())
        
        st.markdown("---")
        
        st.markdown("### 📊 Generate Report")
        st.markdown("Create weekly performance report")
        
        if st.button("📄 Generate Weekly Report", key="weekly_report", width="stretch"):
            with st.spinner("Generating report..."):
                try:
                    report = st.session_state.orchestrator.generate_weekly_report()
                    st.session_state.last_operation = "Weekly Report"
                    st.session_state.operation_result = {'success': True, 'report': report}
                    st.success("Report generated!")
                    
                    # Display report
                    with st.expander("View Report"):
                        st.json(report)
                except Exception as e:
                    st.error(f"Report error: {e}")
    
    with col2:
        st.markdown("### Individual Stages")
        st.markdown("Run specific stages of the pipeline")
        
        if st.button("🔍 Gap Detection Only", key="gap_detection", width="stretch"):
            with st.spinner("Detecting content gaps..."):
                try:
                    result = st.session_state.orchestrator._run_gap_detection()
                    st.session_state.last_operation = "Gap Detection"
                    st.session_state.operation_result = result
                    
                    # Save results
                    if result.get('success') and result.get('gaps'):
                        ensure_directory('data/gaps')
                        save_json('data/gaps/gaps.json', {
                            'scan_time': datetime.now().isoformat(),
                            'top_opportunities': result['gaps'],
                            'gaps': {'all': result['gaps']}
                        })
                    
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Gap detection error: {e}")
                    st.code(traceback.format_exc())
        
        if st.button("📊 Analyze Gaps", key="analyze_gaps", width="stretch" ):
            gaps_data = load_gaps_data()
            gaps = gaps_data.get('top_opportunities', [])
            
            if not gaps:
                st.warning("No gaps available. Run gap detection first.")
            else:
                with st.spinner("Analyzing gaps..."):
                    try:
                        result = st.session_state.orchestrator._run_content_analysis(gaps[:5])
                        st.session_state.last_operation = "Content Analysis"
                        st.session_state.operation_result = result
                        
                        # Save briefs
                        if result.get('success') and result.get('briefs'):
                            ensure_directory('data/briefs')
                            save_json('data/briefs/content_briefs.json', result['briefs'])
                        
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                        st.code(traceback.format_exc())
        
        if st.button("✍️ Generate Content", key="generate_content", width="stretch"):
            briefs_data = load_briefs_data()
            
            if not briefs_data:
                st.warning("No briefs available. Run content analysis first.")
            else:
                with st.spinner("Generating content..."):
                    try:
                        result = st.session_state.orchestrator._run_content_generation(
                            briefs_data[:3], 
                            manual_mode=False
                        )
                        st.session_state.last_operation = "Content Generation"
                        st.session_state.operation_result = result
                        
                        # Save articles
                        if result.get('success') and result.get('packages'):
                            ensure_directory('outputs/articles')
                            for i, package in enumerate(result['packages']):
                                save_json(f'outputs/articles/package_{i}_{int(datetime.now().timestamp())}.json', package)
                        
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation error: {e}")
                        st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Revenue Tracking
    st.subheader("💰 Revenue Tracking")
    
    with st.expander("➕ Add Manual Conversion"):
        with st.form("manual_conversion"):
            col1, col2 = st.columns(2)
            
            with col1:
                content_id = st.text_input("Content ID", value=f"manual_{int(datetime.now().timestamp())}")
                content_title = st.text_input("Content Title", value="")
                platform = st.selectbox("Platform", ["devto", "medium", "twitter", "linkedin", "github"])
            
            with col2:
                conv_type = st.selectbox("Conversion Type", ["affiliate", "consulting", "sponsored"])
                amount = st.number_input("Amount ($)", min_value=0.0, value=0.0, step=0.01)
                notes = st.text_area("Notes", value="")
            
            if st.form_submit_button("💾 Save Conversion", width="stretch"):
                if content_title and amount > 0:
                    try:
                        tracker = RevenueTracker()
                        conversion = tracker.track_conversion(
                            content_id=content_id,
                            content_title=content_title,
                            platform=platform,
                            conversion_type=conv_type,
                            amount=amount,
                            notes=notes
                        )
                        st.success(f"✅ Conversion saved: {format_currency(amount)}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving conversion: {e}")
                else:
                    st.warning("Please fill in content title and amount")
    
    st.markdown("---")
    
    # System Configuration
    st.subheader("⚙️ System Configuration")
    
    with st.expander("View/Edit Configuration"):
        config_file = 'config.json'
        
        if os.path.exists(config_file):
            config = load_json(config_file)
            
            # Edit config
            st.markdown("**Detection Settings:**")
            col1, col2 = st.columns(2)
            
            with col1:
                so_tags = st.text_area(
                    "Stack Overflow Tags (comma-separated)",
                    value=", ".join(config.get('detection', {}).get('stackoverflow_tags', []))
                )
            
            with col2:
                reddit_subs = st.text_area(
                    "Reddit Subreddits (comma-separated)",
                    value=", ".join(config.get('detection', {}).get('reddit_subreddits', []))
                )
            
            if st.button("💾 Save Configuration", width="stretch"):
                config['detection']['stackoverflow_tags'] = [t.strip() for t in so_tags.split(',')]
                config['detection']['reddit_subreddits'] = [s.strip() for s in reddit_subs.split(',')]
                save_json(config_file, config)
                st.success("Configuration saved!")
        else:
            st.info("No configuration file found. System will use defaults.")

# Dashboard Page
elif page == "📊 Dashboard":
    st.title("📊 System Dashboard")
    st.markdown("Real-time monitoring of your content amplification system")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    gaps_data = load_gaps_data()
    briefs_data = load_briefs_data()
    revenue_data = load_revenue_data()
    state = load_system_state()
    
    with col1:
        st.metric(
            "Active Opportunities",
            format_number(len(gaps_data.get('top_opportunities', []))),
            delta=f"+{len(gaps_data.get('top_opportunities', []))} detected"
        )
    
    with col2:
        st.metric(
            "Content Briefs",
            format_number(len(briefs_data)),
            delta="Ready for generation"
        )
    
    with col3:
        st.metric(
            "Content Created",
            format_number(state.get('content_created', 0)),
            delta="This month"
        )
    
    with col4:
        st.metric(
            "Revenue (30d)",
            format_currency(revenue_data['revenue_30d']),
            delta=format_currency(revenue_data['revenue_7d']) + " (7d)"
        )
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Top Opportunities")
        
        top_opps = gaps_data.get('top_opportunities', [])[:5]
        if top_opps:
            for i, gap in enumerate(top_opps, 1):
                with st.container():
                    st.markdown(f"**{i}. {gap.get('title', 'Untitled')}**")
                    
                    cols = st.columns([1, 1, 1])
                    with cols[0]:
                        st.markdown(render_platform_badge(gap.get('platform', 'unknown')), unsafe_allow_html=True)
                    with cols[1]:
                        st.caption(f"Score: {gap.get('gap_score', 0):.1f}")
                    with cols[2]:
                        views = gap.get('views', gap.get('score', 0))
                        st.caption(f"Views: {format_number(views)}")
                    
                    st.markdown("---")
        else:
            st.info("No opportunities detected yet. Use Control Panel to run gap detection.")
    
    with col2:
        st.subheader("💰 Revenue by Platform")
        
        platform_revenue = revenue_data['by_platform']
        if platform_revenue:
            for platform, data in sorted(platform_revenue.items(), 
                                        key=lambda x: x[1]['revenue'], 
                                        reverse=True):
                st.markdown(f"**{platform.upper()}**")
                cols = st.columns([3, 1])
                with cols[0]:
                    revenue = data['revenue']
                    max_revenue = max(d['revenue'] for d in platform_revenue.values())
                    progress = revenue / max_revenue if max_revenue > 0 else 0
                    st.progress(progress)
                with cols[1]:
                    st.markdown(f"**{format_currency(revenue)}**")
                st.caption(f"{data['conversions']} conversions")
        else:
            st.info("No revenue data available yet. Add conversions via Control Panel.")

# Gap Detection Page
elif page == "🔍 Gap Detection":
    st.title("🔍 Gap Detection")
    st.markdown("Content opportunities discovered across platforms")
    
    gaps_data = load_gaps_data()
    
    # Quick action button
    if st.button("🔄 Run New Gap Scan", key="rescan_gaps"):
        with st.spinner("Scanning for content gaps..."):
            try:
                result = st.session_state.orchestrator._run_gap_detection()
                st.session_state.last_operation = "Gap Detection"
                st.session_state.operation_result = result
                
                if result.get('success') and result.get('gaps'):
                    ensure_directory('data/gaps')
                    save_json('data/gaps/gaps.json', {
                        'scan_time': datetime.now().isoformat(),
                        'top_opportunities': result['gaps'],
                        'gaps': {'all': result['gaps']}
                    })
                
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    all_gaps = gaps_data.get('gaps', {})
    so_gaps = all_gaps.get('stackoverflow', [])
    reddit_gaps = all_gaps.get('reddit', [])
    devto_gaps = all_gaps.get('devto', [])
    
    with col1:
        st.metric("Total Gaps", format_number(len(gaps_data.get('top_opportunities', []))))
    with col2:
        st.metric("Stack Overflow", format_number(len(so_gaps)))
    with col3:
        st.metric("Reddit", format_number(len(reddit_gaps)))
    with col4:
        st.metric("Dev.to", format_number(len(devto_gaps)))
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        platform_filter = st.selectbox(
            "Platform",
            ["All", "Stack Overflow", "Reddit", "Dev.to"]
        )
    
    with col2:
        min_score = st.slider("Minimum Gap Score", 0, 200, 50)
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Gap Score", "Views", "Recent"])
    
    # Get filtered gaps
    all_opportunities = gaps_data.get('top_opportunities', [])
    
    # Apply filters
    filtered_gaps = all_opportunities
    
    if platform_filter != "All":
        platform_map = {
            "Stack Overflow": "stackoverflow",
            "Reddit": "reddit",
            "Dev.to": "devto"
        }
        filtered_gaps = [g for g in filtered_gaps 
                        if g.get('platform', '').lower() == platform_map.get(platform_filter, '').lower()]
    
    filtered_gaps = [g for g in filtered_gaps if g.get('gap_score', 0) >= min_score]
    
    # Sort
    if sort_by == "Gap Score":
        filtered_gaps.sort(key=lambda x: x.get('gap_score', 0), reverse=True)
    elif sort_by == "Views":
        filtered_gaps.sort(key=lambda x: x.get('views', x.get('score', 0)), reverse=True)
    
    st.markdown(f"### Showing {len(filtered_gaps)} opportunities")
    
    # Display gaps
    for i, gap in enumerate(filtered_gaps[:20], 1):
        with st.expander(f"{i}. {gap.get('title', 'Untitled')}"):
            cols = st.columns([2, 1, 1, 1])
            
            with cols[0]:
                st.markdown(render_platform_badge(gap.get('platform', 'unknown')), unsafe_allow_html=True)
            
            with cols[1]:
                st.metric("Gap Score", f"{gap.get('gap_score', 0):.1f}")
            
            with cols[2]:
                views = gap.get('views', gap.get('score', gap.get('reactions', 0)))
                st.metric("Engagement", format_number(views))
            
            with cols[3]:
                if gap.get('tags'):
                    st.caption("Tags: " + ", ".join(gap['tags'][:3]))
            
            if gap.get('url'):
                st.markdown(f"[View Original]({gap['url']})")

# Content Pipeline Page
elif page == "📝 Content Pipeline":
    st.title("📝 Content Pipeline")
    st.markdown("Track content from brief to publication")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Analyze Gaps", key="pipeline_analyze", width="stretch"):
            gaps_data = load_gaps_data()
            gaps = gaps_data.get('top_opportunities', [])
            
            if not gaps:
                st.warning("No gaps available. Run gap detection first.")
            else:
                with st.spinner("Analyzing gaps..."):
                    result = st.session_state.orchestrator._run_content_analysis(gaps[:5])
                    if result.get('success') and result.get('briefs'):
                        ensure_directory('data/briefs')
                        save_json('data/briefs/content_briefs.json', result['briefs'])
                    st.cache_data.clear()
                    st.rerun()
    
    with col2:
        if st.button("✍️ Generate Content", key="pipeline_generate", width="stretch"):
            briefs_data = load_briefs_data()
            
            if not briefs_data:
                st.warning("No briefs available. Run content analysis first.")
            else:
                with st.spinner("Generating content..."):
                    result = st.session_state.orchestrator._run_content_generation(briefs_data[:3], False)
                    if result.get('success') and result.get('packages'):
                        ensure_directory('outputs/articles')
                        for i, package in enumerate(result['packages']):
                            save_json(f'outputs/articles/package_{i}_{int(datetime.now().timestamp())}.json', package)
                    st.cache_data.clear()
                    st.rerun()
    
    with col3:
        if st.button("📤 Distribute", key="pipeline_distribute", width="stretch"):
            st.info("Distribution feature - would post to platforms")
    
    st.markdown("---")
    
    # Pipeline stages
    col1, col2, col3, col4 = st.columns(4)
    
    gaps_data = load_gaps_data()
    briefs_data = load_briefs_data()
    
    with col1:
        st.metric("Opportunities", len(gaps_data.get('top_opportunities', [])))
        st.progress(1.0)
    
    with col2:
        st.metric("Briefs", len(briefs_data))
        progress = len(briefs_data) / max(len(gaps_data.get('top_opportunities', [])), 1)
        st.progress(min(progress, 1.0))
    
    with col3:
        article_count = len([f for f in os.listdir('outputs/articles') if f.endswith('.json')]) if os.path.exists('outputs/articles') else 0
        st.metric("Articles", article_count)
        progress = article_count / max(len(briefs_data), 1)
        st.progress(min(progress, 1.0))
    
    with col4:
        st.metric("Distributed", 0)
        st.progress(0.0)
    
    st.markdown("---")
    
    # Show briefs
    st.subheader("📋 Content Briefs")
    
    if briefs_data:
        for i, brief in enumerate(briefs_data[:10], 1):
            with st.expander(f"{i}. {brief.get('gap', {}).get('title', 'Untitled')}"):
                cols = st.columns([2, 1, 1])
                
                with cols[0]:
                    title_suggestions = brief.get('brief', {}).get('title_suggestions', [])
                    if title_suggestions:
                        st.markdown(f"**Suggested Title:** {title_suggestions[0]}")
                
                with cols[1]:
                    priority = brief.get('priority', 'unknown')
                    color = {'high': 'success', 'medium': 'warning', 'low': 'error'}.get(priority, 'info')
                    st.markdown(f"<span class='status-{color}'>Priority: {priority.upper()}</span>", 
                               unsafe_allow_html=True)
                
                with cols[2]:
                    word_count = brief.get('brief', {}).get('estimated_word_count', 0)
                    st.metric("Est. Words", format_number(word_count))
    else:
        st.info("No content briefs available. Use Control Panel to analyze gaps.")

# Distribution Page
elif page == "📤 Distribution":
    st.title("📤 Content Distribution")
    st.markdown("Track content distribution across platforms")
    
    st.info("Distribution monitoring - shows where content has been published")
    
    # Platform status
    st.subheader("Platform Status")
    
    platforms = [
        {'name': 'Dev.to', 'status': 'Ready', 'published': 0, 'pending': 0},
        {'name': 'Medium', 'status': 'Ready', 'published': 0, 'pending': 0},
        {'name': 'Twitter', 'status': 'Ready', 'published': 0, 'pending': 0},
        {'name': 'LinkedIn', 'status': 'Ready', 'published': 0, 'pending': 0},
    ]
    
    for platform in platforms:
        cols = st.columns([2, 1, 1, 1])
        
        with cols[0]:
            st.markdown(render_platform_badge(platform['name'].lower()), unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"<span class='status-success'>{platform['status']}</span>", unsafe_allow_html=True)
        
        with cols[2]:
            st.metric("Published", platform['published'])
        
        with cols[3]:
            st.metric("Pending", platform['pending'])

# Revenue Analytics Page
elif page == "💰 Revenue Analytics":
    st.title("💰 Revenue Analytics")
    st.markdown("Track earnings and conversion metrics")
    
    revenue_data = load_revenue_data()
    
    # Quick action
    if st.button("➕ Add Conversion", key="quick_add_conversion"):
        st.session_state.show_conversion_form = True
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            format_currency(revenue_data['total_revenue'])
        )
    
    with col2:
        st.metric(
            "Last 30 Days",
            format_currency(revenue_data['revenue_30d']),
            delta=format_currency(revenue_data['revenue_7d']) + " (7d)"
        )
    
    with col3:
        total_conversions = len(revenue_data['tracker'].conversions)
        st.metric("Total Conversions", format_number(total_conversions))
    
    with col4:
        avg_revenue = revenue_data['total_revenue'] / total_conversions if total_conversions > 0 else 0
        st.metric("Avg per Conversion", format_currency(avg_revenue))
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Revenue by Type")
        
        type_revenue = revenue_data['by_type']
        if type_revenue:
            for conv_type, data in sorted(type_revenue.items(), 
                                         key=lambda x: x[1]['revenue'], 
                                         reverse=True):
                st.markdown(f"**{conv_type.capitalize()}**")
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    revenue = data['revenue']
                    max_revenue = max(d['revenue'] for d in type_revenue.values())
                    progress = revenue / max_revenue if max_revenue > 0 else 0
                    st.progress(progress)
                
                with cols[1]:
                    st.markdown(f"**{format_currency(revenue)}**")
                
                with cols[2]:
                    st.caption(f"{data['conversions']} conv.")
        else:
            st.info("No revenue data by type available.")
    
    with col2:
        st.subheader("📊 Revenue by Platform")
        
        platform_revenue = revenue_data['by_platform']
        if platform_revenue:
            for platform, data in sorted(platform_revenue.items(), 
                                        key=lambda x: x[1]['revenue'], 
                                        reverse=True):
                st.markdown(render_platform_badge(platform), unsafe_allow_html=True)
                cols = st.columns([3, 1, 1])
                
                with cols[0]:
                    revenue = data['revenue']
                    max_revenue = max(d['revenue'] for d in platform_revenue.values())
                    progress = revenue / max_revenue if max_revenue > 0 else 0
                    st.progress(progress)
                
                with cols[1]:
                    st.markdown(f"**{format_currency(revenue)}**")
                
                with cols[2]:
                    st.caption(f"{data['conversions']} conv.")
        else:
            st.info("No revenue data by platform available.")
    
    st.markdown("---")
    
    # Top performing content
    st.subheader("🏆 Top Performing Content")
    
    top_content = revenue_data['top_content']
    if top_content:
        for i, content in enumerate(top_content[:10], 1):
            with st.expander(f"{i}. {content.get('content_title', 'Untitled')}"):
                cols = st.columns([2, 1, 1, 1])
                
                with cols[0]:
                    st.markdown(render_platform_badge(content.get('platform', 'unknown')), 
                               unsafe_allow_html=True)
                
                with cols[1]:
                    st.metric("Revenue", format_currency(content.get('total_revenue', 0)))
                
                with cols[2]:
                    st.metric("Conversions", content.get('total_conversions', 0))
                
                with cols[3]:
                    avg = content.get('total_revenue', 0) / max(content.get('total_conversions', 1), 1)
                    st.metric("Avg/Conv", format_currency(avg))
    else:
        st.info("No revenue data available yet. Add conversions via Control Panel.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Content Resonance Amplifier - Control Center v2.0</p>
        <p>Mode: <strong>{st.session_state.system_mode.upper()}</strong> | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)