"""Smart Website Scanner Page for GOVNEXIS.

Enforces:
- Target ownership & authorization verification
- SSRF-safe scanning with loopback & private destination blocks
- Multi-phase audit progress visualization
- Immediate transparent scoring and finding breakdown
- Instant multi-format report exports (PDF, HTML, JSON, CSV)
"""

import time
import streamlit as st
from urllib.parse import urlparse

from core.config import LOCAL_DEMO_URL, LOCAL_DEMO_HOST, LOCAL_DEMO_PORT
from core.scanner import execute_scan, ScanResult, ScanError
from core.url_validator import ValidationError, SSRFSecurityError
from core.database import save_scan
from core.reports import generate_json_report, generate_html_report, generate_csv_report, generate_pdf_report
from ui.theme import render_brand_header, get_status_badge_html, get_severity_badge_html, render_safe_html


def render_scanner_page():
    """Render the Smart Website Scanner UI."""
    render_brand_header("Defensive Security Configuration Auditing Engine")

    # Scope and Legal Pre-flight Notice
    render_safe_html("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #1e293b; border-left: 4px solid #06b6d4; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-weight: 700; color: #38bdf8; font-size: 0.9rem;">DEFENSIVE CONFIGURATION AUDIT ONLY</div>
        <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.5; margin-top: 4px;">
            GOVNEXIS inspects public HTTP response headers, cookie flags, and TLS connection parameters.
            It performs no port scanning, brute force attacks, or destructive testing. 
            Scanning requires verified authorization from the website owner or administering agency.
        </div>
    </div>
    """)

    # Fast Preset Buttons
    col_pre1, col_pre2, _ = st.columns([1.5, 1.5, 2])
    with col_pre1:
        if st.button("🧪 Auto-fill Local Demo Target", use_container_width=True):
            st.session_state["scan_input_url"] = LOCAL_DEMO_URL
            st.session_state["scan_auth_checked"] = True
    with col_pre2:
        if st.button("🏛️ Auto-fill Public Example", use_container_width=True):
            st.session_state["scan_input_url"] = "https://example.gov"
            st.session_state["scan_auth_checked"] = True

    default_url = st.session_state.get("scan_input_url", "")
    default_auth = st.session_state.get("scan_auth_checked", False)

    # Scan Form
    with st.form("scan_execution_form"):
        col_url, col_scheme = st.columns([3, 1])

        with col_url:
            target_url = st.text_input(
                "Website Target URL",
                value=default_url,
                placeholder="https://agency.example.gov or 127.0.0.1:8765",
                help="Enter full URL or domain. HTTP or HTTPS schemes only."
            )

        with col_scheme:
            # Scheme indicator
            is_https = target_url.lower().startswith("https://")
            scheme_badge = "🔒 HTTPS (Encrypted)" if is_https else "⚠️ HTTP (Plaintext)" if target_url else "— Awaiting URL"
            st.text_input("Protocol Scheme", value=scheme_badge, disabled=True)

        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

        # Mandatory Authorization Checkbox
        auth_confirmed = st.checkbox(
            "I certify that I am the authorized website owner, administrator, or have explicit written permission to audit this endpoint.",
            value=default_auth,
            help="Mandatory authorization confirmation required before any network traffic is dispatched."
        )

        submit_scan = st.form_submit_button("🔍 Start Security Audit", type="primary", use_container_width=True)

    # Execution Handler
    if submit_scan:
        if not target_url.strip():
            st.error("Please enter a valid website URL to audit.")
            return

        if not auth_confirmed:
            st.error("❌ Scan halted: You must certify authorization before proceeding.")
            return

        # Determine if this is local demo
        allow_demo = False
        parsed_target = urlparse(target_url if target_url.startswith(("http://", "https://")) else "https://" + target_url)
        if parsed_target.hostname in ("127.0.0.1", "localhost") and parsed_target.port == LOCAL_DEMO_PORT:
            allow_demo = True

        progress_placeholder = st.empty()
        status_text = st.empty()

        try:
            # Step-by-step progress simulation with real execution
            progress_bar = progress_placeholder.progress(10)
            status_text.caption("Phase 1/5: Validating URL syntax, scheme, and SSRF restrictions...")
            time.sleep(0.15)

            progress_bar.progress(35)
            status_text.caption("Phase 2/5: Resolving DNS hostnames and verifying destination network ranges...")
            time.sleep(0.15)

            progress_bar.progress(60)
            status_text.caption("Phase 3/5: Dispatching defensive HTTP requests & inspecting TLS parameters...")

            # Run actual scan
            scan_result = execute_scan(
                target_url=target_url,
                user_confirmed_authorization=True,
                allow_local_demo=allow_demo
            )

            progress_bar.progress(85)
            status_text.caption("Phase 4/5: Running 10 security configuration audit rules...")
            time.sleep(0.15)

            progress_bar.progress(100)
            status_text.caption("Phase 5/5: Calculating transparent score & persisting audit record...")

            # Persist to database
            scan_id = save_scan(scan_result)
            st.session_state["latest_scan_result"] = scan_result
            st.session_state["latest_scan_id"] = scan_id

            progress_placeholder.empty()
            status_text.empty()
            st.success(f"Audit completed successfully! Scan record #{scan_id} saved.")

        except SSRFSecurityError as e:
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"🛡️ **Security Policy Enforcement**: {str(e)}")
            st.info("Tip: GOVNEXIS blocks internal IPs (10.x, 192.168.x, 127.x) to protect against Server-Side Request Forgery. Use the Local Demo Lab for sandbox testing.")
            return
        except ValidationError as e:
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"⚠️ **Validation Error**: {str(e)}")
            return
        except ScanError as e:
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"🚨 **Scan Error**: {e.message}")
            if e.technical_details:
                st.caption(f"Technical details: {e.technical_details}")
            if e.remediation_hint:
                st.info(f"Troubleshooting guidance: {e.remediation_hint}")
            return
        except Exception as e:
            progress_placeholder.empty()
            status_text.empty()
            st.error(f"An unexpected scan failure occurred: {str(e)}")
            return

    # Render results if available in session
    if "latest_scan_result" in st.session_state:
        res: ScanResult = st.session_state["latest_scan_result"]
        render_scan_results(res)


def render_scan_results(res: ScanResult):
    """Render the full interactive audit results view."""
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    score = res.score_report.final_score
    grade = res.score_report.letter_grade
    score_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 60 else "#ef4444")

    # Score Overview Banner
    col_score, col_meta = st.columns([1.2, 2.8])

    with col_score:
        render_safe_html(f"""
        <div style="background: #0f172a; border: 2px solid {score_color}; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
            <div style="font-size: 0.8rem; text-transform: uppercase; color: #94a3b8; font-weight: 600;">SECURITY SCORE</div>
            <div style="font-size: 3.2rem; font-weight: 900; color: {score_color}; line-height: 1.1;">{score}</div>
            <div style="font-size: 1.2rem; font-weight: 800; color: {score_color}; margin-top: 4px;">GRADE: {grade}</div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 8px;">Transparent CISA/NIST Metric</div>
        </div>
        """)

    with col_meta:
        pass_count = sum(1 for f in res.findings if f.status == "PASS")
        fail_count = sum(1 for f in res.findings if f.status == "FAIL")
        warn_count = sum(1 for f in res.findings if f.status == "WARNING")

        render_safe_html(f"""
        <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 12px;">
                <span style="font-weight: 700; color: #f8fafc; font-size: 1.1rem;">Target: {res.hostname}</span>
                <span style="font-size: 0.8rem; color: #94a3b8;">Duration: {res.duration_ms} ms</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center;">
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px;">
                    <div style="font-size: 1.4rem; font-weight: 800; color: #34d399;">{pass_count}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">CHECKS PASSED</div>
                </div>
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 10px;">
                    <div style="font-size: 1.4rem; font-weight: 800; color: #f87171;">{fail_count}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">CHECKS FAILED</div>
                </div>
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 10px;">
                    <div style="font-size: 1.4rem; font-weight: 800; color: #fbbf24;">{warn_count}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">WARNINGS</div>
                </div>
            </div>
            <div style="margin-top: 12px; font-size: 0.8rem; color: #94a3b8;">
                <strong>Destination URL:</strong> <code>{res.final_url}</code> (HTTP {res.status_code})
            </div>
        </div>
        """)

    # Export Report Toolbar
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📥 Export Assessment Report")
    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

    scan_dict = res.to_dict()

    with exp_col1:
        pdf_bytes = generate_pdf_report(scan_dict)
        st.download_button(
            "📄 Export PDF",
            data=pdf_bytes,
            file_name=f"GOVNEXIS-Audit-{res.hostname}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with exp_col2:
        html_str = generate_html_report(scan_dict)
        st.download_button(
            "🌐 Export HTML",
            data=html_str,
            file_name=f"GOVNEXIS-Audit-{res.hostname}.html",
            mime="text/html",
            use_container_width=True
        )

    with exp_col3:
        json_str = generate_json_report(scan_dict)
        st.download_button(
            "📦 Export JSON",
            data=json_str,
            file_name=f"GOVNEXIS-Audit-{res.hostname}.json",
            mime="application/json",
            use_container_width=True
        )

    with exp_col4:
        csv_str = generate_csv_report(scan_dict)
        st.download_button(
            "📊 Export CSV",
            data=csv_str,
            file_name=f"GOVNEXIS-Audit-{res.hostname}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Detailed Findings Accordion
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📋 Evaluated Security Configuration Checks")

    for f in res.findings:
        status_pill = get_status_badge_html(f.status)
        sev_pill = get_severity_badge_html(f.severity)

        with st.expander(f"{f.status} — {f.title} ({f.severity})"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Category:** `{f.category}` | **Status:** {status_pill} | **Severity:** {sev_pill}", unsafe_allow_html=True)
                st.markdown(f"**Observed Evidence:**")
                st.code(f.evidence, language="http")
                st.markdown(f"**Why It Matters:** {f.why_it_matters}")
                st.markdown(f"**Potential Adversary Impact:** {f.potential_impact}")
                st.markdown(f"**Recommended Action:** {f.recommended_action}")
            with c2:
                st.markdown("**References & Standards:**")
                for r in f.references:
                    st.markdown(f"- [{r['title']}]({r['url']})")
                st.caption(f"Audit confidence: {f.confidence}")
