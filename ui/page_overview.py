"""Executive Security Dashboard for GOVNEXIS.

Displays real metrics, aggregated audit statistics, and interactive Plotly charts:
- Total Scans & Authorized Target Count
- Active Findings by Severity
- Remediation Progress & Verified Resolutions
- Scan Timeline & Score Trajectory
- Top Configuration Vulnerabilities
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.database import get_scan_trends, get_all_scans, seed_demo_history
from ui.theme import render_brand_header, get_status_badge_html


def render_overview_page():
    """Render the executive security overview dashboard."""
    render_brand_header("Executive Web Security Configuration Auditing Dashboard")

    trends = get_scan_trends()
    total_scans = trends["total_scans"]

    # Onboarding screen if zero scans exist
    if total_scans == 0:
        st.info("👋 Welcome to **GOVNEXIS**. No security audit scans have been recorded in the database yet.")
        col_onboard1, col_onboard2 = st.columns([2, 1])
        with col_onboard1:
            st.markdown("""
            ### Quick Start Workflow
            1. **Run a Live Scan**: Head to **New Security Scan** in the navigation menu to audit an authorized government endpoint.
            2. **Test the Local Demo Lab**: Open **Local Demo Lab** to test a controlled, isolated website with intentional configuration gaps.
            3. **Review Remediation**: Explore **Remediation Lab** for production-ready web server configurations (Nginx, Apache, Caddy).
            """)
        with col_onboard2:
            st.markdown("### Hackathon Quick Demonstration")
            st.caption("Populate realistic historical demonstration records to explore the executive dashboard and charts immediately.")
            if st.button("🚀 Load Hackathon Sample Scans (Demo)", use_container_width=True, type="primary"):
                seed_demo_history()
                st.success("Loaded demonstration audit records! Refreshing...")
                st.rerun()
        return

    # Top Metric KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">TOTAL AUDIT SCANS</div>
            <div class="gov-metric-value">{trends['total_scans']}</div>
            <div class="gov-metric-delta">Persistent records</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">AUTHORIZED TARGETS</div>
            <div class="gov-metric-value">{trends['unique_targets']}</div>
            <div class="gov-metric-delta">Unique hostnames</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_score = trends["avg_score"]
        score_color = "#10b981" if avg_score >= 80 else ("#f59e0b" if avg_score >= 60 else "#ef4444")
        st.markdown(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">AVERAGE SECURITY SCORE</div>
            <div class="gov-metric-value" style="color: {score_color};">{avg_score}<span style="font-size: 1rem; color: #94a3b8;">/100</span></div>
            <div class="gov-metric-delta">Across all targets</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">RESOLVED / VERIFIED</div>
            <div class="gov-metric-value" style="color: #38bdf8;">{trends['resolved_count']}</div>
            <div class="gov-metric-delta">Remediated findings</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.markdown("##### 🎯 Active Findings by Severity")
        sev_counts = trends["severity_counts"]
        sev_df = pd.DataFrame([
            {"Severity": "Critical", "Count": sev_counts.get("Critical", 0), "Color": "#ef4444"},
            {"Severity": "High", "Count": sev_counts.get("High", 0), "Color": "#f97316"},
            {"Severity": "Medium", "Count": sev_counts.get("Medium", 0), "Color": "#eab308"},
            {"Severity": "Low", "Count": sev_counts.get("Low", 0), "Color": "#3b82f6"},
            {"Severity": "Informational", "Count": sev_counts.get("Informational", 0), "Color": "#64748b"},
        ])

        if sev_df["Count"].sum() > 0:
            fig_sev = px.pie(
                sev_df,
                names="Severity",
                values="Count",
                color="Severity",
                color_discrete_map={
                    "Critical": "#ef4444",
                    "High": "#f97316",
                    "Medium": "#eab308",
                    "Low": "#3b82f6",
                    "Informational": "#64748b",
                },
                hole=0.55
            )
            fig_sev.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#94a3b8"},
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                height=280,
            )
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("No active open findings recorded across targets.")

    with chart_col2:
        st.markdown("##### 🏷️ Findings by Security Category")
        cat_counts = trends["category_counts"]
        if cat_counts:
            cat_df = pd.DataFrame([
                {"Category": cat, "Findings": count}
                for cat, count in cat_counts.items()
            ]).head(6)

            fig_cat = px.bar(
                cat_df,
                x="Findings",
                y="Category",
                orientation="h",
                color="Findings",
                color_continuous_scale=["#06b6d4", "#10b981"],
            )
            fig_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#94a3b8"},
                margin=dict(t=10, b=10, l=10, r=10),
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                height=280,
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")

    # Timeline Chart & Top Issues
    time_col1, time_col2 = st.columns([1, 1])

    with time_col1:
        st.markdown("##### 📈 Scan Activity & Average Score Trajectory")
        activity = trends["activity_over_time"]
        if activity:
            act_df = pd.DataFrame(activity)
            fig_act = go.Figure()
            fig_act.add_trace(go.Bar(
                x=act_df["scan_date"],
                y=act_df["count"],
                name="Scans Performed",
                marker_color="#06b6d4",
                opacity=0.7,
                yaxis="y",
            ))
            fig_act.add_trace(go.Scatter(
                x=act_df["scan_date"],
                y=act_df["avg_score"],
                name="Avg Score",
                line=dict(color="#10b981", width=3),
                mode="lines+markers",
                yaxis="y2",
            ))
            fig_act.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#94a3b8"},
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                yaxis=dict(title="Scan Count", showgrid=False),
                yaxis2=dict(title="Score (0-100)", overlaying="y", side="right", range=[0, 100], showgrid=True, gridcolor="#1e293b"),
                height=260,
            )
            st.plotly_chart(fig_act, use_container_width=True)
        else:
            st.info("Timeline activity not yet populated.")

    with time_col2:
        st.markdown("##### 🚨 Top Recurring Configuration Issues")
        top_issues = trends["top_issues"]
        if top_issues:
            for item in top_issues:
                st.markdown(f"""
                <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;">{item['title']}</div>
                        <div style="font-size: 0.75rem; color: #64748b;">{item['category']}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;">
                            {item['occurrences']} sites affected
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recurring configuration issues identified.")

    # Recent Scans Table
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 🕒 Recent Audit Scan Log")
    scans = get_all_scans(limit=5)
    if scans:
        scan_records = []
        for s in scans:
            score = s["score"]
            score_badge = f"{score}/100 ({s['letter_grade']})"
            scan_records.append({
                "Target Hostname": s["hostname"],
                "Timestamp": s["timestamp"][:19],
                "Score": score_badge,
                "Status": f"{s['status_code']}",
                "Checks (P/F/W)": f"{s['passed_checks']} / {s['failed_checks']} / {s['warning_checks']}",
                "Type": "Local Demo" if s["is_demo"] else "Authorized External",
            })
        st.dataframe(pd.DataFrame(scan_records), use_container_width=True, hide_index=True)
