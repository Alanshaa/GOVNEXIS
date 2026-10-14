"""GOVNEXIS — Intelligent Government Web Security Auditing Platform.

Main Application Entry Point and Navigation Router.
Tagline: "See the Risk. Fix the Gap. Build Trust."
"""

import streamlit as st

# Configure page metadata first (must be the very first Streamlit call)
st.set_page_config(
    page_title="GOVNEXIS — Government Web Security Auditing",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.theme import (
    apply_theme,
    render_sidebar_brand,
    render_sidebar_compliance,
    get_current_theme,
    set_theme,
)
from core.config import APP_VERSION
from core.database import init_db, seed_demo_history
from core.mock_site import start_mock_server

# Import page renderers
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
    """Application entry point: initialise services, apply theme, route pages."""
    # Initialise database, seed demo records on first run, start sandbox server
    init_db()
    seed_demo_history()
    start_mock_server()

    # Apply the professional theme (dark or light based on persisted preference)
    apply_theme()

    # ---- Sidebar ----
    with st.sidebar:
        render_sidebar_brand()

        nav_options = [
            "New Scan",
            "Overview",
            "Findings",
            "Remediation",
            "Verification",
            "Reports",
            "Demo Lab",
            "History",
            "Settings",
        ]

        # Restore active page from session state (supports int or str)
        default_index = 0
        if "active_page" in st.session_state:
            val = st.session_state["active_page"]
            if isinstance(val, int) and 1 <= val <= len(nav_options):
                default_index = val - 1
            elif isinstance(val, str):
                for idx, opt in enumerate(nav_options):
                    if opt.lower() == val.lower() or val.lower() in opt.lower():
                        default_index = idx
                        break

        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=default_index,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Theme switcher — compact toggle
        current = get_current_theme()
        theme_label = "Switch to Light" if current == "dark" else "Switch to Dark"
        if st.button(theme_label, use_container_width=True):
            new_theme = "light" if current == "dark" else "dark"
            set_theme(new_theme)
            st.rerun()

        render_sidebar_compliance()
        st.caption(f"GOVNEXIS v{APP_VERSION}")

    # ---- Page routing ----
    if selected_page == "Overview":
        render_overview_page()
    elif selected_page == "New Scan":
        render_scanner_page()
    elif selected_page == "Findings":
        render_findings_page()
    elif selected_page == "Remediation":
        render_remediation_page()
    elif selected_page == "Verification":
        render_verification_page()
    elif selected_page == "History":
        render_history_page()
    elif selected_page == "Reports":
        render_reports_page()
    elif selected_page == "Demo Lab":
        render_demo_lab_page()
    elif selected_page == "Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
