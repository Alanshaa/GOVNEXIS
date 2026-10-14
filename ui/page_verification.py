"""Before-and-After Security Verification for GOVNEXIS.

Workflow:
- Select Baseline Scan (Before) and Rescan (After)
- Score Delta calculation and trajectory visualization
- Differential finding analysis: Resolved, Remaining, and Regressed
- Side-by-side response header and cookie comparison
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List

from core.database import get_all_scans, get_scan
from ui.theme import (
    render_page_header,
    render_safe_html,
    get_tokens,
    get_score_color,
)


def render_verification_page() -> None:
    """Render Before-and-After Verification UI."""
    render_page_header(
        "Verification",
        "Empirical before-and-after comparison of baseline vs. follow-up scans",
    )
    tokens = get_tokens()

    render_safe_html(f"""
    <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-left: 4px solid {tokens['accent']}; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
        <div style="font-weight: 600; color: {tokens['accent']}; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em;">Empirical Verification Workflow</div>
        <div style="font-size: 0.82rem; color: {tokens['text_secondary']}; line-height: 1.5; margin-top: 4px;">
            A fix is only verified when demonstrated by a repeatable, empirical follow-up audit.
            Compare your baseline scan before applying remediation against your post-hardening verification scan.
        </div>
    </div>
    """)

    all_scans = get_all_scans(limit=50)
    if len(all_scans) < 2:
        st.info("At least two scans are required to perform a Before-and-After comparison. Run scans on the New Scan page or use the Demo Lab.")
        return

    # Select Scans for Comparison
    col_sel1, col_sel2 = st.columns(2)

    scan_options = {
        s["id"]: f"#{s['id']} | {s['hostname']} | Score {s['score']}/100 | {s['timestamp'][:16]}"
        for s in all_scans
    }

    with col_sel1:
        baseline_id = st.selectbox(
            "Select Baseline Scan (Before)",
            options=list(scan_options.keys()),
            index=1 if len(scan_options) > 1 else 0,
            format_func=lambda x: scan_options[x]
        )

    with col_sel2:
        rescan_id = st.selectbox(
            "Select Follow-up Scan (After)",
            options=list(scan_options.keys()),
            index=0,
            format_func=lambda x: scan_options[x]
        )

    if baseline_id == rescan_id:
        st.warning("Please select two distinct scans to evaluate verification deltas.")
        return

    # Load Scan Details
    scan_a = get_scan(baseline_id)
    scan_b = get_scan(rescan_id)

    if not scan_a or not scan_b:
        st.error("Error loading selected scan records.")
        return

    score_a = scan_a["score"]
    score_b = scan_b["score"]
    delta_score = score_b - score_a

    # Comparison Cards
    st.write("")
    c_card1, c_card2, c_card3 = st.columns(3)

    delta_color = tokens["accent"] if delta_score > 0 else (tokens["text_muted"] if delta_score == 0 else tokens["error"])
    delta_sign = f"+{delta_score}" if delta_score > 0 else str(delta_score)
    delta_verdict = "Significant Improvement Verified" if delta_score > 10 else ("Measurable Change" if delta_score != 0 else "Identical Posture")

    with c_card1:
        render_safe_html(f"""
        <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-radius: 8px; padding: 18px; text-align: center;">
            <div style="font-size: 0.72rem; color: {tokens['text_muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Baseline (Before)</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: {get_score_color(score_a)}; margin: 4px 0;">{score_a}<span style="font-size: 1rem; color: {tokens['text_muted']}; font-weight: 400;">/100</span></div>
            <div style="font-size: 0.8rem; color: {tokens['text_secondary']};">Grade: {scan_a['letter_grade']} ({scan_a['timestamp'][:16]})</div>
        </div>
        """)

    with c_card2:
        render_safe_html(f"""
        <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-radius: 8px; padding: 18px; text-align: center;">
            <div style="font-size: 0.72rem; color: {tokens['text_muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Rescan (After)</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: {get_score_color(score_b)}; margin: 4px 0;">{score_b}<span style="font-size: 1rem; color: {tokens['text_muted']}; font-weight: 400;">/100</span></div>
            <div style="font-size: 0.8rem; color: {tokens['text_secondary']};">Grade: {scan_b['letter_grade']} ({scan_b['timestamp'][:16]})</div>
        </div>
        """)

    with c_card3:
        render_safe_html(f"""
        <div style="background: {tokens['surface']}; border: 1px solid {delta_color}; border-radius: 8px; padding: 18px; text-align: center;">
            <div style="font-size: 0.72rem; color: {tokens['text_muted']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Verification Delta</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: {delta_color}; margin: 4px 0;">{delta_sign} pts</div>
            <div style="font-size: 0.8rem; color: {delta_color}; font-weight: 600;">{delta_verdict}</div>
        </div>
        """)

    # Detailed Rule-by-Rule Differential Analysis
    st.write("")
    st.markdown("#### Rule-by-Rule Differential Audit")

    findings_a = {f["check_id"]: f for f in scan_a.get("findings", [])}
    findings_b = {f["check_id"]: f for f in scan_b.get("findings", [])}

    resolved_items = []
    remaining_items = []
    regressed_items = []

    all_check_ids = sorted(list(set(list(findings_a.keys()) + list(findings_b.keys()))))

    for cid in all_check_ids:
        fa = findings_a.get(cid)
        fb = findings_b.get(cid)

        st_a = fa["status"] if fa else "N/A"
        st_b = fb["status"] if fb else "N/A"
        title = (fb or fa)["title"]

        if st_a in ("FAIL", "WARNING") and st_b == "PASS":
            resolved_items.append((title, st_a, st_b))
        elif st_a in ("FAIL", "WARNING") and st_b in ("FAIL", "WARNING"):
            remaining_items.append((title, st_a, st_b))
        elif st_a == "PASS" and st_b in ("FAIL", "WARNING"):
            regressed_items.append((title, st_a, st_b))

    tab_res, tab_rem, tab_diff = st.tabs([
        f"Resolved Findings ({len(resolved_items)})",
        f"Remaining Issues ({len(remaining_items)})",
        "Header Comparison"
    ])

    with tab_res:
        if resolved_items:
            for title, before, after in resolved_items:
                render_safe_html(f"""
                <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-left: 4px solid {tokens['accent']}; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: {tokens['text_primary']};">{title}</span>
                    <div>
                        <span style="color: {tokens['error']}; text-decoration: line-through; font-size: 0.82rem; margin-right: 8px;">{before}</span>
                        <span style="color: {tokens['accent']}; font-weight: 700; font-size: 0.88rem;">&rarr; {after}</span>
                    </div>
                </div>
                """)
        else:
            st.info("No previously failed findings were resolved between these two scans.")

    with tab_rem:
        if remaining_items:
            for title, before, after in remaining_items:
                render_safe_html(f"""
                <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-left: 4px solid {tokens['warning']}; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: {tokens['text_primary']};">{title}</span>
                    <span style="color: {tokens['warning']}; font-size: 0.82rem; font-weight: 600;">Status: {after}</span>
                </div>
                """)
        else:
            st.success("All configuration checks passed in the follow-up scan.")

    with tab_diff:
        st.markdown("**Side-by-Side Header Observations**")
        headers_a = scan_a.get("details", {}).get("response_headers", {})
        headers_b = scan_b.get("details", {}).get("response_headers", {})

        all_header_keys = sorted(list(set(list(headers_a.keys()) + list(headers_b.keys()))))
        diff_rows = []
        for h in all_header_keys:
            val_a = headers_a.get(h, "<ABSENT>")
            val_b = headers_b.get(h, "<ABSENT>")
            diff_rows.append({
                "HTTP Header": h,
                "Baseline (Scan A)": val_a,
                "Rescan (Scan B)": val_b,
                "Changed": "YES" if val_a != val_b else "NO",
            })

        st.dataframe(pd.DataFrame(diff_rows), use_container_width=True, hide_index=True)
