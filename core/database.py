"""SQLite Persistence Engine for GOVNEXIS.

Stores:
- Complete scan execution history & metrics
- Audited findings records with severity and category tags
- Remediation task tracking with verification lifecycle
- Aggregated metrics and trend calculations for executive dashboards
"""

import sqlite3
import json
import datetime
from typing import Dict, List, Any, Optional
from core.config import (
    DATABASE_PATH, STATUS_PASS, STATUS_FAIL, STATUS_WARNING, STATUS_NOT_ASSESSED,
    SEV_CRITICAL, SEV_HIGH, SEV_MEDIUM, SEV_LOW, SEV_INFO
)
from core.scanner import ScanResult


def get_connection(db_path: str = DATABASE_PATH) -> sqlite3.Connection:
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_PATH):
    """Initialize database tables and indexes."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_url TEXT NOT NULL,
                final_url TEXT NOT NULL,
                hostname TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                score INTEGER NOT NULL,
                letter_grade TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0,
                total_checks INTEGER NOT NULL,
                passed_checks INTEGER NOT NULL,
                failed_checks INTEGER NOT NULL,
                warning_checks INTEGER NOT NULL,
                not_assessed_checks INTEGER NOT NULL,
                critical_high_count INTEGER NOT NULL,
                raw_json TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                check_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                evidence TEXT NOT NULL,
                why_it_matters TEXT NOT NULL,
                potential_impact TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                verification_status TEXT NOT NULL DEFAULT 'Open',
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS remediation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_host TEXT NOT NULL,
                check_id TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                notes TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_hostname ON scans(hostname);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON findings(scan_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_remediation_target ON remediation_tasks(target_host);")
        conn.commit()


def save_scan(scan_result: ScanResult, db_path: str = DATABASE_PATH) -> int:
    """Persist a completed scan result and its individual findings into SQLite."""
    init_db(db_path)

    # Calculate status counts
    total_checks = len(scan_result.findings)
    passed_checks = sum(1 for f in scan_result.findings if f.status == STATUS_PASS)
    failed_checks = sum(1 for f in scan_result.findings if f.status == STATUS_FAIL)
    warning_checks = sum(1 for f in scan_result.findings if f.status == STATUS_WARNING)
    not_assessed_checks = sum(1 for f in scan_result.findings if f.status == STATUS_NOT_ASSESSED)
    critical_high_count = scan_result.score_report.critical_high_count

    raw_json = json.dumps(scan_result.to_dict())

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (
                target_url, final_url, hostname, timestamp, score, letter_grade,
                status_code, duration_ms, is_demo, total_checks, passed_checks,
                failed_checks, warning_checks, not_assessed_checks,
                critical_high_count, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_result.target_url,
            scan_result.final_url,
            scan_result.hostname,
            scan_result.timestamp,
            scan_result.score_report.final_score,
            scan_result.score_report.letter_grade,
            scan_result.status_code,
            scan_result.duration_ms,
            1 if scan_result.is_demo else 0,
            total_checks,
            passed_checks,
            failed_checks,
            warning_checks,
            not_assessed_checks,
            critical_high_count,
            raw_json
        ))
        scan_id = cursor.lastrowid

        for finding in scan_result.findings:
            cursor.execute("""
                INSERT INTO findings (
                    scan_id, check_id, title, category, severity, status,
                    evidence, why_it_matters, potential_impact, recommended_action,
                    verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                finding.check_id,
                finding.title,
                finding.category,
                finding.severity,
                finding.status,
                finding.evidence,
                finding.why_it_matters,
                finding.potential_impact,
                finding.recommended_action,
                "Open" if finding.status in (STATUS_FAIL, STATUS_WARNING) else "Verified"
            ))

            # Maintain or insert remediation task if issue exists
            if finding.status in (STATUS_FAIL, STATUS_WARNING):
                cursor.execute("""
                    SELECT id FROM remediation_tasks
                    WHERE target_host = ? AND check_id = ?
                """, (scan_result.hostname, finding.check_id))
                existing = cursor.fetchone()
                if not existing:
                    cursor.execute("""
                        INSERT INTO remediation_tasks (target_host, check_id, title, status, notes, updated_at)
                        VALUES (?, ?, ?, 'Open', 'Auto-created from scan detection', ?)
                    """, (scan_result.hostname, finding.check_id, finding.title, scan_result.timestamp))

        conn.commit()
        return scan_id


def get_scan(scan_id: int, db_path: str = DATABASE_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve full details of a specific scan by ID."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
        row = cursor.fetchone()
        if not row:
            return None
        scan_data = dict(row)
        scan_data["details"] = json.loads(scan_data["raw_json"])

        cursor.execute("SELECT * FROM findings WHERE scan_id = ? ORDER BY id ASC", (scan_id,))
        scan_data["findings"] = [dict(f) for f in cursor.fetchall()]
        return scan_data


def get_all_scans(limit: int = 100, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """Retrieve list of scans ordered by most recent first."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]


def delete_scan(scan_id: int, db_path: str = DATABASE_PATH) -> bool:
    """Delete a scan and its associated findings."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM findings WHERE scan_id = ?", (scan_id,))
        cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        return cursor.rowcount > 0


def delete_all_scans(db_path: str = DATABASE_PATH):
    """Clear all scans and findings from database."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM findings")
        cursor.execute("DELETE FROM scans")
        cursor.execute("DELETE FROM remediation_tasks")
        conn.commit()


def get_scan_trends(db_path: str = DATABASE_PATH) -> Dict[str, Any]:
    """Calculate executive dashboard metrics across all historical scans."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT hostname), AVG(score) FROM scans")
        scans_count_row = cursor.fetchone()
        total_scans = scans_count_row[0] or 0
        unique_targets = scans_count_row[1] or 0
        avg_score = round(scans_count_row[2] or 0.0, 1)

        # Latest scan info
        cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC LIMIT 1")
        latest_row = cursor.fetchone()
        latest_scan = dict(latest_row) if latest_row else None

        # Severity distribution of all active findings in the latest scans of each host
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM findings
            WHERE status IN ('FAIL', 'WARNING')
            GROUP BY severity
        """)
        severity_counts = {row["severity"]: row["count"] for row in cursor.fetchall()}
        for s in (SEV_CRITICAL, SEV_HIGH, SEV_MEDIUM, SEV_LOW, SEV_INFO):
            severity_counts.setdefault(s, 0)

        # Category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM findings
            WHERE status IN ('FAIL', 'WARNING')
            GROUP BY category
            ORDER BY count DESC
        """)
        category_counts = {row["category"]: row["count"] for row in cursor.fetchall()}

        # Activity over time (scans grouped by date YYYY-MM-DD)
        cursor.execute("""
            SELECT substr(timestamp, 1, 10) as scan_date, COUNT(*) as count, AVG(score) as avg_score
            FROM scans
            GROUP BY scan_date
            ORDER BY scan_date ASC
        """)
        activity_over_time = [dict(r) for r in cursor.fetchall()]

        # Top recurring configuration issues
        cursor.execute("""
            SELECT title, category, severity, COUNT(*) as occurrences
            FROM findings
            WHERE status IN ('FAIL', 'WARNING')
            GROUP BY title
            ORDER BY occurrences DESC
            LIMIT 5
        """)
        top_issues = [dict(r) for r in cursor.fetchall()]

        # Remediation resolution counts
        cursor.execute("SELECT status, COUNT(*) as count FROM remediation_tasks GROUP BY status")
        remediation_counts = {row["status"]: row["count"] for row in cursor.fetchall()}
        resolved_count = remediation_counts.get("Fixed", 0) + remediation_counts.get("Verified", 0)

        return {
            "total_scans": total_scans,
            "unique_targets": unique_targets,
            "avg_score": avg_score,
            "latest_scan": latest_scan,
            "severity_counts": severity_counts,
            "category_counts": category_counts,
            "activity_over_time": activity_over_time,
            "top_issues": top_issues,
            "resolved_count": resolved_count,
            "remediation_counts": remediation_counts,
        }


def get_remediation_tasks(target_host: Optional[str] = None, db_path: str = DATABASE_PATH) -> List[Dict[str, Any]]:
    """Retrieve checklist of remediation items."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if target_host:
            cursor.execute("SELECT * FROM remediation_tasks WHERE target_host = ? ORDER BY id DESC", (target_host,))
        else:
            cursor.execute("SELECT * FROM remediation_tasks ORDER BY id DESC")
        return [dict(r) for r in cursor.fetchall()]


def update_remediation_status(task_id: int, new_status: str, notes: str = "", db_path: str = DATABASE_PATH) -> bool:
    """Update task lifecycle state (Open, In Progress, Fixed, Verified)."""
    init_db(db_path)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE remediation_tasks
            SET status = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, notes, now, task_id))
        conn.commit()
        return cursor.rowcount > 0


def seed_demo_history(db_path: str = DATABASE_PATH):
    """Seed realistic demonstration audit records for hackathon presentation."""
    init_db(db_path)
    # Check if already seeded
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scans")
        if cursor.fetchone()[0] > 0:
            return  # Already has records

    # Let's seed 3 historical scans showing realistic progression
    dates = [
        "2026-10-09T14:20:00Z",
        "2026-10-10T11:05:00Z",
        "2026-10-11T16:45:00Z",
    ]

    # Scan 1: Baseline City Hall Portal (Score 35)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        raw_s1 = json.dumps({
            "target_url": "https://portal.citygov.example.gov",
            "final_url": "https://portal.citygov.example.gov",
            "hostname": "portal.citygov.example.gov",
            "timestamp": dates[0],
            "status_code": 200,
            "resolved_ips": ["198.51.100.10"],
            "score_report": {"final_score": 35, "letter_grade": "F", "critical_high_count": 4},
            "response_headers": {"server": "Apache/2.4.41 (Ubuntu)", "x-powered-by": "PHP/7.4.3"}
        })
        cursor.execute("""
            INSERT INTO scans (
                target_url, final_url, hostname, timestamp, score, letter_grade,
                status_code, duration_ms, is_demo, total_checks, passed_checks,
                failed_checks, warning_checks, not_assessed_checks,
                critical_high_count, raw_json
            ) VALUES (
                'https://portal.citygov.example.gov', 'https://portal.citygov.example.gov', 'portal.citygov.example.gov',
                ?, 35, 'F', 200, 340, 1, 10, 2, 6, 2, 0, 4, ?
            )
        """, (dates[0], raw_s1))
        s1 = cursor.lastrowid

        # Insert some findings
        sample_findings = [
            (s1, "content_security_policy", "Content-Security-Policy (CSP)", "Injection Defense", SEV_HIGH, STATUS_FAIL, "Header absent", "Open"),
            (s1, "hsts_header", "HTTP Strict Transport Security (HSTS)", "Transport Layer Security", SEV_HIGH, STATUS_FAIL, "Header absent", "Open"),
            (s1, "x_frame_options", "Clickjacking Defense", "UI Redressing", SEV_MEDIUM, STATUS_FAIL, "Missing XFO", "Open"),
            (s1, "secure_cookies", "Cookie Security Attributes", "Session Integrity", SEV_MEDIUM, STATUS_FAIL, "Missing HttpOnly and Secure", "Open"),
            (s1, "server_disclosure", "Server Information Disclosure", "Information Disclosure", SEV_LOW, STATUS_FAIL, "Apache/2.4.41 leaked", "Open"),
        ]
        for f in sample_findings:
            cursor.execute("""
                INSERT INTO findings (scan_id, check_id, title, category, severity, status, evidence, why_it_matters, potential_impact, recommended_action, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Critical header', 'Risk', 'Fix config', ?)
            """, (f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7]))

        # Scan 2: State Health Portal (Score 65)
        raw_s2 = json.dumps({
            "target_url": "https://health.agency.example.gov",
            "final_url": "https://health.agency.example.gov",
            "hostname": "health.agency.example.gov",
            "timestamp": dates[1],
            "status_code": 200,
            "resolved_ips": ["198.51.100.20"],
            "score_report": {"final_score": 65, "letter_grade": "D", "critical_high_count": 2},
            "response_headers": {"server": "nginx/1.18.0", "strict-transport-security": "max-age=86400"}
        })
        cursor.execute("""
            INSERT INTO scans (
                target_url, final_url, hostname, timestamp, score, letter_grade,
                status_code, duration_ms, is_demo, total_checks, passed_checks,
                failed_checks, warning_checks, not_assessed_checks,
                critical_high_count, raw_json
            ) VALUES (
                'https://health.agency.example.gov', 'https://health.agency.example.gov', 'health.agency.example.gov',
                ?, 65, 'D', 200, 410, 1, 10, 5, 3, 2, 0, 2, ?
            )
        """, (dates[1], raw_s2))

        # Scan 3: Modernized Municipal Service (Score 92)
        raw_s3 = json.dumps({
            "target_url": "https://services.state.example.gov",
            "final_url": "https://services.state.example.gov",
            "hostname": "services.state.example.gov",
            "timestamp": dates[2],
            "status_code": 200,
            "resolved_ips": ["198.51.100.30"],
            "score_report": {"final_score": 92, "letter_grade": "A", "critical_high_count": 0},
            "response_headers": {
                "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
                "content-security-policy": "default-src 'self'",
                "x-frame-options": "DENY",
                "x-content-type-options": "nosniff"
            }
        })
        cursor.execute("""
            INSERT INTO scans (
                target_url, final_url, hostname, timestamp, score, letter_grade,
                status_code, duration_ms, is_demo, total_checks, passed_checks,
                failed_checks, warning_checks, not_assessed_checks,
                critical_high_count, raw_json
            ) VALUES (
                'https://services.state.example.gov', 'https://services.state.example.gov', 'services.state.example.gov',
                ?, 92, 'A', 200, 290, 1, 10, 8, 0, 2, 0, 0, ?
            )
        """, (dates[2], raw_s3))

        # Remediation tasks
        cursor.execute("""
            INSERT INTO remediation_tasks (target_host, check_id, title, status, notes, updated_at)
            VALUES
            ('portal.citygov.example.gov', 'content_security_policy', 'Content-Security-Policy (CSP)', 'In Progress', 'Nginx config tested on staging', ?),
            ('portal.citygov.example.gov', 'hsts_header', 'HTTP Strict Transport Security (HSTS)', 'Fixed', 'Applied max-age=31536000', ?),
            ('health.agency.example.gov', 'secure_cookies', 'Cookie Security Attributes', 'Open', 'Pending backend session cookie patch', ?)
        """, (dates[1], dates[2], dates[1]))

        conn.commit()
