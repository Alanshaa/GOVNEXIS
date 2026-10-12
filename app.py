"""GOVNEXIS — Intelligent Government Web Security Auditing Platform.

Main Application Entry Point and Navigation Router.
Tagline: "See the Risk. Fix the Gap. Build Trust."
"""

import streamlit as st

# Configure page metadata first
st.set_page_config(
    page_title="GOVNEXIS — Government Web Security Auditing Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.theme import apply_theme, LOGO_SVG
from core.config import APP_NAME, APP_TAGLINE, APP_VERSION
from core.database import init_db, seed_demo_history
from core.mock_site import start_mock_server

# Import Pages
from ui.page_overview import render_overview_page
from ui.page_scanner import render_scanner_page
from ui.page_findings import render_findings_page
from ui.page_remediation import render_remediation_page
from ui.page_verification import render_verification_page
from ui.page_history import render_history_page
from ui.page_reports import render_reports_page
from ui.page_demo_lab import render_demo_lab_page
from ui.page_settings import render_settings_page


def main():
    # Initialize database, telemetry seed records, and local sandbox server
    init_db()
    seed_demo_history()
    start_mock_server()

    # Apply Custom Dark Cyber Theme
    apply_theme()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #1e293b; margin-bottom: 16px;">
            {LOGO_SVG}
            <div>
                <div style="font-size: 1.3rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.05em;">
                    GOV<span style="color: #10b981;">NEXIS</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748b;">Security Audit Platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            "1. Overview",
            "2. New Security Scan",
            "3. Findings Center",
            "4. Remediation Lab",
            "5. Before & After Verification",
            "6. Scan History",
            "7. Reports",
            "8. Local Demo Lab",
            "9. Settings and About"
        ]

        # Read query param or session state for navigation
        default_index = 0
        if "active_page" in st.session_state:
            for i, opt in enumerate(nav_options):
                if opt.startswith(str(st.session_state["active_page"])):
                    default_index = i
                    break

        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=default_index,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid #1e293b; border-radius: 8px; padding: 12px; margin-top: 10px;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8;">ACTIVE COMPLIANCE</div>
            <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 2px;">
                CISA BOD 18-01<br>
                NIST SP 800-52r2<br>
                OWASP Secure Headers
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption(f"GOVNEXIS Core v{APP_VERSION} (Defensive)")

    # Page Routing
    if "Overview" in selected_page:
        render_overview_page()
    elif "New Security Scan" in selected_page:
        render_scanner_page()
    elif "Findings Center" in selected_page:
        render_findings_page()
    elif "Remediation Lab" in selected_page:
        render_remediation_page()
    elif "Before & After" in selected_page:
        render_verification_page()
    elif "Scan History" in selected_page:
        render_history_page()
    elif "Reports" in selected_page:
        render_reports_page()
    elif "Local Demo Lab" in selected_page:
        render_demo_lab_page()
    elif "Settings" in selected_page:
        render_settings_page()


if __name__ == "__main__":
    main()
