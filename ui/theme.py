"""Advanced Futuristic Cyber Theme & Aesthetic System for GOVNEXIS.

Visual Design Language:
- Deep Void Cyberpunk Foundation (#030712, #070d1e)
- Holographic Neon Cyan (#00f2fe, #06b6d4, #38bdf8)
- Laser Matrix Emerald (#00ff87, #10b981, #34d399)
- Plasma Purple / Indigo Accents (#8b5cf6, #6366f1)
- Typography: Orbitron, Rajdhani, JetBrains Mono, Inter
- HUD Glassmorphism, Neon Edge Glows, Corner Accents, Animated Beacons
"""

import streamlit as st
from typing import Optional
from core.config import APP_NAME, APP_TAGLINE, APP_VERSION

import textwrap

LOGO_SVG = (
    '<svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<defs>'
    '<linearGradient id="shieldCyberGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
    '<stop offset="0%" stop-color="#00f2fe" />'
    '<stop offset="50%" stop-color="#06b6d4" />'
    '<stop offset="100%" stop-color="#00ff87" />'
    '</linearGradient>'
    '<filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">'
    '<feGaussianBlur stdDeviation="2.5" result="blur" />'
    '<feComposite in="SourceGraphic" in2="blur" operator="over" />'
    '</filter>'
    '</defs>'
    '<path d="M50 6 L88 23 V52 C88 76 50 94 50 94 C50 94 12 76 12 52 V23 L50 6 Z" stroke="url(#shieldCyberGrad)" stroke-width="3.5" fill="#070d1e" fill-opacity="0.9" filter="url(#neonGlow)" />'
    '<path d="M50 16 L78 30 V50 C78 68 50 82 50 82 C50 82 22 68 22 50 V30 L50 16 Z" stroke="rgba(0, 242, 254, 0.4)" stroke-width="1.5" stroke-dasharray="4,3" fill="none" />'
    '<circle cx="50" cy="35" r="4.5" fill="#00ff87" filter="url(#neonGlow)" />'
    '<circle cx="34" cy="56" r="3.5" fill="#00f2fe" />'
    '<circle cx="66" cy="56" r="3.5" fill="#00f2fe" />'
    '<circle cx="50" cy="74" r="4" fill="#38bdf8" />'
    '<path d="M50 35 L66 56 L50 74 L34 56 Z" stroke="#00f2fe" stroke-width="2" fill="rgba(6, 182, 212, 0.1)" />'
    '<path d="M58 44 H45 C39 44 39 64 45 64 H56 V53 H48" stroke="#ffffff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" fill="none" />'
    '</svg>'
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800;900&family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

/* Global Variables */
:root {
    --bg-void: #030712;
    --bg-surface: #070d1e;
    --bg-surface-elevated: #0d1527;
    --accent-cyan-neon: #00f2fe;
    --accent-cyan: #06b6d4;
    --accent-emerald-neon: #00ff87;
    --accent-emerald: #10b981;
    --accent-purple: #8b5cf6;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-glow: rgba(0, 242, 254, 0.3);
    --border-subtle: rgba(30, 41, 59, 0.7);
}

/* Background Atmosphere */
.stApp {
    background-color: var(--bg-void) !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.16) 0%, transparent 45%),
        radial-gradient(circle at 90% 20%, rgba(16, 185, 129, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 10% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
        linear-gradient(to right, rgba(14, 23, 42, 0.45) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(14, 23, 42, 0.45) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 32px 32px, 32px 32px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Typography Overrides */
h1, h2, h3, .cyber-font {
    font-family: 'Orbitron', 'Rajdhani', sans-serif !important;
    letter-spacing: 0.04em !important;
}

h4, h5, h6 {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.03em !important;
    font-weight: 700 !important;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Sidebar Ultra Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050a17 0%, #03060f 100%) !important;
    border-right: 1px solid rgba(0, 242, 254, 0.2) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.8) !important;
}

section[data-testid="stSidebar"] .stRadio > div {
    gap: 6px !important;
}

/* Sidebar Radio Buttons */
section[data-testid="stSidebar"] label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    color: #cbd5e1 !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] label:hover {
    color: var(--accent-cyan-neon) !important;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.5) !important;
}

/* Cyber Header Banner */
.gov-brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 28px;
    background: linear-gradient(135deg, rgba(13, 21, 39, 0.9) 0%, rgba(7, 13, 30, 0.95) 100%);
    border: 1px solid rgba(0, 242, 254, 0.28);
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.8), 0 0 20px -5px rgba(0, 242, 254, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}

.gov-brand-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00f2fe, #00ff87, transparent);
}

.gov-brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: #f8fafc;
    display: flex;
    align-items: center;
    gap: 12px;
    text-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
}

.gov-brand-title span.emerald {
    color: #00ff87;
    text-shadow: 0 0 15px rgba(0, 255, 135, 0.5);
}

.gov-brand-tagline {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    color: #94a3b8;
    margin-top: 2px;
    letter-spacing: 0.05em;
    font-weight: 500;
}

/* Advanced Futuristic Metric Cards */
.gov-metric-card {
    background: linear-gradient(145deg, rgba(13, 21, 39, 0.85) 0%, rgba(7, 13, 30, 0.95) 100%);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.gov-metric-card:hover {
    border-color: rgba(0, 242, 254, 0.5);
    box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 242, 254, 0.25);
    transform: translateY(-3px);
}

.gov-metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(180deg, #00f2fe, #00ff87);
}

.gov-metric-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.1em;
    font-weight: 700;
}

.gov-metric-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 6px 0;
    text-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
}

.gov-metric-delta {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: #38bdf8;
    font-weight: 600;
    letter-spacing: 0.03em;
}

/* Tactical HUD Bar */
.gov-hud-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(10, 17, 34, 0.65);
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 8px;
    padding: 8px 16px;
    margin-bottom: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #94a3b8;
}

.gov-pulse-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #00ff87;
    border-radius: 50%;
    margin-right: 8px;
    box-shadow: 0 0 8px #00ff87;
    animation: cyberPulse 2s infinite;
}

@keyframes cyberPulse {
    0% { box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }
    70% { box-shadow: 0 0 0 6px rgba(0, 255, 135, 0); }
    100% { box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }
}

/* Futuristic Streamlit Buttons */
.stButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 242, 254, 0.4) !important;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%) !important;
    color: #f8fafc !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
}

.stButton > button:hover {
    border-color: #00f2fe !important;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.4) 0%, rgba(16, 185, 129, 0.4) 100%) !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.45) !important;
    transform: translateY(-2px) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%) !important;
    border: 1px solid #00f2fe !important;
    color: #030712 !important;
    font-weight: 800 !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.4) !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 30px rgba(0, 255, 135, 0.6) !important;
}

/* Badges with Neon Glow */
.badge-pass {
    background: rgba(0, 255, 135, 0.12);
    color: #00ff87;
    border: 1px solid rgba(0, 255, 135, 0.5);
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.05em;
    display: inline-block;
    box-shadow: 0 0 10px rgba(0, 255, 135, 0.25);
}

.badge-fail {
    background: rgba(239, 68, 68, 0.15);
    color: #ff4d6d;
    border: 1px solid rgba(239, 68, 68, 0.6);
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.05em;
    display: inline-block;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.5);
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.05em;
    display: inline-block;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.25);
}

.badge-na {
    background: rgba(100, 116, 139, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(100, 116, 139, 0.4);
    padding: 3px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Rajdhani', sans-serif;
    display: inline-block;
}

/* Severity Badges */
.badge-sev-critical {
    background: #ff0055;
    color: #ffffff;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
    box-shadow: 0 0 10px rgba(255, 0, 85, 0.5);
}
.badge-sev-high {
    background: #f97316;
    color: #ffffff;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
    box-shadow: 0 0 8px rgba(249, 115, 22, 0.4);
}
.badge-sev-medium {
    background: #eab308;
    color: #030712;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
}
.badge-sev-low {
    background: #0284c7;
    color: #ffffff;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
}
.badge-sev-info {
    background: #475569;
    color: #ffffff;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 800;
    font-family: 'Orbitron', sans-serif;
}

/* Demo Banner */
.demo-banner {
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.15), rgba(0, 255, 135, 0.15));
    border: 1px solid rgba(0, 242, 254, 0.45);
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);
}
</style>
"""


def render_safe_html(html_str: str):
    """Safely render HTML without Markdown code-block interpretation.
    
    Uses native st.html if supported, and strips leading whitespace so markdown parsers
    never interpret indented markup as <pre><code> blocks.
    """
    clean_html = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        no_indent = "\n".join(line.lstrip() for line in clean_html.splitlines())
        st.markdown(no_indent, unsafe_allow_html=True)


def apply_theme():
    """Inject the advanced futuristic cyber theme into the Streamlit session."""
    render_safe_html(CUSTOM_CSS)


def render_brand_header(subtitle: Optional[str] = None):
    """Render the official GOVNEXIS futuristic header bar."""
    sub_text = subtitle or APP_TAGLINE
    header_html = (
        f'<div class="gov-brand-header">'
        f'<div style="display: flex; align-items: center; gap: 16px;">'
        f'{LOGO_SVG}'
        f'<div>'
        f'<div class="gov-brand-title">'
        f'GOV<span class="emerald">NEXIS</span>'
        f'<span style="font-size: 0.7rem; font-weight: 700; color: #00f2fe; background: rgba(0, 242, 254, 0.12); border: 1px solid rgba(0, 242, 254, 0.4); padding: 2px 10px; border-radius: 9999px; text-shadow: none;">v{APP_VERSION} PRO</span>'
        f'</div>'
        f'<div class="gov-brand-tagline">{sub_text}</div>'
        f'</div>'
        f'</div>'
        f'<div style="text-align: right;">'
        f'<div style="display: flex; align-items: center; justify-content: flex-end;">'
        f'<span class="gov-pulse-dot"></span>'
        f'<span style="font-family: \'Orbitron\', sans-serif; font-size: 0.8rem; font-weight: 700; color: #00ff87; letter-spacing: 0.05em;">DEFENSE POSTURE ACTIVE</span>'
        f'</div>'
        f'<div style="font-family: \'Rajdhani\', sans-serif; font-size: 0.75rem; color: #64748b; margin-top: 2px;">CISA BOD 18-01 // NIST SP 800-52</div>'
        f'</div>'
        f'</div>'
    )
    render_safe_html(header_html)


def render_sidebar_brand():
    """Render the sidebar branding header with logo, wordmark, and subtitle."""
    brand_html = (
        f'<div style="display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(0, 242, 254, 0.2); margin-bottom: 16px;">'
        f'{LOGO_SVG}'
        f'<div>'
        f'<div style="font-family: \'Orbitron\', sans-serif; font-size: 1.3rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.05em;">'
        f'GOV<span style="color: #00ff87;">NEXIS</span>'
        f'</div>'
        f'<div style="font-family: \'Rajdhani\', sans-serif; font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.03em;">Security Audit Platform</div>'
        f'</div>'
        f'</div>'
    )
    render_safe_html(brand_html)


def render_sidebar_compliance():
    """Render the sidebar active compliance badge container."""
    compliance_html = (
        '<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 8px; padding: 12px; margin-top: 10px;">'
        '<div style="font-family: \'Orbitron\', sans-serif; font-size: 0.75rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.05em;">ACTIVE COMPLIANCE</div>'
        '<div style="font-family: \'Rajdhani\', sans-serif; font-size: 0.75rem; color: #94a3b8; margin-top: 4px; line-height: 1.4;">'
        'CISA BOD 18-01<br>'
        'NIST SP 800-52r2<br>'
        'OWASP Secure Headers'
        '</div>'
        '</div>'
    )
    render_safe_html(compliance_html)


def render_hud_telemetry():
    """Render tactical live system telemetry HUD bar."""
    hud_html = (
        '<div class="gov-hud-bar">'
        '<div><span class="gov-pulse-dot"></span>SYSTEM STATUS: <strong>OPERATIONAL</strong></div>'
        '<div>DEFENSIVE RULES: <strong>10 ACTIVE</strong></div>'
        '<div>SSRF GUARD: <strong>ENFORCED (RFC1918 FILTER)</strong></div>'
        '<div>ENCRYPTION MONITOR: <strong>TLS 1.3 / HSTS COMPLIANT</strong></div>'
        '</div>'
    )
    render_safe_html(hud_html)


def render_demo_banner():
    """Render an explicit notice that local demo testing is active and isolated."""
    demo_html = (
        '<div class="demo-banner">'
        '<span style="font-size: 1.6rem;">🛡️</span>'
        '<div>'
        '<div style="font-family: \'Orbitron\', sans-serif; font-weight: 700; color: #00f2fe; font-size: 0.95rem; letter-spacing: 0.04em;">ISOLATED LOCAL SANDBOX ENVIRONMENT</div>'
        '<div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">'
        'Target is strictly allowlisted to <code>127.0.0.1:8765</code>. Zero external network packets dispatched.'
        '</div>'
        '</div>'
        '</div>'
    )
    render_safe_html(demo_html)


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
