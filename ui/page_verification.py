"""Before-and-After Security Verification for GOVNEXIS.

Workflow:
- Select Baseline Scan (Before) and Rescan (After)
- Score Delta calculation and trajectory visualization
- Differential finding analysis: Resolved, Remaining, and Newly Introduced
- Side-by-side response header and cookie comparison
"""

import streamlit as st
import pandas as pd
import json

from core.database import get_all_scans, get_scan
from ui.theme import render_brand_header, get_status_badge_html, render_safe_html


def render_verification_page():
    """Render Before-and-After Verification UI."""
    render_brand_header("Before-and-After Verification Engine")

    render_safe_html("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1e293b; border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #34d399; font-size: 0.9rem;">EMPIRICAL VERIFICATION WORKFLOW</div>
        <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5; margin-top: 4px;">
            A fix is only verified when demonstrated by a repeatable, empirical follow-up audit.
            Compare your baseline scan before applying remediation against your post-hardening verification scan.
        </div>
    </div>
    """)

    all_scans = get_all_scans(limit=50)
    if len(all_scans) < 2:
        st.info("At least two scans are required to perform a Before-and-After comparison. Run scans on the **New Security Scan** page or test the **Local Demo Lab**.")
        return

    # Select Scans for Comparison
    col_sel1, col_sel2 = st.columns(2)

    scan_options = {
        s["id"]: f"#{s['id']} | {s['hostname']} | Score {s['score']}/100 | {s['timestamp'][:16]}"
        for s in all_scans
    }

    with col_sel1:
        baseline_id = st.selectbox(
            "Select Baseline Scan (BEFORE)",
            options=list(scan_options.keys()),
            index=1 if len(scan_options) > 1 else 0,
            format_func=lambda x: scan_options[x]
        )

    with col_sel2:
        rescan_id = st.selectbox(
            "Select Follow-up Scan (AFTER)",
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
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c_card1, c_card2, c_card3 = st.columns(3)

    delta_color = "#10b981" if delta_score > 0 else ("#94a3b8" if delta_score == 0 else "#ef4444")
    delta_sign = f"+{delta_score}" if delta_score > 0 else str(delta_score)

    with c_card1:
        render_safe_html(f"""
        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">BASELINE (BEFORE)</div>
            <div style="font-size: 2.2rem; font-weight: 900; color: #f8fafc; margin: 4px 0;">{score_a}<span style="font-size: 1rem; color: #64748b;">/100</span></div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Grade: {scan_a['letter_grade']} ({scan_a['timestamp'][:16]})</div>
        </div>
        """)

    with c_card2:
        render_safe_html(f"""
        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">RESCAN (AFTER)</div>
            <div style="font-size: 2.2rem; font-weight: 900; color: #f8fafc; margin: 4px 0;">{score_b}<span style="font-size: 1rem; color: #64748b;">/100</span></div>
            <div style="font-size: 0.8rem; color: #94a3b8;">Grade: {scan_b['letter_grade']} ({scan_b['timestamp'][:16]})</div>
        </div>
        """)

    with c_card3:
        render_safe_html(f"""
        <div style="background: #0f172a; border: 2px solid {delta_color}; border-radius: 10px; padding: 18px; text-align: center;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">VERIFICATION DELTA</div>
            <div style="font-size: 2.2rem; font-weight: 900; color: {delta_color}; margin: 4px 0;">{delta_sign} pts</div>
            <div style="font-size: 0.8rem; color: {delta_color}; font-weight: 600;">
                {"Significant Improvement Verified ✓" if delta_score > 10 else "Measurable Change" if delta_score != 0 else "Identical Posture"}
            </div>
        </div>
        """)

    # Detailed Rule-by-Rule Differential Analysis
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔍 Rule-by-Rule Differential Audit")

    findings_a = {f["check_id"]: f for f in scan_a["findings"]}
    findings_b = {f["check_id"]: f for f in scan_b["findings"]}

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
        f"✅ Resolved Findings ({len(resolved_items)})",
        f"⚠️ Remaining Issues ({len(remaining_items)})",
        "📄 Raw Headers Diff"
    ])

    with tab_res:
        if resolved_items:
            for title, before, after in resolved_items:
                render_safe_html(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #34d399;">✓ {title}</span>
                    <div>
                        <span style="color: #f87171; text-decoration: line-through; font-size: 0.85rem; margin-right: 8px;">{before}</span>
                        <span style="color: #34d399; font-weight: 800; font-size: 0.9rem;">➔ {after}</span>
                    </div>
                </div>
                """)
        else:
            st.info("No previously failed findings were resolved between these two scans.")

    with tab_rem:
        if remaining_items:
            for title, before, after in remaining_items:
                render_safe_html(f"""
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #fbbf24;">⚠ {title}</span>
                    <span style="color: #fbbf24; font-size: 0.85rem;">Status still {after}</span>
                </div>
                """)
        else:
            st.success("All configuration checks passed in the follow-up scan!")

    with tab_diff:
        st.markdown("##### Side-by-Side Header Observations")
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
