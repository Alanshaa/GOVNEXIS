"""Findings page for GOVNEXIS.

Provides:
- Search, multi-dimensional filtering, and rule-based prioritization
- Vulnerability details with evidence, risk explanation, and remediation guidance
- Verification lifecycle tracking (Open, In Progress, Fixed, Verified)
"""

import streamlit as st
from typing import List, Dict, Any

from core.database import get_connection
from ui.theme import (
    render_page_header,
    render_info_banner,
    get_status_badge_html,
    get_severity_badge_html,
    render_safe_html,
    get_tokens,
    get_verification_color,
)


def render_findings_page() -> None:
    """Render the Security Findings and Priority Center."""
    render_page_header(
        "Findings",
        "Search, filter, and track security findings across all audited targets",
    )
    tokens = get_tokens()

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
        st.info("No findings found in the database. Run a scan from the New Scan page or audit a target to populate results.")
        return

    # Prioritization Methodology Notice
    render_safe_html(f"""
    <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-left: 4px solid {tokens['accent']}; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
        <div style="font-weight: 600; color: {tokens['accent']}; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em;">Prioritization Methodology</div>
        <div style="font-size: 0.82rem; color: {tokens['text_secondary']}; margin-top: 4px; line-height: 1.5;">
            Findings are prioritized based on attack vector exploitability, blast radius, and federal mandates (CISA BOD 18-01 / NIST SP 800-52r2).
            Transport encryption, script injection defenses, and critical headers rank with highest priority.
        </div>
    </div>
    """)

    # Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        search_query = st.text_input("Search Findings", placeholder="Filter by title, host, category...")

    with f_col2:
        severities = ["All"] + sorted(list(set(f["severity"] for f in all_findings)))
        selected_sev = st.selectbox("Severity", severities)

    with f_col3:
        statuses = ["All", "FAIL", "WARNING", "PASS"]
        selected_status = st.selectbox("Audit Status", statuses)

    with f_col4:
        hostnames = ["All"] + sorted(list(set(f["hostname"] for f in all_findings)))
        selected_host = st.selectbox("Target Host", hostnames)

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

    st.markdown(f"<span style='font-size: 0.85rem; color: {tokens['text_muted']};'>Showing {len(filtered)} of {len(all_findings)} finding records</span>", unsafe_allow_html=True)
    st.write("")

    # Render Findings List
    for finding in filtered:
        status_pill = get_status_badge_html(finding["status"])
        sev_pill = get_severity_badge_html(finding["severity"])
        v_status = finding.get("verification_status", "Open")
        v_color = get_verification_color(v_status)

        expander_title = f"[{finding['severity']}] {finding['title']} — {finding['hostname']}"
        with st.expander(expander_title):
            col_l, col_r = st.columns([3, 1])

            with col_l:
                render_safe_html(f"""
                <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px; flex-wrap: wrap;">
                    {status_pill} {sev_pill}
                    <span style="font-size: 0.8rem; color: {tokens['text_secondary']};">Target: <code>{finding['hostname']}</code></span>
                    <span style="font-size: 0.8rem; color: {tokens['text_muted']};">Detected: {finding['scan_time'][:19]}</span>
                </div>
                """)

                st.markdown("**Observed Evidence**")
                st.code(finding["evidence"], language="http")

                st.markdown(f"**Why It Matters:** {finding['why_it_matters']}")
                st.markdown(f"**Potential Adversary Impact:** {finding['potential_impact']}")
                st.markdown(f"**Recommended Remediation:** {finding['recommended_action']}")

            with col_r:
                render_safe_html(f"""
                <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-radius: 6px; padding: 12px; margin-bottom: 12px;">
                    <div style="font-size: 0.72rem; color: {tokens['text_muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Lifecycle Status</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: {v_color}; margin: 4px 0;">{v_status}</div>
                </div>
                """)

                st.markdown("**Update Status**")
                options = ["Open", "In Progress", "Fixed", "Verified"]
                curr_idx = options.index(v_status) if v_status in options else 0
                new_status = st.selectbox(
                    "Set Status",
                    options,
                    index=curr_idx,
                    key=f"status_sel_{finding['id']}",
                    label_visibility="collapsed"
                )

                if st.button("Save", key=f"btn_save_{finding['id']}", use_container_width=True):
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE findings SET verification_status = ? WHERE id = ?", (new_status, finding["id"]))
                        conn.commit()
                    st.success("Status updated.")
                    st.rerun()
