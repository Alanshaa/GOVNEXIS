"""Test UI Rendering and Brand Header/Sidebar Markup Integrity.

Verifies that no raw HTML/CSS markup leaks into rendered markdown elements.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "app.py")


@pytest.mark.parametrize("page_num,page_name", [
    (1, "Overview"),
    (2, "New Security Scan"),
    (3, "Findings Center"),
    (4, "Remediation Lab"),
    (5, "Before & After Verification"),
    (6, "Scan History"),
    (7, "Reports"),
    (8, "Local Demo Lab"),
    (9, "Settings and About"),
])
def test_page_renders_without_raw_markup_leaks(page_num, page_name):
    """Test that each page executes without exceptions and does not leak raw HTML into markdown."""
    at = AppTest.from_file(APP_PATH)
    at.session_state["active_page"] = page_num
    at.run()

    assert len(at.exception) == 0, f"Exceptions occurred while rendering {page_name}: {at.exception}"

    # Verify no raw HTML header tags or SVG strings were parsed as markdown text / code fences
    for m in at.markdown:
        assert "gov-brand-header" not in m.value, f"Raw header HTML leaked into markdown on {page_name}"
        assert "shieldCyberGrad" not in m.value, f"Raw SVG leaked into markdown on {page_name}"
        assert "<linearGradient" not in m.value, f"Raw gradient leaked into markdown on {page_name}"
