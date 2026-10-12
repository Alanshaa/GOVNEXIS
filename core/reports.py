"""Professional Report Generation Engine for GOVNEXIS.

Supports multi-format exports:
- Structured JSON (machine-readable)
- Executive HTML Report (cyber-styled, self-contained, escaped)
- CSV Spreadsheet Export (remediation tracking)
- Executive PDF Report (ReportLab styled vector document)
"""

import json
import csv
import io
import html
from typing import Dict, Any, List
from core.config import APP_NAME, APP_TAGLINE, APP_VERSION
from core.scanner import ScanResult


def generate_json_report(scan_dict: Dict[str, Any]) -> str:
    """Produce formatted machine-readable JSON security assessment export."""
    payload = {
        "metadata": {
            "platform": APP_NAME,
            "version": APP_VERSION,
            "tagline": APP_TAGLINE,
            "report_type": "Web Security Configuration Audit",
            "generation_time": scan_dict.get("timestamp"),
            "disclaimer": (
                "This assessment evaluates public HTTP headers and TLS configuration posture. "
                "It does not certify the absence of software application vulnerabilities."
            ),
        },
        "target": {
            "target_url": scan_dict.get("target_url"),
            "final_url": scan_dict.get("final_url"),
            "hostname": scan_dict.get("hostname"),
            "status_code": scan_dict.get("status_code"),
            "resolved_ips": scan_dict.get("resolved_ips", []),
        },
        "score": scan_dict.get("score_report", {}),
        "tls_observations": scan_dict.get("tls_info"),
        "findings": scan_dict.get("findings", []),
        "raw_headers": scan_dict.get("response_headers", {}),
    }
    return json.dumps(payload, indent=2)


def generate_csv_report(scan_dict: Dict[str, Any]) -> str:
    """Generate CSV spreadsheet formatted findings for ticketing or SIEM ingestion."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Platform", "Target Hostname", "Scan Timestamp", "Score",
        "Check ID", "Title", "Severity", "Category", "Status",
        "Evidence", "Recommended Action", "Primary Reference"
    ])

    hostname = scan_dict.get("hostname", "")
    timestamp = scan_dict.get("timestamp", "")
    score = scan_dict.get("score_report", {}).get("final_score", 0)

    for finding in scan_dict.get("findings", []):
        ref_url = ""
        refs = finding.get("references", [])
        if refs and len(refs) > 0:
            ref_url = refs[0].get("url", "")

        writer.writerow([
            APP_NAME,
            hostname,
            timestamp,
            score,
            finding.get("check_id", ""),
            finding.get("title", ""),
            finding.get("severity", ""),
            finding.get("category", ""),
            finding.get("status", ""),
            finding.get("evidence", ""),
            finding.get("recommended_action", ""),
            ref_url,
        ])

    return output.getvalue()


def generate_html_report(scan_dict: Dict[str, Any]) -> str:
    """Generate a responsive, standalone executive cybersecurity audit report in HTML."""
    target_url = html.escape(str(scan_dict.get("target_url", "")))
    final_url = html.escape(str(scan_dict.get("final_url", "")))
    hostname = html.escape(str(scan_dict.get("hostname", "")))
    timestamp = html.escape(str(scan_dict.get("timestamp", "")))
    score = scan_dict.get("score_report", {}).get("final_score", 0)
    grade = html.escape(str(scan_dict.get("score_report", {}).get("letter_grade", "N/A")))
    findings = scan_dict.get("findings", [])

    # Color tokens
    score_color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 60 else "#ef4444")

    # Generate Findings HTML rows
    finding_rows = []
    for f in findings:
        title = html.escape(str(f.get("title", "")))
        cat = html.escape(str(f.get("category", "")))
        sev = html.escape(str(f.get("severity", "")))
        status = html.escape(str(f.get("status", "")))
        evidence = html.escape(str(f.get("evidence", "")))
        remediation = html.escape(str(f.get("recommended_action", "")))

        status_badge_bg = "#064e3b" if status == "PASS" else ("#78350f" if status == "WARNING" else ("#7f1d1d" if status == "FAIL" else "#334155"))
        status_badge_text = "#34d399" if status == "PASS" else ("#fbbf24" if status == "WARNING" else ("#f87171" if status == "FAIL" else "#94a3b8"))

        finding_rows.append(f"""
        <tr style="border-bottom: 1px solid #1e293b;">
            <td style="padding: 12px; font-weight: 600; color: #f8fafc;">
                {title}
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 400;">{cat}</div>
            </td>
            <td style="padding: 12px; text-align: center;">
                <span style="display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; background: {status_badge_bg}; color: {status_badge_text};">
                    {status}
                </span>
            </td>
            <td style="padding: 12px; font-size: 0.85rem; color: #94a3b8;">{sev}</td>
            <td style="padding: 12px; font-family: monospace; font-size: 0.8rem; color: #cbd5e1; max-width: 320px; word-break: break-all;">
                {evidence}
            </td>
            <td style="padding: 12px; font-size: 0.85rem; color: #a7f3d0;">
                {remediation}
            </td>
        </tr>
        """)

    joined_rows = "\n".join(finding_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GOVNEXIS Security Configuration Audit — {hostname}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #0b0f17;
            color: #e2e8f0;
            margin: 0;
            padding: 30px;
        }}
        .report-card {{
            max-width: 1100px;
            margin: 0 auto;
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 35px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #10b981;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .brand {{
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            color: #f8fafc;
        }}
        .brand span {{ color: #10b981; }}
        .score-box {{
            text-align: center;
            background: #0f172a;
            border: 2px solid {score_color};
            border-radius: 10px;
            padding: 12px 25px;
        }}
        .score-val {{
            font-size: 2.2rem;
            font-weight: 900;
            color: {score_color};
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
            background: #0b0f17;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #1e293b;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            text-align: left;
        }}
        th {{
            background: #0f172a;
            color: #94a3b8;
            padding: 12px;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid #1e293b;
        }}
        .disclaimer {{
            margin-top: 35px;
            padding: 15px;
            border-radius: 6px;
            background: #0f172a;
            border-left: 4px solid #06b6d4;
            font-size: 0.8rem;
            color: #94a3b8;
            line-height: 1.5;
        }}
        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .report-card {{ border: none; box-shadow: none; background: #fff; color: #000; }}
            .summary-grid {{ background: #f8fafc; border: 1px solid #e2e8f0; }}
            th {{ background: #f1f5f9; color: #334155; }}
            tr {{ border-bottom: 1px solid #e2e8f0; }}
            .brand {{ color: #0f172a; }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="header">
            <div>
                <div class="brand">GOV<span>NEXIS</span></div>
                <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 4px;">{APP_TAGLINE}</div>
                <div style="color: #64748b; font-size: 0.8rem;">Government Website Security Configuration Audit Report</div>
            </div>
            <div class="score-box">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em;">Security Score</div>
                <div class="score-val">{score}/100</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: {score_color};">Grade: {grade}</div>
            </div>
        </div>

        <div class="summary-grid">
            <div>
                <div style="font-size: 0.75rem; color: #64748b;">TARGET HOSTNAME</div>
                <div style="font-weight: 600; color: #f8fafc;">{hostname}</div>
            </div>
            <div>
                <div style="font-size: 0.75rem; color: #64748b;">ASSESSMENT URL</div>
                <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem; word-break: break-all;">{target_url}</div>
            </div>
            <div>
                <div style="font-size: 0.75rem; color: #64748b;">AUDIT TIMESTAMP</div>
                <div style="font-weight: 600; color: #f8fafc;">{timestamp}</div>
            </div>
            <div>
                <div style="font-size: 0.75rem; color: #64748b;">TOTAL CHECKS</div>
                <div style="font-weight: 600; color: #f8fafc;">{len(findings)} Rules Evaluated</div>
            </div>
        </div>

        <h3 style="color: #f8fafc; margin-top: 30px; margin-bottom: 10px; border-left: 3px solid #10b981; padding-left: 10px;">
            Detailed Configuration Audit Findings
        </h3>

        <table>
            <thead>
                <tr>
                    <th>Security Check & Category</th>
                    <th style="text-align: center;">Status</th>
                    <th>Severity</th>
                    <th>Observed Evidence</th>
                    <th>Recommended Action</th>
                </tr>
            </thead>
            <tbody>
                {joined_rows}
            </tbody>
        </table>

        <div class="disclaimer">
            <strong>Methodology & Legal Notice:</strong> GOVNEXIS performs non-destructive, passive observation of web server response headers and TLS certificates in compliance with CISA BOD 18-01 and NIST SP 800-52 guidelines. This report identifies configuration hygiene gaps and does not certify complete defense against code execution, SQL injection, or server-side exploits.
        </div>
    </div>
</body>
</html>
"""


def generate_pdf_report(scan_dict: Dict[str, Any]) -> bytes:
    """Generate an executive PDF security report using ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom ReportLab styles
    title_style = ParagraphStyle(
        "GovNexisTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "GovNexisSubTitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569"),
        fontName="Helvetica",
    )
    header_style = ParagraphStyle(
        "GovNexisHeader",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#047857"),
        fontName="Helvetica-Bold",
    )
    cell_style = ParagraphStyle(
        "GovNexisCell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica",
    )
    cell_bold_style = ParagraphStyle(
        "GovNexisCellBold",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )

    story = []

    # Title Banner
    story.append(Paragraph("<b>GOVNEXIS</b> — Government Website Security Audit Report", title_style))
    story.append(Paragraph(f"{APP_TAGLINE} | Platform Version {APP_VERSION}", subtitle_style))
    story.append(Spacer(1, 12))

    # Executive Summary Info Table
    hostname = scan_dict.get("hostname", "Unknown")
    timestamp = scan_dict.get("timestamp", "Unknown")
    score = scan_dict.get("score_report", {}).get("final_score", 0)
    grade = scan_dict.get("score_report", {}).get("letter_grade", "N/A")

    info_data = [
        [
            Paragraph("<b>Target Host:</b> " + hostname, cell_style),
            Paragraph("<b>Audit Date:</b> " + str(timestamp)[:19], cell_style),
            Paragraph(f"<b>Security Score:</b> {score}/100 (Grade {grade})", cell_bold_style),
        ]
    ]
    info_table = Table(info_data, colWidths=[180, 180, 180])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # Findings Table Header
    story.append(Paragraph("Evaluated Security Configuration Checks", header_style))
    story.append(Spacer(1, 6))

    table_data = [
        [
            Paragraph("<b>Security Rule</b>", cell_bold_style),
            Paragraph("<b>Status</b>", cell_bold_style),
            Paragraph("<b>Severity</b>", cell_bold_style),
            Paragraph("<b>Observed Evidence</b>", cell_bold_style),
            Paragraph("<b>Recommended Action</b>", cell_bold_style),
        ]
    ]

    for f in scan_dict.get("findings", []):
        st = f.get("status", "")
        # Status text styling
        st_color = "#047857" if st == "PASS" else ("#b45309" if st == "WARNING" else "#b91c1c")
        st_text = f"<font color='{st_color}'><b>{st}</b></font>"

        table_data.append([
            Paragraph(f.get("title", ""), cell_bold_style),
            Paragraph(st_text, cell_style),
            Paragraph(f.get("severity", ""), cell_style),
            Paragraph(f.get("evidence", "")[:120], cell_style),
            Paragraph(f.get("recommended_action", "")[:120], cell_style),
        ])

    findings_table = Table(table_data, colWidths=[120, 55, 55, 155, 155])
    findings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 14))

    # Methodology & Legal Disclaimer
    disclaimer_text = (
        "<b>Notice:</b> This automated audit inspects public HTTP headers and TLS handshakes in alignment "
        "with CISA BOD 18-01, NIST SP 800-52, and OWASP recommendations. It provides defensive configuration guidance "
        "and is intended exclusively for authorized system administrators and site owners."
    )
    story.append(Paragraph(disclaimer_text, subtitle_style))

    doc.build(story)
    return buffer.getvalue()
