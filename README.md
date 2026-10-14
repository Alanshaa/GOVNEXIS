# GOVNEXIS

> **Intelligent Government Web Security Auditing Platform**  
> *"See the Risk. Fix the Gap. Build Trust."*

---

## 🏛️ Executive Summary

**GOVNEXIS** is an intelligent, defensive cybersecurity auditing platform designed specifically for authorized public sector agencies, municipal portals, and government website administrators. It enables authorized teams to:

1. **Identify Security Configuration Weaknesses**: Non-destructively audit HTTP response headers, cookie attributes, TLS cryptographic parameters, and redirect behaviors.
2. **Understand Operational Impact**: Translate technical header omissions into clear, CVSS/CISA-aligned threat models and citizen trust risks.
3. **Prioritize Remediation**: Deliver battle-tested server configuration playbooks for Nginx, Apache, Caddy, Node.js, and Python.
4. **Empirically Verify Improvements**: Validate remediation through repeatable before-and-after follow-up audits with quantified delta metrics.

GOVNEXIS adheres strictly to **CISA Binding Operational Directive (BOD) 18-01**, **NIST SP 800-52 Rev. 2**, and **OWASP Secure Headers Project** guidelines.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph UI ["User Experience (Streamlit + Cyber Theme)"]
        Nav[Sidebar Navigation Router]
        Overview[Executive Dashboard & Trends]
        Scanner[Smart Website Scanner]
        Findings[Intelligent Findings Center]
        Remediation[Remediation Lab & Playbooks]
        Verification[Before & After Verification Engine]
        DemoLab[Isolated Local Demo Lab]
        Reports[Multi-Format Export Center]
    end

    subgraph Core ["GOVNEXIS Core Engine"]
        Validator[URL & SSRF Safety Validator]
        AuditEngine[Security Configuration Engine]
        Scoring[Transparent Scoring Calculator]
        ScannerCore[Defensive Request Orchestrator]
        ReportGen[PDF / HTML / JSON / CSV Generators]
        MockSite[Local Sandbox HTTP Server :8765]
    end

    subgraph Storage ["Persistence Layer (SQLite3)"]
        DB[(govnexis.db)]
        ScansTable[Scans History]
        FindingsTable[Audited Findings]
        TasksTable[Remediation Tasks]
    end

    Nav --> Overview & Scanner & Findings & Remediation & Verification & DemoLab & Reports
    Scanner --> Validator --> ScannerCore --> AuditEngine --> Scoring --> DB
    DemoLab <--> MockSite
    DB --> Overview & Findings & Remediation & Verification & Reports
    Reports --> ReportGen
```

---

## 🛡️ Core Features

| Feature | Description |
| :--- | :--- |
| **Executive Security Dashboard** | Real-time aggregate KPIs, severity donut charts, category distribution, and longitudinal score trajectories powered by Plotly. |
| **Smart Website Scanner** | Defensive, SSRF-guarded auditing engine enforcing owner authorization, strict timeouts, hop limits, and TLS observations. |
| **10 Configuration Checks** | Evaluates HTTPS enforcement, HSTS, CSP, X-Frame-Options, X-Content-Type-Options, cookie security flags, Referrer-Policy, Permissions-Policy, server banners, and TLS certificates. |
| **Intelligent Findings Center** | Searchable and filterable vulnerability management center with transparent rule-based prioritization (no opaque AI claims). |
| **Remediation Lab** | Ready-to-deploy configuration snippets for Nginx, Apache, Caddy, Node.js (Helmet), and FastAPI/Django, plus compatibility warnings. |
| **Before-and-After Verification** | Quantified verification engine calculating score delta (+pts), resolved check lists, and side-by-side header diffs. |
| **Isolated Local Demo Lab** | Safe localhost sandbox on `127.0.0.1:8765` simulating misconfigured baseline vs. hardened states for live hackathon demos. |
| **Professional Report Generator** | Export compliant audit reports in 4 formats: Vector PDF (ReportLab), Cyber HTML with print CSS, JSON, and CSV. |
| **Transparent Security Score** | Fully explainable 0–100 score reflecting weighted check evaluations and independent visibility of critical risks. |

---

## 🔒 Defensive Safeguards & Legal Compliance

GOVNEXIS is an **auditing and hardening platform**, not an offensive exploitation framework:
- **SSRF Defense**: Automatically blocks scans against private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), link-local (`169.254.0.0/16`), and multicast addresses.
- **DNS Rebinding Protection**: Resolves target hostnames and validates destination IP addresses prior to connecting.
- **Safe Redirect Tracing**: Validates each redirect hop (max 5 hops) to ensure targets cannot pivot to prohibited destinations.
- **Strict Timeouts**: 5-second connect timeout and 8-second read timeout prevent hung connections.
- **No Intrusive Testing**: Does not inject exploit payloads, perform SQL injection, attempt directory traversal, or execute brute-force attacks.
- **Mandatory Ownership Affirmation**: Explicit authorization affirmation is required before any scan is executed.

---

## 💻 Technology Stack

- **Backend / Engine**: Python 3.10+ (Standard library `socket`, `ssl`, `ipaddress`, `sqlite3`)
- **Web UI & Dashboard**: Streamlit, Plotly Express & Graph Objects, Pandas
- **Reporting**: ReportLab (PDF), Jinja2 / HTML5, CSV, JSON
- **Network Client**: Requests (with custom session adapters and streaming response limits)
- **Test Framework**: Pytest

---

🚀 Installation & Launch

GOVNEXIS is a Python-based website security auditing platform.

Prerequisites

- Python 3.10+
- Git

Linux / macOS

git clone YOUR_GITHUB_REPOSITORY_URL
cd GOVNEXIS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py

Windows

git clone YOUR_GITHUB_REPOSITORY_URL
cd GOVNEXIS
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py

Open the Application

Visit http://localhost:8501 in your browser.


## 🧪 Running Automated Tests

GOVNEXIS includes a comprehensive automated test suite covering network safety, SSRF blocking, rule evaluations, scoring mathematics, database persistence, report generation, and the local demo lifecycle.

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute all automated tests
pytest -v tests
```

---


## 👥 Contributors & Acknowledgements

- **GOVNEXIS Security Engineering Team , members are Muhammed Alansha,Karan,Joceln Olivia and Charu Netra**
- Built for government agency transparency and citizen digital trust.
- Standards reference: CISA BOD 18-01, NIST SP 800-52 Rev. 2, OWASP Secure Headers.
