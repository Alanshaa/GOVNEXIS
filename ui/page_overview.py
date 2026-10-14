"""Overview Dashboard for GOVNEXIS.

Displays aggregate security metrics derived from actual stored scan data:
- Summary KPI cards (total scans, total findings, average score, resolved)
- Severity distribution chart
- Category breakdown chart
- Scan activity timeline
- Top recurring issues
- Recent scan table
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.database import get_scan_trends, get_all_scans
from ui.theme import (
    render_page_header,
    render_safe_html,
    render_metric_card_html,
    get_score_color,
    get_tokens,
    get_plotly_layout_defaults,
    get_severity_color_map,
)


def render_overview_page():
    """Render the executive security overview dashboard."""
    render_page_header(
        "Overview",
        "Aggregate security posture across all audited targets.",
    )

    trends = get_scan_trends()
    t = get_tokens()

    # ---- Empty state ----
    if trends["total_scans"] == 0:
        st.info(
            "No scan data yet. Run a scan from **New Scan** or try the "
            "**Demo Lab** to see results here."
        )
        return

    # ---- KPI cards ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_safe_html(render_metric_card_html(
            "Total Scans", str(trends["total_scans"]), "Stored audit records"
        ))
    with col2:
        render_safe_html(render_metric_card_html(
            "Unique Targets", str(trends["unique_targets"]), "Distinct hostnames"
        ))
    with col3:
        avg_score = trends["avg_score"]
        color = get_score_color(int(avg_score))
        render_safe_html(f"""
        <div class="gn-metric">
            <div class="gn-metric-label">Average Score</div>
            <div class="gn-metric-value" style="color:{color};">
                {avg_score}<span style="font-size:0.9rem; color:{t['text_muted']};">/100</span>
            </div>
            <div class="gn-metric-sub">Across all scans</div>
        </div>
        """)
    with col4:
        render_safe_html(render_metric_card_html(
            "Resolved", str(trends["resolved_count"]), "Fixed or verified"
        ))

    st.markdown("")

    # ---- Row 1: Severity distribution + Category breakdown ----
    chart_layout = get_plotly_layout_defaults()
    sev_colors = get_severity_color_map()

    donut_col, bar_col = st.columns(2)

    with donut_col:
        st.markdown("##### Findings by Severity")
        sev_counts = trends["severity_counts"]
        sev_df = pd.DataFrame([
            {"Severity": sev, "Count": sev_counts.get(sev, 0)}
            for sev in ("Critical", "High", "Medium", "Low", "Informational")
        ])
        total_findings = sev_df["Count"].sum()

        if total_findings > 0:
            fig_sev = px.pie(
                sev_df, names="Severity", values="Count", hole=0.55,
                color="Severity", color_discrete_map=sev_colors,
            )
            fig_sev.update_traces(
                textposition="inside", textinfo="percent+label",
                marker=dict(line=dict(color=t["bg"], width=2)),
            )
            fig_sev.update_layout(
                **chart_layout,
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5, font=dict(size=11),
                ),
                height=280,
                annotations=[{
                    "text": f"<b>{total_findings}</b><br><span style='font-size:10px;color:{t['text_muted']};'>FINDINGS</span>",
                    "x": 0.5, "y": 0.5,
                    "font": {"size": 16, "color": t["text_primary"]},
                    "showarrow": False,
                }],
            )
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("No active findings detected.")

    with bar_col:
        st.markdown("##### Findings by Category")
        cat_counts = trends["category_counts"]
        if cat_counts:
            cat_df = pd.DataFrame([
                {"Category": cat, "Findings": count}
                for cat, count in cat_counts.items()
            ]).head(8)
            fig_cat = px.bar(
                cat_df, x="Findings", y="Category", orientation="h",
                color_discrete_sequence=[t["accent"]],
            )
            fig_cat.update_layout(
                **chart_layout,
                margin=dict(t=10, b=10, l=10, r=10),
                yaxis=dict(categoryorder="total ascending",
                           tickfont=dict(size=11, color=t["chart_text"])),
                xaxis=dict(showgrid=True, gridcolor=t["chart_grid"]),
                height=280,
                showlegend=False,
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available yet.")

    st.markdown("")

    # ---- Row 2: Activity timeline + Top issues ----
    time_col, issues_col = st.columns([1.3, 1])

    with time_col:
        st.markdown("##### Scan Activity and Score Trend")
        activity = trends["activity_over_time"]
        if activity:
            act_df = pd.DataFrame(activity)
            fig_act = go.Figure()

            fig_act.add_trace(go.Bar(
                x=act_df["scan_date"], y=act_df["count"],
                name="Scans", yaxis="y",
                marker=dict(color=t["accent_secondary"], opacity=0.5),
            ))
            fig_act.add_trace(go.Scatter(
                x=act_df["scan_date"], y=act_df["avg_score"],
                name="Score", yaxis="y2",
                line=dict(color=t["accent"], width=2.5),
                mode="lines+markers",
                marker=dict(size=6, color=t["accent"]),
            ))
            fig_act.update_layout(
                **chart_layout,
                margin=dict(t=15, b=10, l=10, r=10),
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.25,
                    xanchor="center", x=0.5, font=dict(size=11),
                ),
                yaxis=dict(title="Scans", showgrid=False,
                           tickfont=dict(color=t["chart_text"])),
                yaxis2=dict(
                    title="Score (0-100)", overlaying="y", side="right",
                    range=[0, 105], showgrid=True,
                    gridcolor=t["chart_grid"],
                    tickfont=dict(color=t["accent"]),
                ),
                xaxis=dict(showgrid=False, tickfont=dict(color=t["chart_text"])),
                height=280,
            )
            st.plotly_chart(fig_act, use_container_width=True)
        else:
            st.info("No scan activity data yet.")

    with issues_col:
        st.markdown("##### Top Recurring Issues")
        top_issues = trends["top_issues"]
        if top_issues:
            for item in top_issues:
                render_safe_html(f"""
                <div class="gn-finding-row">
                    <div>
                        <div class="gn-finding-title">{item['title']}</div>
                        <div class="gn-finding-meta">{item['category']}</div>
                    </div>
                    <div>
                        <span class="gn-badge gn-badge-fail">{item['occurrences']} affected</span>
                    </div>
                </div>
                """)
        else:
            st.info("No recurring issues found.")

    # ---- Recent scans table ----
    st.markdown("")
    st.markdown("##### Recent Audit Records")
    scans = get_all_scans(limit=6)
    if scans:
        rows = []
        for s in scans:
            rows.append({
                "Target": s["hostname"],
                "Timestamp": s["timestamp"][:19],
                "Score": f"{s['score']}/100 ({s['letter_grade']})",
                "HTTP": str(s["status_code"]),
                "Pass / Fail / Warn": (
                    f"{s['passed_checks']} / {s['failed_checks']} / {s['warning_checks']}"
                ),
                "Type": "Local Demo" if s["is_demo"] else "External",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
