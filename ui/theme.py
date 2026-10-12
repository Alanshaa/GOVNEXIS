"""Theme, Aesthetics and UI Components for GOVNEXIS.

Cybersecurity Aesthetic Tokens:
- Dark Charcoal / Midnight Navy background (#080c14, #0f172a)
- Emerald Green (#10b981, #059669, #34d399)
- Electric Cyan (#06b6d4, #22d3ee, #00f2fe)
- Silver & Slate Typography (#f8fafc, #e2e8f0, #94a3b8)
- Subtle grid lines, glassmorphism, responsive cards, consistent badges
"""

import streamlit as st
from typing import Optional
from core.config import APP_NAME, APP_TAGLINE, APP_VERSION

LOGO_SVG = """
<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" />
      <stop offset="100%" stop-color="#10b981" />
    </linearGradient>
    <linearGradient id="glowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.2" />
    </linearGradient>
  </defs>
  <!-- Outer Shield -->
  <path d="M50 8 L85 24 V52 C85 74 50 92 50 92 C50 92 15 74 15 52 V24 L50 8 Z" 
        stroke="url(#shieldGrad)" stroke-width="4" fill="#0f172a" fill-opacity="0.85" />
  <!-- Cyber Circuit Network Nodes -->
  <circle cx="50" cy="35" r="4" fill="#10b981" />
  <circle cx="35" cy="55" r="3.5" fill="#06b6d4" />
  <circle cx="65" cy="55" r="3.5" fill="#06b6d4" />
  <circle cx="50" cy="72" r="4" fill="#34d399" />
  <!-- Connecting Hexagon/G Lattice -->
  <path d="M50 35 L65 55 L50 72 L35 55 Z" stroke="#38bdf8" stroke-width="2" stroke-dasharray="3,2" fill="none" />
  <!-- Stylized Monogram G -->
  <path d="M57 44 H46 C41 44 41 62 46 62 H55 V52 H49" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
</svg>
"""

CUSTOM_CSS = """
<style>
/* Root CSS Variables */
:root {
    --bg-main: #080c14;
    --bg-card: #0f172a;
    --bg-card-hover: #1e293b;
    --border-color: #1e293b;
    --border-glow: rgba(16, 185, 129, 0.3);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-emerald: #10b981;
    --accent-cyan: #06b6d4;
    --sev-critical: #ef4444;
    --sev-high: #f97316;
    --sev-medium: #eab308;
    --sev-low: #3b82f6;
    --sev-info: #64748b;
}

/* Background Cyber Grid */
.stApp {
    background-color: var(--bg-main);
    background-image: 
        linear-gradient(to right, rgba(30, 41, 59, 0.2) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(30, 41, 59, 0.2) 1px, transparent 1px);
    background-size: 36px 36px;
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid #1e293b !important;
}

/* Cyber Header Banner */
.gov-brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(8, 12, 20, 0.95));
    border: 1px solid #1e293b;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.6);
}

.gov-brand-title {
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 12px;
}

.gov-brand-title span.emerald {
    color: var(--accent-emerald);
}

.gov-brand-title span.cyan {
    color: var(--accent-cyan);
}

.gov-brand-tagline {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 3px;
    letter-spacing: 0.02em;
}

/* Metric Card */
.gov-metric-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.gov-metric-card:hover {
    border-color: rgba(16, 185, 129, 0.4);
    transform: translateY(-2px);
}

.gov-metric-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.gov-metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 4px 0;
}

.gov-metric-delta {
    font-size: 0.8rem;
    color: #34d399;
}

/* Badges */
.badge-pass {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-block;
}

.badge-fail {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-block;
}

.badge-warning {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-block;
}

.badge-na {
    background-color: rgba(100, 116, 139, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(100, 116, 139, 0.4);
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    display: inline-block;
}

/* Severity Badges */
.badge-sev-critical {
    background-color: #ef4444;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-sev-high {
    background-color: #f97316;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-sev-medium {
    background-color: #eab308;
    color: #0f172a;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-sev-low {
    background-color: #3b82f6;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-sev-info {
    background-color: #64748b;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* Demo Mode Banner */
.demo-banner {
    background: linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(16, 185, 129, 0.15));
    border: 1px solid rgba(6, 182, 212, 0.4);
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}
</style>
"""


def apply_theme():
    """Inject the dark cyber theme into the Streamlit session."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_brand_header(subtitle: Optional[str] = None):
    """Render the official GOVNEXIS header bar with logo, wordmark and tagline."""
    sub_text = subtitle or APP_TAGLINE
    st.markdown(f"""
    <div class="gov-brand-header">
        <div style="display: flex; align-items: center; gap: 16px;">
            {LOGO_SVG}
            <div>
                <div class="gov-brand-title">
                    GOV<span class="emerald">NEXIS</span>
                    <span style="font-size: 0.75rem; font-weight: 600; color: #06b6d4; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.3); padding: 2px 8px; border-radius: 9999px;">v{APP_VERSION}</span>
                </div>
                <div class="gov-brand-tagline">{sub_text}</div>
            </div>
        </div>
        <div style="text-align: right; font-size: 0.75rem; color: #64748b;">
            <div style="color: #34d399; font-weight: 600;">ACTIVE DEFENSE</div>
            <div>Government Web Security Auditing</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_demo_banner():
    """Render an explicit notice that local demo testing is active and isolated."""
    st.markdown("""
    <div class="demo-banner">
        <span style="font-size: 1.4rem;">🛡️</span>
        <div>
            <div style="font-weight: 700; color: #38bdf8; font-size: 0.9rem;">LOCAL DEMO LAB ACTIVE</div>
            <div style="font-size: 0.8rem; color: #94a3b8;">
                Target is strictly isolated to <code>127.0.0.1:8765</code>. No external network traffic is generated.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Return inline HTML pill badge for PASS, FAIL, WARNING, NOT ASSESSED."""
    if status == "PASS":
        return '<span class="badge-pass">✓ PASS</span>'
    elif status == "FAIL":
        return '<span class="badge-fail">✕ FAIL</span>'
    elif status == "WARNING":
        return '<span class="badge-warning">⚠ WARNING</span>'
    else:
        return '<span class="badge-na">○ NOT ASSESSED</span>'


def get_severity_badge_html(severity: str) -> str:
    """Return inline HTML pill badge for finding severity."""
    s = severity.lower()
    if s == "critical":
        return '<span class="badge-sev-critical">CRITICAL</span>'
    elif s == "high":
        return '<span class="badge-sev-high">HIGH</span>'
    elif s == "medium":
        return '<span class="badge-sev-medium">MEDIUM</span>'
    elif s == "low":
        return '<span class="badge-sev-low">LOW</span>'
    else:
        return '<span class="badge-sev-info">INFO</span>'
