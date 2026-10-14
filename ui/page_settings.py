"""Settings, Methodology and Guided Help for GOVNEXIS.

Contains:
- Product identity, mission statement, and core architecture
- Theme & appearance preferences
- Transparent scoring methodology and check weights reference table
- Guided troubleshooting for common network and TLS failure modes
- Legal authorization notice and defensive auditing disclaimers
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from core.config import (
    APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_CATEGORY, APP_VERSION,
    CHECK_WEIGHTS
)
from ui.theme import (
    render_page_header,
    render_safe_html,
    get_current_theme,
    set_theme,
    get_tokens,
    THEME_DARK,
    THEME_LIGHT,
)


def render_settings_page() -> None:
    """Render Settings, Methodology and Guided Help page."""
    render_page_header(
        "Settings & Documentation",
        "System architecture, transparent scoring methodology, and guided troubleshooting",
    )
    tokens = get_tokens()
    current_theme = get_current_theme()

    tab_about, tab_theme, tab_scoring, tab_help, tab_legal = st.tabs([
        "About GOVNEXIS",
        "Theme & Appearance",
        "Scoring Methodology",
        "Guided Troubleshooting",
        "Legal & Ethical Notice",
    ])

    with tab_about:
        st.subheader(f"{APP_NAME} — {APP_CATEGORY}")
        st.markdown(f"> *\"{APP_TAGLINE}\"*")
        st.markdown(f"**Description:** {APP_DESCRIPTION}")

        st.markdown("""
        #### Core Capabilities
        1. **Passive Defense-Only Auditing**: Evaluates public HTTP response headers, cookie attributes, and TLS protocol observations without invasive payloads.
        2. **Transparent Scoring**: Deterministic 0–100 scale grounded directly in federal and international standards (CISA BOD 18-01, NIST SP 800-52r2, OWASP).
        3. **Remediation Knowledge Base**: Actionable configuration playbooks for Nginx, Apache, Caddy, Node.js, and Python.
        4. **Empirical Before-and-After Verification**: Side-by-side verification proving that remediations genuinely resolved configuration gaps.
        5. **Isolated Local Demo Lab**: Safe sandbox test harness on `127.0.0.1:8765` for hackathon evaluation and air-gapped testing.
        """)

        st.divider()
        st.caption(f"GOVNEXIS Core Engine v{APP_VERSION} | Python 3 | SQLite 3 | Streamlit")

    with tab_theme:
        st.subheader("Appearance & Design System")
        st.markdown("GOVNEXIS supports dark and light modes. Your preference is persisted across browser refreshes and sessions.")

        col_t1, col_t2 = st.columns([2, 2])
        with col_t1:
            theme_choice = st.radio(
                "Interface Theme",
                [THEME_DARK, THEME_LIGHT],
                index=0 if current_theme == THEME_DARK else 1,
                format_func=lambda x: f"Dark Mode ({x.title()})" if x == THEME_DARK else f"Light Mode ({x.title()})",
                horizontal=True
            )
            if theme_choice != current_theme:
                set_theme(theme_choice)
                st.rerun()

        with col_t2:
            st.markdown(f"""
            <div style="background: {tokens['surface']}; border: 1px solid {tokens['border']}; border-radius: 6px; padding: 12px 16px;">
                <div style="font-size: 0.75rem; color: {tokens['text_muted']}; font-weight: 600; text-transform: uppercase;">Active Theme</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: {tokens['accent']}; margin: 4px 0;">{current_theme.upper()}</div>
                <div style="font-size: 0.8rem; color: {tokens['text_secondary']};">Tokens loaded from centralized design system</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Design Palette Tokens")
        token_rows = [
            {"Token": "Background", "Hex": tokens["bg"], "Description": "Main application canvas"},
            {"Token": "Surface", "Hex": tokens["surface"], "Description": "Card and container backgrounds"},
            {"Token": "Surface Elevated", "Hex": tokens["surface_elevated"], "Description": "Raised elements and inputs"},
            {"Token": "Primary Text", "Hex": tokens["text_primary"], "Description": "High contrast body and titles"},
            {"Token": "Secondary Text", "Hex": tokens["text_secondary"], "Description": "Descriptions and secondary content"},
            {"Token": "Borders", "Hex": tokens["border"], "Description": "Subtle structural separators"},
            {"Token": "Primary Accent", "Hex": tokens["accent"], "Description": "Muted emerald for primary actions"},
            {"Token": "Secondary Accent", "Hex": tokens["accent_teal"], "Description": "Restrained teal for secondary highlights"},
            {"Token": "Warning", "Hex": tokens["warning"], "Description": "Amber warning indicators"},
            {"Token": "Error", "Hex": tokens["error"], "Description": "Accessible muted red failure indicators"},
        ]
        st.dataframe(pd.DataFrame(token_rows), use_container_width=True, hide_index=True)

    with tab_scoring:
        st.subheader("Transparent Scoring Methodology")
        st.markdown("""
        GOVNEXIS scores website security configurations deterministically out of **100 points**.
        The algorithm applies the following rules:
        - **PASS**: Awards 100% of the assigned check weight.
        - **WARNING**: Awards 50% partial credit (50% penalty for incomplete or weak configuration).
        - **FAIL**: Awards 0 points (100% penalty).
        - **NOT ASSESSED**: Excluded from the scoring denominator.
        """)

        weights_data = []
        for cid, meta in CHECK_WEIGHTS.items():
            weights_data.append({
                "Check Rule": meta["title"],
                "Category": meta["category"],
                "Assigned Weight": f"{meta['weight']} pts",
                "Severity on Fail": meta["severity_on_fail"],
                "Scope": meta["description"],
            })

        st.dataframe(pd.DataFrame(weights_data), use_container_width=True, hide_index=True)

        st.info("Independent Risk Visibility: High and Critical findings remain prominently visible in executive reports regardless of the numerical score.")

    with tab_help:
        st.subheader("Guided Troubleshooting & Plain-English Error Help")
        st.markdown("If an audit scan fails to complete, refer to the diagnostic guide below:")

        errors = [
            {
                "Issue": "DNS Resolution Failure",
                "Plain English": "The domain name could not be resolved to an IP address.",
                "Action": "Check spelling of the domain. Verify the domain is publicly registered and active in DNS."
            },
            {
                "Issue": "Connection Timed Out",
                "Plain English": "The server did not respond to initial TCP connection requests within 5.0 seconds.",
                "Action": "Ensure the web server is running and port 80/443 is open. Check if an external firewall is dropping requests."
            },
            {
                "Issue": "SSRF / Destination Blocked",
                "Plain English": "The URL resolved to a loopback, private (RFC 1918), or reserved IP address.",
                "Action": "GOVNEXIS blocks scans against internal infrastructure to protect against SSRF. For sandbox testing, use the designated Local Demo Lab."
            },
            {
                "Issue": "TLS / SSL Handshake Failure",
                "Plain English": "The server's TLS certificate is invalid, expired, self-signed, or the server rejects HTTPS.",
                "Action": "Verify that a valid CA-signed certificate is installed and bound to port 443."
            },
            {
                "Issue": "Too Many Redirects (>5)",
                "Plain English": "The URL initiated a circular or excessively long chain of HTTP redirects.",
                "Action": "Audit server redirect rules (e.g. infinite HTTP to HTTPS loop caused by reverse proxy misconfiguration)."
            }
        ]

        for e in errors:
            with st.expander(e["Issue"]):
                st.markdown(f"**What Happened:** {e['Plain English']}")
                st.markdown(f"**Recommended Action:** {e['Action']}")

    with tab_legal:
        st.subheader("Legal Authorization & Ethical Assessment Notice")
        st.markdown("""
        **Notice of Intended Use:**
        GOVNEXIS is developed strictly as a defensive auditing and educational platform. 
        It is intended solely for authorized system administrators, security officers, and website owners 
        evaluating their own public web infrastructure.

        **Protective Constraints:**
        - No intrusive port scans, vulnerability exploits, or brute-force tests are performed.
        - Users must explicitly certify ownership or written permission prior to scanning.
        - All external scans enforce rate limits, strict timeouts, and SSRF destination filters.
        """)
