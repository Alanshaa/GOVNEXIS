"""GOVNEXIS Configuration and Constants.

Intelligent Government Web Security Auditing Platform.
Tagline: "See the Risk. Fix the Gap. Build Trust."
"""

from typing import Dict, Any

APP_NAME = "GOVNEXIS"
APP_CATEGORY = "Government Website Security Configuration Auditing Platform"
APP_TAGLINE = "See the Risk. Fix the Gap. Build Trust."
APP_DESCRIPTION = (
    "GOVNEXIS helps authorized website owners identify security configuration weaknesses, "
    "understand their impact, prioritize remediation, and verify improvements through "
    "repeatable security checks."
)
APP_VERSION = "2.4.0"
AUTHOR = "GOVNEXIS Security Engineering Team"

# Local Demo Server Configuration
LOCAL_DEMO_HOST = "127.0.0.1"
LOCAL_DEMO_PORT = 8765
LOCAL_DEMO_URL = f"http://{LOCAL_DEMO_HOST}:{LOCAL_DEMO_PORT}"

# Scanner Constraints & Defensive Guards
CONNECT_TIMEOUT = 5.0       # seconds
READ_TIMEOUT = 8.0          # seconds
MAX_REDIRECTS = 5           # redirect hop limit
MAX_RESPONSE_BYTES = 2097152  # 2 MB response size cap
SCAN_USER_AGENT = "GOVNEXIS-Security-Auditor/2.4.0 (Defensive-Audit-Platform; Authorized-Use-Only)"

# Result Statuses
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARNING = "WARNING"
STATUS_NOT_ASSESSED = "NOT ASSESSED"

# Severity Categories
SEV_CRITICAL = "Critical"
SEV_HIGH = "High"
SEV_MEDIUM = "Medium"
SEV_LOW = "Low"
SEV_INFO = "Informational"

# Transparent Security Scoring Weights (Sum = 100)
# Based on CISA BOD 18-01, NIST SP 800-52r2, and OWASP Secure Headers Project
CHECK_WEIGHTS: Dict[str, Dict[str, Any]] = {
    "https_enforced": {
        "title": "HTTPS Transport Enforcement",
        "weight": 20,
        "severity_on_fail": SEV_CRITICAL,
        "category": "Transport Layer Security",
        "description": "Verifies that communication requires TLS encryption to prevent eavesdropping and tampering.",
    },
    "hsts_header": {
        "title": "HTTP Strict Transport Security (HSTS)",
        "weight": 15,
        "severity_on_fail": SEV_HIGH,
        "category": "Transport Layer Security",
        "description": "Checks for Strict-Transport-Security with max-age >= 1 year and includeSubDomains.",
    },
    "content_security_policy": {
        "title": "Content-Security-Policy (CSP)",
        "weight": 15,
        "severity_on_fail": SEV_HIGH,
        "category": "Injection Defense",
        "description": "Inspects CSP directives to mitigate Cross-Site Scripting (XSS) and code injection.",
    },
    "x_frame_options": {
        "title": "Clickjacking Defense (X-Frame-Options / frame-ancestors)",
        "weight": 10,
        "severity_on_fail": SEV_MEDIUM,
        "category": "UI Redressing",
        "description": "Ensures the site prevents embedding in hostile iframes via X-Frame-Options or CSP frame-ancestors.",
    },
    "x_content_type_options": {
        "title": "MIME-Sniffing Defense (X-Content-Type-Options)",
        "weight": 10,
        "severity_on_fail": SEV_MEDIUM,
        "category": "Content Handling",
        "description": "Requires 'nosniff' to prevent browsers from interpreting non-executable MIME types as executable.",
    },
    "secure_cookies": {
        "title": "Cookie Security Attributes (Secure, HttpOnly, SameSite)",
        "weight": 10,
        "severity_on_fail": SEV_MEDIUM,
        "category": "Session Integrity",
        "description": "Audits Set-Cookie headers for Secure flag, HttpOnly flag, and appropriate SameSite controls.",
    },
    "referrer_policy": {
        "title": "Referrer-Policy Header",
        "weight": 5,
        "severity_on_fail": SEV_LOW,
        "category": "Information Disclosure",
        "description": "Restricts URL path and parameter leakage in Referer headers to third-party destinations.",
    },
    "permissions_policy": {
        "title": "Permissions-Policy Header",
        "weight": 5,
        "severity_on_fail": SEV_LOW,
        "category": "Feature Governance",
        "description": "Disables unnecessary browser hardware features (camera, microphone, geolocation) by default.",
    },
    "server_disclosure": {
        "title": "Server Information Disclosure",
        "weight": 5,
        "severity_on_fail": SEV_LOW,
        "category": "Information Disclosure",
        "description": "Checks if Server or X-Powered-By headers leak detailed software versions or OS architectures.",
    },
    "tls_configuration": {
        "title": "TLS Protocol & Certificate Hygiene",
        "weight": 5,
        "severity_on_fail": SEV_LOW,
        "category": "Cryptographic Hygiene",
        "description": "Observes TLS protocol version (>= TLSv1.2 required) and certificate validity window.",
    },
}

# Database File
DATABASE_PATH = "govnexis.db"
