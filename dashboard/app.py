import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Ensure src modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analytics import DB_PATH
from src.agent import RealDynamicAIAgent, format_formal_label

st.set_page_config(
    page_title="State Education Dept. — Student Retention & Welfare Efficacy Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Advanced Ultra-Modern Glassmorphic Modern Website Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Hide Streamlit default sidebar for full website layout */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 35%),
                    radial-gradient(circle at 85% 85%, rgba(168, 85, 247, 0.08) 0%, transparent 35%),
                    #050814;
        color: #f8fafc;
    }
    
    /* Modern Website Header Top Bar */
    .website-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(20px) saturate(190%);
        -webkit-backdrop-filter: blur(20px) saturate(190%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 18px 28px;
        margin-bottom: 20px;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.6);
        position: relative;
    }
    
    .website-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
        background: linear-gradient(90deg, #38bdf8, #8b5cf6, #10b981, #f43f5e);
    }
    
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-top: 4px;
        margin-bottom: 0;
        font-weight: 400;
    }
    
    .header-badge {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Modern Website Navigation Bar Styling (Top Radio Pills) */
    .stRadio > div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 8px 12px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5) !important;
    }

    .stRadio > div[role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        cursor: pointer !important;
        white-space: nowrap !important;
    }

    .stRadio > div[role="radiogroup"] label:hover {
        color: #f8fafc !important;
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }

    .stRadio > div[role="radiogroup"] label[data-checked="true"],
    .stRadio > div[role="radiogroup"] div[aria-checked="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        color: #38bdf8 !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25) !important;
    }

    /* Top Global Filter Container */
    .filter-panel {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 14px 20px;
        margin-bottom: 24px;
    }

    /* Hero Page Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.65) 100%);
        backdrop-filter: blur(20px) saturate(190%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px 26px;
        margin-bottom: 22px;
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.5);
    }
    
    .hero-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-top: 5px;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Glassmorphic Metric Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 18px;
    }
    
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 35px -8px rgba(56, 189, 248, 0.25);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    .glass-card-title {
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .glass-card-value {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .glass-card-subtext {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Streamlit Default Container Polish */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5) !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }

    /* Primary Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: white !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 20px rgba(2, 132, 199, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    return duckdb.connect(DB_PATH, read_only=True)

conn = get_db_connection()

# Modern Website Header Brand Banner
st.markdown("""
<div class="website-header">
    <div>
        <div class="brand-title">🎓 State Education Dept. portal</div>
        <div class="brand-subtitle">Student Retention & Welfare Efficacy Intelligence System</div>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
        <span class="header-badge">Governed DuckDB Warehouse</span>
        <span class="header-badge" style="background: rgba(139, 92, 246, 0.12); border-color: rgba(139, 92, 246, 0.3); color: #a855f7;">Gemini 3.6 AI Engine</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Website Navigation Bar
nav_page = st.radio(
    "Website Navigation Bar",
    [
        "1. Executive Command Center",
        "2. Attendance Intelligence",
        "3. MDM Procurement Intelligence",
        "4. Infrastructure & Amenities",
        "5. FLN Learning Outcomes",
        "6. Welfare & Retention Risk Tracker",
        "7. Real Gemini AI Agent"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# Global Administrative Filter Controls
districts_list = ['All Districts'] + conn.execute("SELECT DISTINCT district FROM dim_school WHERE district IS NOT NULL ORDER BY district").df()['district'].tolist()
school_types = ['All Types'] + conn.execute("SELECT DISTINCT school_type FROM dim_school WHERE school_type IS NOT NULL ORDER BY school_type").df()['school_type'].tolist()

with st.container():
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        selected_district = st.selectbox("🌐 Filter District Name", districts_list, key="top_district_select")
    with f_col2:
        selected_type = st.selectbox("🏫 Filter School Type / Level", school_types, key="top_type_select")
    with f_col3:
        st.markdown(f"""
        <div style="margin-top: 24px; padding: 8px 16px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px;">
            <span style="color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Active Filter Scope:</span> &nbsp;
            <span style="color: #38bdf8; font-weight: 700; font-size: 0.88rem;">📍 {selected_district}</span> &nbsp;|&nbsp; 
            <span style="color: #a855f7; font-weight: 700; font-size: 0.88rem;">🏫 {selected_type}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def get_filter_clause(table_alias="s"):
    clauses = []
    if selected_district != 'All Districts':
        clauses.append(f"{table_alias}.district = '{selected_district}'")
    if selected_type != 'All Types':
        clauses.append(f"{table_alias}.school_type = '{selected_type}'")
    if clauses:
        return "WHERE " + " AND ".join(clauses)
    return ""

filter_clause = get_filter_clause("s")

def render_hero_banner(title, subtitle):
    st.markdown(f"""
    <div class="hero-banner">
        <h2 class="hero-title">{title}</h2>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_glass_card(title, value, subtext="", accent_color="#38bdf8"):
    st.markdown(f"""
    <div class="glass-card" style="border-top: 3px solid {accent_color};">
        <div class="glass-card-title">{title}</div>
        <div class="glass-card-value" style="color: {accent_color};">{value}</div>
        <div class="glass-card-subtext">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

# Smart Comparative Plotly Scaling & Formatting Helper
def style_plotly_figure(fig, df=None, y_cols=None, is_horizontal=False):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=12, color="#cbd5e1"),
        margin=dict(l=50, r=40, t=80, b=50),
        title=dict(
            font=dict(size=14, color="#f8fafc", family="Plus Jakarta Sans, sans-serif"),
            x=0.0,
            xanchor='left',
            y=0.98,
            yanchor='top'
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)', showgrid=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1.0,
            title_text="",
            bgcolor='rgba(15, 23, 42, 0.7)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1
        )
    )

    # Dynamic comparative Y-axis / X-axis range padding for clear contrast
    if df is not None and not df.empty:
        if y_cols is None:
            y_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        
        if y_cols:
            vals = []
            for c in y_cols:
                if c in df.columns:
                    vals.extend(df[c].dropna().tolist())
            if vals:
                min_v, max_v = min(vals), max(vals)
                diff = max_v - min_v
                padding = max(diff * 0.25, max_v * 0.05) if diff > 0 else (max_v * 0.1 if max_v != 0 else 1.0)
                lower_b = max(0, min_v - padding) if min_v >= 0 else min_v - padding
                upper_b = max_v + padding
                
                if is_horizontal:
                    fig.update_layout(xaxis=dict(range=[lower_b, upper_b]))
                else:
                    fig.update_layout(yaxis=dict(range=[lower_b, upper_b]))

    # Only set cliponaxis on bar/line/scatter traces (not pie traces)
    fig.for_each_trace(lambda t: t.update(cliponaxis=False) if hasattr(t, 'cliponaxis') and t.type in ['bar', 'scatter'] else None)
    return fig

# ==============================================================================
# PAGE 1: EXECUTIVE COMMAND CENTER
# ==============================================================================
if nav_page.startswith("1"):
    render_hero_banner(
        "📊 Executive Command Center",
        "Statewide administrative dashboard monitoring enrollment, attendance integrity, infrastructure health, and learning outcome efficacy."
    )

    kpi_query = f"""
    SELECT 
        COUNT(DISTINCT s.school_id) AS total_schools,
        SUM(s.total_enrolled_students) AS total_enrollment,
        AVG(att.avg_attendance_rate) AS overall_attendance,
        AVG(att.proxy_anomaly_rate) AS proxy_anomaly_rate,
        AVG(infra.infrastructure_deficit_pct) AS avg_infra_deficit,
        AVG(ts.avg_fln_score) AS avg_fln_score
    FROM dim_school s
    LEFT JOIN (
        SELECT school_id, 
               AVG(CASE WHEN data_quality_status = 'VALID' THEN attendance_rate END) AS avg_attendance_rate,
               (SUM(CASE WHEN is_proxy_attendance THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS proxy_anomaly_rate
        FROM fact_attendance GROUP BY school_id
    ) att ON s.school_id = att.school_id
    LEFT JOIN dim_infrastructure_current infra ON s.school_id = infra.school_id
    LEFT JOIN (
        SELECT school_id, AVG(score_percentage) AS avg_fln_score FROM fact_test_scores GROUP BY school_id
    ) ts ON s.school_id = ts.school_id
    {filter_clause};
    """
    kpi_df = conn.execute(kpi_query).df()
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_glass_card("Total Reporting Schools", f"{kpi_df['total_schools'].iloc[0]:,}", "Governed School Master", "#38bdf8")
    with c2:
        render_glass_card("Total Student Enrollment", f"{kpi_df['total_enrollment'].iloc[0]:,}", "Enrolled Students", "#8b5cf6")
    with c3:
        render_glass_card("Avg Daily Attendance Rate", f"{kpi_df['overall_attendance'].iloc[0]:.1f}%", "Validated Attendance", "#10b981")
    with c4:
        render_glass_card("Proxy Anomaly Rate", f"{kpi_df['proxy_anomaly_rate'].iloc[0]:.1f}%", "Sunday/Holiday Proxy Marking", "#f43f5e")
    with c5:
        render_glass_card("Infra Deficit Index", f"{kpi_df['avg_infra_deficit'].iloc[0]:.1f}%", "Missing Basic Amenities", "#f59e0b")
    with c6:
        render_glass_card("Avg FLN Test Score", f"{kpi_df['avg_fln_score'].iloc[0]:.1f}%", "Standardized Assessment", "#06b6d4")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("District Performance Comparison")
        dist_df = conn.execute(f"""
            SELECT district, AVG(avg_attendance_rate) AS att_rate, AVG(avg_fln_score) AS fln_score
            FROM vw_district_summary
            GROUP BY district ORDER BY att_rate DESC
        """).df()
        
        dist_df_plot = dist_df.rename(columns={
            'district': 'District Name',
            'att_rate': 'Average Daily Attendance Rate (%)',
            'fln_score': 'Average FLN Test Score (%)'
        })
        
        fig_dist = px.bar(
            dist_df_plot, x='District Name',
            y=['Average Daily Attendance Rate (%)', 'Average FLN Test Score (%)'],
            barmode='group',
            title="District Performance Audit: Attendance Rate vs FLN Test Score",
            labels={'value': 'Percentage Score (%)', 'variable': 'Indicator Metric'},
            color_discrete_sequence=['#38bdf8', '#10b981'],
            text_auto='.1f'
        )
        fig_dist.update_traces(textposition='outside', cliponaxis=False)
        st.plotly_chart(style_plotly_figure(fig_dist, dist_df_plot, ['Average Daily Attendance Rate (%)', 'Average FLN Test Score (%)']), width='stretch')

    with col2:
        st.subheader("Statewide Welfare Risk Distribution")
        risk_dist = conn.execute("SELECT welfare_risk_category, COUNT(*) AS school_count FROM fact_welfare_risk GROUP BY welfare_risk_category").df()
        risk_dist_plot = risk_dist.rename(columns={
            'welfare_risk_category': 'Welfare Risk Classification',
            'school_count': 'School Count'
        })
        
        fig_pie = px.pie(
            risk_dist_plot, names='Welfare Risk Classification', values='School Count',
            title="Statewide School Risk Profile Distribution",
            color='Welfare Risk Classification',
            color_discrete_map={'High Risk': '#ef4444', 'Moderate Risk': '#f59e0b', 'Low Risk': '#10b981'}
        )
        fig_pie.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(style_plotly_figure(fig_pie), width='stretch')

# ==============================================================================
# PAGE 2: ATTENDANCE INTELLIGENCE
# ==============================================================================
elif nav_page.startswith("2"):
    render_hero_banner(
        "📅 Attendance Intelligence & Proxy Marking Auditing",
        "Comprehensive auditing of daily student attendance logs, impossible attendance records (present > enrolled), and Sunday proxy marking anomalies."
    )

    att_stats = conn.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN is_impossible_attendance THEN 1 ELSE 0 END) AS imp, SUM(CASE WHEN is_proxy_attendance THEN 1 ELSE 0 END) AS proxy FROM fact_attendance").df()
    c1, c2, c3 = st.columns(3)
    with c1:
        render_glass_card("Total Attendance Audit Records", f"{att_stats['total'].iloc[0]:,}", "Processed Daily Logs", "#38bdf8")
    with c2:
        render_glass_card("Impossible Records (Present > Enrolled)", f"{att_stats['imp'].iloc[0]:,}", "Data Quality Violations", "#ef4444")
    with c3:
        render_glass_card("Sunday Proxy Marking Anomalies", f"{att_stats['proxy'].iloc[0]:,}", "100% Attendance on Sundays", "#f59e0b")

    st.markdown("---")
    m_trend = conn.execute("""
        SELECT 
            month, 
            AVG(avg_attendance_rate) AS avg_attendance_rate, 
            AVG(proxy_anomaly_rate_pct) AS proxy_anomaly_rate_pct 
        FROM vw_school_attendance_monthly 
        WHERE month IS NOT NULL 
        GROUP BY month 
        ORDER BY month
    """).df()
    
    m_trend_plot = m_trend.rename(columns={
        'month': 'Academic Month',
        'avg_attendance_rate': 'Average Daily Attendance Rate (%)',
        'proxy_anomaly_rate_pct': 'Proxy Attendance Anomaly Rate (%)'
    })

    col1, col2 = st.columns(2)
    with col1:
        fig_m = px.line(
            m_trend_plot, x='Academic Month', y='Average Daily Attendance Rate (%)',
            title="Statewide Monthly Attendance Rate Trend", markers=True
        )
        fig_m.update_traces(
            line_color='#38bdf8', 
            line_width=3, 
            marker=dict(size=8, color='#0284c7'),
            hovertemplate='<b>%{x}</b><br>Attendance Rate: %{y:.1f}%<extra></extra>'
        )
        st.plotly_chart(style_plotly_figure(fig_m, m_trend_plot, ['Average Daily Attendance Rate (%)']), width='stretch')

    with col2:
        fig_p = px.line(
            m_trend_plot, x='Academic Month', y='Proxy Attendance Anomaly Rate (%)',
            title="Statewide Monthly Proxy Anomaly Rate Trend", markers=True
        )
        fig_p.update_traces(
            line_color='#f43f5e', 
            line_width=3, 
            marker=dict(size=8, color='#ef4444'),
            hovertemplate='<b>%{x}</b><br>Proxy Anomaly Rate: %{y:.1f}%<extra></extra>'
        )
        st.plotly_chart(style_plotly_figure(fig_p, m_trend_plot, ['Proxy Attendance Anomaly Rate (%)']), width='stretch')

    st.subheader("Top Anomalous School Records (Sunday 100% Proxy Attendance)")
    proxy_df = conn.execute("""
        SELECT school_id, school_name, district, attendance_date, present_students, total_students, marked_by
        FROM vw_school_attendance_daily
        WHERE is_proxy_attendance = TRUE
        ORDER BY attendance_date DESC LIMIT 20
    """).df()
    
    proxy_df.columns = [format_formal_label(c) for c in proxy_df.columns]
    st.dataframe(proxy_df, width='stretch')

# ==============================================================================
# PAGE 3: MDM PROCUREMENT INTELLIGENCE
# ==============================================================================
elif nav_page.startswith("3"):
    render_hero_banner(
        "🍲 Mid-Day Meal Procurement Intelligence",
        "Standardized food grain procurement analytics, supplier expenditure rankings, commodity mix breakdown, and unit cost efficiency metrics."
    )

    mdm_kpi = conn.execute("SELECT SUM(quantity_kg) AS tot_kg, SUM(total_cost) AS tot_cost, AVG(cost_per_kg) AS avg_cpk FROM fact_mdm_procurement").df()
    c1, c2, c3 = st.columns(3)
    with c1:
        render_glass_card("Total Procurement Volume (KG)", f"{mdm_kpi['tot_kg'].iloc[0]:,.1f} KG", "Standardized Food Grain", "#10b981")
    with c2:
        render_glass_card("Total Supplier Expenditure (₹)", f"₹{mdm_kpi['tot_cost'].iloc[0]:,.2f}", "Cleaned Currency Costs", "#8b5cf6")
    with c3:
        render_glass_card("Average Unit Cost Efficiency (₹/KG)", f"₹{mdm_kpi['avg_cpk'].iloc[0]:,.2f}/KG", "Procurement Cost Metric", "#06b6d4")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        v_df = conn.execute("SELECT vendor_name, SUM(total_cost) AS total_cost FROM vw_school_mdm_summary GROUP BY vendor_name ORDER BY total_cost DESC").df()
        v_df_plot = v_df.rename(columns={
            'vendor_name': 'MDM Supplier Entity Name',
            'total_cost': 'Total Procurement Expenditure (₹)'
        })
        fig_v = px.bar(
            v_df_plot, x='MDM Supplier Entity Name', y='Total Procurement Expenditure (₹)',
            title="Total Expenditure by MDM Supplier Entity", color='Total Procurement Expenditure (₹)',
            color_continuous_scale='Viridis',
            text_auto=',.0f'
        )
        fig_v.update_traces(texttemplate='₹%{y:,.0f}', textposition='outside', cliponaxis=False)
        st.plotly_chart(style_plotly_figure(fig_v, v_df_plot, ['Total Procurement Expenditure (₹)']), width='stretch')

    with col2:
        g_df = conn.execute("SELECT grain_type, SUM(quantity_kg) AS total_kg FROM vw_school_mdm_summary GROUP BY grain_type ORDER BY total_kg DESC").df()
        g_df_plot = g_df.rename(columns={
            'grain_type': 'Food Grain Commodity',
            'total_kg': 'Total Procurement Volume (KG)'
        })
        fig_g = px.pie(
            g_df_plot, names='Food Grain Commodity', values='Total Procurement Volume (KG)',
            title="Procurement Volume Distribution by Commodity", color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_g.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(style_plotly_figure(fig_g), width='stretch')

# ==============================================================================
# PAGE 4: INFRASTRUCTURE & AMENITIES
# ==============================================================================
elif nav_page.startswith("4"):
    render_hero_banner(
        "🏫 Infrastructure & Amenity Deficit Tracker",
        "Auditing five basic school amenities (Electricity, Safe Drinking Water, Functional Toilets, Boundary Wall, Playground) across districts."
    )

    inf_kpi = conn.execute("""
        SELECT 
            AVG(CASE WHEN has_electricity THEN 1.0 ELSE 0.0 END)*100 AS elec,
            AVG(CASE WHEN has_drinking_water THEN 1.0 ELSE 0.0 END)*100 AS water,
            AVG(CASE WHEN has_functional_toilet THEN 1.0 ELSE 0.0 END)*100 AS toilet,
            AVG(CASE WHEN has_boundary_wall THEN 1.0 ELSE 0.0 END)*100 AS wall,
            AVG(CASE WHEN has_playground THEN 1.0 ELSE 0.0 END)*100 AS play
        FROM dim_infrastructure_current
    """).df()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_glass_card("Electricity Availability", f"{inf_kpi['elec'].iloc[0]:.1f}%", "Functional Power", "#38bdf8")
    with c2:
        render_glass_card("Drinking Water", f"{inf_kpi['water'].iloc[0]:.1f}%", "Safe Water Source", "#06b6d4")
    with c3:
        render_glass_card("Functional Toilet", f"{inf_kpi['toilet'].iloc[0]:.1f}%", "Sanitation Access", "#10b981")
    with c4:
        render_glass_card("Boundary Wall Security", f"{inf_kpi['wall'].iloc[0]:.1f}%", "Perimeter Wall", "#8b5cf6")
    with c5:
        render_glass_card("Playground Facility", f"{inf_kpi['play'].iloc[0]:.1f}%", "Sports Facility", "#f59e0b")

    st.markdown("---")
    d_inf = conn.execute("SELECT district, AVG(infrastructure_deficit_pct) AS deficit FROM vw_school_infrastructure_summary GROUP BY district ORDER BY deficit DESC").df()
    d_inf_plot = d_inf.rename(columns={
        'district': 'District Name',
        'deficit': 'Infrastructure Deficit Index (%)'
    })
    fig_def = px.bar(
        d_inf_plot, x='District Name', y='Infrastructure Deficit Index (%)',
        title="District Infrastructure Deficit Index Ranking (%)", color='Infrastructure Deficit Index (%)',
        color_continuous_scale='Reds',
        text_auto='.1f'
    )
    fig_def.update_traces(texttemplate='%{y:.1f}%', textposition='outside', cliponaxis=False)
    st.plotly_chart(style_plotly_figure(fig_def, d_inf_plot, ['Infrastructure Deficit Index (%)']), width='stretch')

# ==============================================================================
# PAGE 5: FLN LEARNING OUTCOMES
# ==============================================================================
elif nav_page.startswith("5"):
    render_hero_banner(
        "🎓 Foundational Literacy & Numeracy (FLN) Learning Outcomes",
        "Performance metrics evaluated across 8,000 FLN assessments standardized into percentage learning scores."
    )

    fln_kpi = conn.execute("SELECT AVG(score_percentage) AS avg_score, COUNT(*) AS total_tests FROM fact_test_scores").df()
    c1, c2 = st.columns(2)
    with c1:
        render_glass_card("Statewide Average FLN Test Score", f"{fln_kpi['avg_score'].iloc[0]:.1f}%", "Standardized Percentage Score", "#38bdf8")
    with c2:
        render_glass_card("Total Assessments Evaluated", f"{fln_kpi['total_tests'].iloc[0]:,}", "Ingested Test Records", "#8b5cf6")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        sub_df = conn.execute("SELECT subject, AVG(score_percentage) AS avg_score FROM vw_school_test_summary GROUP BY subject ORDER BY avg_score DESC").df()
        sub_df_plot = sub_df.rename(columns={
            'subject': 'Academic Subject',
            'avg_score': 'Average FLN Test Score (%)'
        })
        fig_sub = px.bar(
            sub_df_plot, x='Academic Subject', y='Average FLN Test Score (%)',
            title="Average Standardized FLN Score by Academic Subject", color='Average FLN Test Score (%)',
            color_continuous_scale='Blues',
            text_auto='.1f'
        )
        fig_sub.update_traces(texttemplate='%{y:.1f}%', textposition='outside', cliponaxis=False)
        st.plotly_chart(style_plotly_figure(fig_sub, sub_df_plot, ['Average FLN Test Score (%)']), width='stretch')

    with col2:
        gr_df = conn.execute("SELECT grade, AVG(score_percentage) AS avg_score FROM vw_school_test_summary GROUP BY grade ORDER BY avg_score DESC").df()
        gr_df_plot = gr_df.rename(columns={
            'grade': 'Grade / Class Level',
            'avg_score': 'Average FLN Test Score (%)'
        })
        fig_gr = px.bar(
            gr_df_plot, x='Grade / Class Level', y='Average FLN Test Score (%)',
            title="Average Standardized FLN Score by Grade Level", color='Average FLN Test Score (%)',
            color_continuous_scale='Greens',
            text_auto='.1f'
        )
        fig_gr.update_traces(texttemplate='%{y:.1f}%', textposition='outside', cliponaxis=False)
        st.plotly_chart(style_plotly_figure(fig_gr, gr_df_plot, ['Average FLN Test Score (%)']), width='stretch')

# ==============================================================================
# PAGE 6: WELFARE & RETENTION RISK TRACKER
# ==============================================================================
elif nav_page.startswith("6"):
    render_hero_banner(
        "⚠️ Welfare & Retention Risk Tracker Engine",
        "Decision-support multi-factor index combining attendance risk, learning outcome gaps, infrastructure deficits, and data integrity anomalies."
    )

    risk_df = conn.execute("SELECT * FROM fact_welfare_risk ORDER BY welfare_risk_score DESC").df()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_glass_card("High Risk Schools Count", f"{(risk_df['welfare_risk_category']=='High Risk').sum()}", "Risk Score ≥ 70", "#ef4444")
    with c2:
        render_glass_card("Moderate Risk Schools Count", f"{(risk_df['welfare_risk_category']=='Moderate Risk').sum()}", "Risk Score 40-69", "#f59e0b")
    with c3:
        render_glass_card("Low Risk Schools Count", f"{(risk_df['welfare_risk_category']=='Low Risk').sum()}", "Risk Score < 40", "#10b981")

    st.markdown("---")
    st.subheader("Priority Action Table: High Risk Schools Requiring Departmental Intervention")
    
    formatted_risk_df = risk_df[['school_id', 'school_name', 'district', 'block', 'welfare_risk_score', 'welfare_risk_category', 'avg_attendance_rate', 'avg_fln_score', 'infrastructure_deficit_pct']].copy()
    formatted_risk_df.columns = [format_formal_label(c) for c in formatted_risk_df.columns]
    
    st.dataframe(formatted_risk_df, width='stretch')

# ==============================================================================
# PAGE 7: REAL GEMINI AI AGENT
# ==============================================================================
elif nav_page.startswith("7"):
    render_hero_banner(
        "🤖 Real AI Agent — Live Data Intelligence",
        "Powered by Generative AI (Gemini 3.6 Flash). Translates natural language questions into live SQL queries, executes queries live, generates Plotly graphs, and writes executive summaries."
    )

    agent = RealDynamicAIAgent(conn=conn)

    if 'current_query' not in st.session_state:
        st.session_state.current_query = "How many total students are enrolled in each district?"

    st.markdown("#### Sample Audit Questions:")
    sample_cols = st.columns(4)
    if sample_cols[0].button("👥 Enrollment by District"):
        st.session_state.current_query = "How many total students are enrolled in each district?"
    if sample_cols[1].button("🚨 Sunday Attendance Anomalies"):
        st.session_state.current_query = "Which schools reported 100% attendance on Sundays?"
    if sample_cols[2].button("⚡ Electricity vs Test Scores"):
        st.session_state.current_query = "Compare average test scores between schools with and without functional electricity."
    if sample_cols[3].button("🍲 MDM Cost by Vendor"):
        st.session_state.current_query = "Show total MDM procurement cost by vendor."

    user_input = st.text_input(
        "Type your question for the AI Agent:",
        value=st.session_state.current_query,
        key="query_text_input"
    )

    if st.button("Run Live AI Query", type="primary"):
        with st.spinner("Gemini 3.6 Flash AI Engine introspecting query, translating to DuckDB SQL, and rendering live graphics..."):
            res = agent.process_query(user_input)

        if res['status'] == 'SUCCESS':
            st.success("Query Executed Successfully against Governed DuckDB Database via Gemini AI Engine.")
            
            st.markdown("### Executive AI Narrative Analysis")
            st.markdown(res['summary'])

            if res['chart'] is not None:
                st.plotly_chart(style_plotly_figure(res['chart']), width='stretch')

            if res['data'] is not None:
                st.subheader("Formally Labeled Governed Data Result")
                st.dataframe(res['data'], width='stretch')

            with st.expander("Inspect Live Executed DuckDB SQL Query"):
                st.code(res['sql'], language='sql')
        else:
            st.warning(res['summary'])
