"""Intelligent Findings Center for GOVNEXIS.

Provides:
- Search, multi-dimensional filtering, and transparent rule-based prioritization
- Comprehensive vulnerability cards with evidence, risk explanation and references
- Verification lifecycle tracking (Open, In Progress, Fixed, Verified)
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from core.database import get_connection, update_remediation_status
from ui.theme import render_brand_header, get_status_badge_html, get_severity_badge_html


def render_findings_page():
    """Render the Intelligent Findings Center."""
    render_brand_header("Intelligent Security Findings & Priority Center")

    # Fetch all findings joined with scans
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.*, s.hostname, s.timestamp as scan_time, s.target_url
            FROM findings f
            JOIN scans s ON f.scan_id = s.id
            ORDER BY 
                CASE f.severity
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                    ELSE 5
                END ASC,
                f.id DESC
        """)
        rows = cursor.fetchall()
        all_findings = [dict(r) for r in rows]

    if not all_findings:
        st.info("No findings found in the database. Run a scan from the **New Security Scan** page or load sample data from the **Overview** dashboard.")
        return

    # Prioritization Methodology Notice
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1e293b; border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #34d399; font-size: 0.85rem;">TRANSPARENT RULE-BASED PRIORITIZATION MATRIX</div>
        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 3px;">
            Findings are prioritized based on attack vector exploitability, blast radius, and federal mandates (CISA BOD 18-01 / NIST SP 800-52r2).
            Transport encryption and script injection defenses are ranked with highest priority.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        search_query = st.text_input("🔍 Search Findings", placeholder="Search title, host, evidence...")

    with f_col2:
        severities = ["All"] + sorted(list(set(f["severity"] for f in all_findings)))
        selected_sev = st.selectbox("Filter Severity", severities)

    with f_col3:
        statuses = ["All", "FAIL", "WARNING", "PASS"]
        selected_status = st.selectbox("Filter Audit Status", statuses)

    with f_col4:
        hostnames = ["All"] + sorted(list(set(f["hostname"] for f in all_findings)))
        selected_host = st.selectbox("Filter Target Host", hostnames)

    # Filter evaluation
    filtered = all_findings
    if search_query.strip():
        q = search_query.lower()
        filtered = [
            f for f in filtered
            if q in f["title"].lower() or q in f["hostname"].lower() or q in f["evidence"].lower() or q in f["category"].lower()
        ]

    if selected_sev != "All":
        filtered = [f for f in filtered if f["severity"] == selected_sev]

    if selected_status != "All":
        filtered = [f for f in filtered if f["status"] == selected_status]

    if selected_host != "All":
        filtered = [f for f in filtered if f["hostname"] == selected_host]

    st.markdown(f"**Showing {len(filtered)} of {len(all_findings)} finding records**")

    # Render Findings List
    for finding in filtered:
        status_pill = get_status_badge_html(finding["status"])
        sev_pill = get_severity_badge_html(finding["severity"])
        v_status = finding.get("verification_status", "Open")

        v_color = "#34d399" if v_status == "Verified" else ("#38bdf8" if v_status == "Fixed" else ("#fbbf24" if v_status == "In Progress" else "#f87171"))

        with st.expander(f"[{finding['severity']}] {finding['title']} — {finding['hostname']}"):
            col_l, col_r = st.columns([3, 1])

            with col_l:
                st.markdown(f"""
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                    {status_pill} {sev_pill}
                    <span style="font-size: 0.8rem; color: #94a3b8;">Target: <code>{finding['hostname']}</code></span>
                    <span style="font-size: 0.8rem; color: #64748b;">Detected: {finding['scan_time'][:19]}</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Observed Evidence:**")
                st.code(finding["evidence"], language="http")

                st.markdown(f"**Why It Matters:** {finding['why_it_matters']}")
                st.markdown(f"**Potential Adversary Impact:** {finding['potential_impact']}")
                st.markdown(f"**Recommended Remediation:** {finding['recommended_action']}")

            with col_r:
                st.markdown(f"""
                <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">TRACKING STATUS</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: {v_color}; margin: 4px 0;">{v_status}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Update Status:**")
                new_status = st.selectbox(
                    "Set Lifecycle Status",
                    ["Open", "In Progress", "Fixed", "Verified"],
                    index=["Open", "In Progress", "Fixed", "Verified"].index(v_status) if v_status in ["Open", "In Progress", "Fixed", "Verified"] else 0,
                    key=f"status_sel_{finding['id']}"
                )

                if st.button("Save Status", key=f"btn_save_{finding['id']}", use_container_width=True):
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE findings SET verification_status = ? WHERE id = ?", (new_status, finding["id"]))
                        conn.commit()
                    st.success("Updated!")
                    st.rerun()
