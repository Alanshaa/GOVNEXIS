"""Local Demo Lab for GOVNEXIS.

Provides an interactive sandbox environment for live Hackathon demonstrations:
- Controls local test HTTP server on 127.0.0.1:8765
- Demonstrates Baseline (vulnerable/misconfigured) vs Hardened states
- One-click scan, remediation fix application, rescan, and comparative verification
- Controlled sandbox banner isolating demonstration traffic
"""

import streamlit as st
import time

from core.config import LOCAL_DEMO_URL, LOCAL_DEMO_HOST, LOCAL_DEMO_PORT
from core.mock_site import start_mock_server, stop_mock_server, get_demo_status, DEMO_STATE, MockServerState
from core.scanner import execute_scan
from core.database import save_scan
from ui.theme import render_brand_header, render_demo_banner, get_status_badge_html, render_safe_html


def render_demo_lab_page():
    """Render the Local Demo Lab sandbox page."""
    render_brand_header("Local Demo Lab — Interactive Hackathon Sandbox")
    render_demo_banner()

    # Ensure demo server is started
    server_started = start_mock_server()
    status = get_demo_status()

    # Status Panel
    col_st1, col_st2, col_st3 = st.columns(3)

    with col_st1:
        render_safe_html(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">SANDBOX SERVER STATUS</div>
            <div class="gov-metric-value" style="color: {'#10b981' if status['running'] else '#ef4444'}; font-size: 1.4rem;">
                {'● ONLINE' if status['running'] else '○ OFFLINE'}
            </div>
            <div class="gov-metric-delta">Bound to {status['host']}:{status['port']}</div>
        </div>
        """)

    with col_st2:
        mode_text = status['mode'].upper()
        mode_color = "#34d399" if status['mode'] == MockServerState.MODE_HARDENED else "#f87171"
        render_safe_html(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">CURRENT SIMULATION STATE</div>
            <div class="gov-metric-value" style="color: {mode_color}; font-size: 1.4rem;">
                {mode_text}
            </div>
            <div class="gov-metric-delta">
                {'Hardened Defense Posture' if status['mode'] == MockServerState.MODE_HARDENED else 'Vulnerable Baseline Posture'}
            </div>
        </div>
        """)

    with col_st3:
        render_safe_html(f"""
        <div class="gov-metric-card">
            <div class="gov-metric-title">TARGET URL</div>
            <div class="gov-metric-value" style="font-size: 1.2rem; color: #38bdf8;">
                {status['url']}
            </div>
            <div class="gov-metric-delta">Safe localhost allowlist</div>
        </div>
        """)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Action Buttons
    st.markdown("### 🎮 Hackathon Demo Controls")
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)

    with b_col1:
        if st.button("1️⃣ Run Baseline Demo Scan", use_container_width=True, type="primary"):
            DEMO_STATE.set_mode(MockServerState.MODE_BASELINE)
            with st.spinner("Running Baseline security audit on local sandbox..."):
                time.sleep(0.3)
                res = execute_scan(
                    target_url=LOCAL_DEMO_URL,
                    user_confirmed_authorization=True,
                    allow_local_demo=True
                )
                scan_id = save_scan(res)
                st.session_state["demo_baseline_scan"] = res
                st.session_state["latest_scan_result"] = res
                st.success(f"Baseline scan completed! Score: {res.score_report.final_score}/100")
                st.rerun()

    with b_col2:
        if st.button("2️⃣ Apply Demo Fixes (Harden)", use_container_width=True):
            DEMO_STATE.set_mode(MockServerState.MODE_HARDENED)
            st.success("Config applied: Hardened headers (HSTS, CSP, XFO, XCTO, secure cookies) enabled on local demo server!")
            st.rerun()

    with b_col3:
        if st.button("3️⃣ Rescan Hardened Demo", use_container_width=True, type="primary"):
            DEMO_STATE.set_mode(MockServerState.MODE_HARDENED)
            with st.spinner("Executing post-hardening verification audit..."):
                time.sleep(0.3)
                res = execute_scan(
                    target_url=LOCAL_DEMO_URL,
                    user_confirmed_authorization=True,
                    allow_local_demo=True
                )
                scan_id = save_scan(res)
                st.session_state["demo_hardened_scan"] = res
                st.session_state["latest_scan_result"] = res
                st.success(f"Verification scan completed! Score: {res.score_report.final_score}/100")
                st.rerun()

    with b_col4:
        if st.button("🔄 Reset Demo to Baseline", use_container_width=True):
            DEMO_STATE.set_mode(MockServerState.MODE_BASELINE)
            st.info("Demo server reset to Baseline (Misconfigured) state.")
            st.rerun()

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Live Before & After Verification in the Lab
    has_baseline = "demo_baseline_scan" in st.session_state
    has_hardened = "demo_hardened_scan" in st.session_state

    if has_baseline or has_hardened:
        st.markdown("### 📊 Demo Scan Results")

        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.markdown("#### Baseline Result (Before)")
            if has_baseline:
                b_res = st.session_state["demo_baseline_scan"]
                b_score = b_res.score_report.final_score
                render_safe_html(f"""
                <div style="background: #0f172a; border: 2px solid #ef4444; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">BASELINE SCORE</div>
                    <div style="font-size: 2.4rem; font-weight: 900; color: #ef4444;">{b_score}/100 (Grade {b_res.score_report.letter_grade})</div>
                    <div style="font-size: 0.8rem; color: #f87171;">Critical gaps: Missing HSTS, CSP, XFO, weak session cookie</div>
                </div>
                """)
                for f in b_res.findings:
                    if f.status in ("FAIL", "WARNING"):
                        st.caption(f"✕ {f.title}: {f.evidence[:60]}")
            else:
                st.info("Click '1️⃣ Run Baseline Demo Scan' above to record the baseline state.")

        with res_col2:
            st.markdown("#### Hardened Result (After)")
            if has_hardened:
                h_res = st.session_state["demo_hardened_scan"]
                h_score = h_res.score_report.final_score
                render_safe_html(f"""
                <div style="background: #0f172a; border: 2px solid #10b981; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">VERIFIED SCORE</div>
                    <div style="font-size: 2.4rem; font-weight: 900; color: #10b981;">{h_score}/100 (Grade {h_res.score_report.letter_grade})</div>
                    <div style="font-size: 0.8rem; color: #34d399;">Defense-in-depth verified: All headers & secure cookies active</div>
                </div>
                """)
                for f in h_res.findings:
                    if f.status == "PASS":
                        st.caption(f"✓ {f.title}")
            else:
                st.info("Click '2️⃣ Apply Demo Fixes' then '3️⃣ Rescan Hardened Demo' to observe verification.")

        if has_baseline and has_hardened:
            delta = st.session_state["demo_hardened_scan"].score_report.final_score - st.session_state["demo_baseline_scan"].score_report.final_score
            st.success(f"🎉 **Live Verification Demonstrated**: Security posture improved by **+{delta} points** in the local sandbox!")
