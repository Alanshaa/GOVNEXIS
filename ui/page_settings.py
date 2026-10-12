"""Settings, Methodology and Guided Help for GOVNEXIS.

Contains:
- Product identity, mission statement, and core architecture
- Transparent scoring methodology and check weights reference table
- Guided troubleshooting for common network and TLS failure modes
- Legal authorization notice and defensive auditing disclaimers
"""

import streamlit as st
import pandas as pd

from core.config import (
    APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_CATEGORY, APP_VERSION,
    CHECK_WEIGHTS
)
from ui.theme import render_brand_header


def render_settings_page():
    """Render Settings, Methodology and Guided Help page."""
    render_brand_header("System Architecture, Methodology & Guided Help")

    tab_about, tab_scoring, tab_help, tab_legal = st.tabs([
        "🛡️ About GOVNEXIS",
        "⚖️ Transparent Scoring Model",
        "❓ Guided Error Help",
        "📜 Legal & Authorization Notice"
    ])

    with tab_about:
        st.markdown(f"### {APP_NAME} — {APP_CATEGORY}")
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

        st.markdown("---")
        st.caption(f"GOVNEXIS Core Engine v{APP_VERSION} | Python 3 | SQLite 3 | Streamlit")

    with tab_scoring:
        st.markdown("### Transparent Scoring Methodology")
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

        st.info("ℹ️ **Independent Risk Visibility**: High and Critical findings remain prominently visible in executive reports regardless of the numerical score.")

    with tab_help:
        st.markdown("### Guided Troubleshooting & Plain-English Error Help")
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
            with st.expander(f"⚠️ {e['Issue']}"):
                st.markdown(f"**What Happened:** {e['Plain English']}")
                st.markdown(f"**Recommended Action:** {e['Action']}")

    with tab_legal:
        st.markdown("### Legal Authorization & Ethical Assessment Notice")
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
