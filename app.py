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

from ui.theme import apply_theme, LOGO_SVG, render_sidebar_brand, render_sidebar_compliance
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
        render_sidebar_brand()

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
        render_sidebar_compliance()

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
