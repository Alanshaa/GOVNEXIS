"""Transparent Security Scoring Engine for GOVNEXIS.

Implements an explainable, deterministic scoring methodology grounded in
observed configuration checks:
- Score out of 100 based on weighted security standards (CISA BOD 18-01 / NIST SP 800-52).
- Full audit breakdown explaining points awarded, penalties, and excluded checks.
- Clear disclaimers and independent visibility of high-severity risks.
"""

from typing import List, Dict, Any
from core.config import (
    CHECK_WEIGHTS, STATUS_PASS, STATUS_FAIL, STATUS_WARNING, STATUS_NOT_ASSESSED,
    SEV_CRITICAL, SEV_HIGH
)
from core.security_checks import FindingRecord


class ScoreReport:
    """Detailed explainable security score breakdown."""

    def __init__(
        self,
        final_score: int,
        letter_grade: str,
        total_possible_points: int,
        earned_points: float,
        breakdown: List[Dict[str, Any]],
        critical_high_count: int,
        summary_statement: str,
        methodology_notes: str,
    ):
        self.final_score = final_score
        self.letter_grade = letter_grade
        self.total_possible_points = total_possible_points
        self.earned_points = earned_points
        self.breakdown = breakdown
        self.critical_high_count = critical_high_count
        self.summary_statement = summary_statement
        self.methodology_notes = methodology_notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_score": self.final_score,
            "letter_grade": self.letter_grade,
            "total_possible_points": self.total_possible_points,
            "earned_points": round(self.earned_points, 1),
            "breakdown": self.breakdown,
            "critical_high_count": self.critical_high_count,
            "summary_statement": self.summary_statement,
            "methodology_notes": self.methodology_notes,
        }


def calculate_grade(score: int, critical_high_count: int) -> str:
    """Calculate transparent letter grade reflecting both score and critical findings."""
    # Safety rule: If any CRITICAL finding exists, grade cannot exceed C
    if critical_high_count > 0 and score >= 80:
        if any(c == "Critical" for c in [critical_high_count]):
            return "B-"
    if score >= 90:
        return "A+" if score >= 95 else "A"
    elif score >= 80:
        return "B+" if score >= 85 else "B"
    elif score >= 70:
        return "C+" if score >= 75 else "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def compute_security_score(findings: List[FindingRecord]) -> ScoreReport:
    """Calculate the transparent security configuration score from audit findings."""
    total_assessed_possible = 0
    total_earned = 0.0
    breakdown: List[Dict[str, Any]] = []
    critical_high_count = 0

    findings_by_id = {f.check_id: f for f in findings}

    for check_id, meta in CHECK_WEIGHTS.items():
        weight = meta["weight"]
        finding = findings_by_id.get(check_id)

        if not finding:
            status = STATUS_NOT_ASSESSED
            earned = 0.0
            explanation = "Check was not evaluated in this scan pass."
        else:
            status = finding.status
            if finding.severity in (SEV_CRITICAL, SEV_HIGH) and status in (STATUS_FAIL, STATUS_WARNING):
                critical_high_count += 1

            if status == STATUS_PASS:
                earned = float(weight)
                explanation = f"Passed full standard (+{weight} pts)."
            elif status == STATUS_WARNING:
                # 50% partial credit for warning/contextual concern
                earned = float(weight) * 0.5
                explanation = f"Partial configuration (+{earned:.1f} pts, 50% penalty applied: {finding.evidence[:80]})."
            elif status == STATUS_FAIL:
                earned = 0.0
                explanation = f"Failed check (-{weight} pts: {finding.evidence[:80]})."
            else: # NOT_ASSESSED
                earned = 0.0
                explanation = "Excluded from scoring denominator (Not Assessed / Not Applicable)."

        if status != STATUS_NOT_ASSESSED:
            total_assessed_possible += weight
            total_earned += earned

        breakdown.append({
            "check_id": check_id,
            "title": meta["title"],
            "category": meta["category"],
            "status": status,
            "weight": weight,
            "points_earned": round(earned, 1),
            "explanation": explanation,
        })

    # Normalized score out of 100 based on evaluated checks
    if total_assessed_possible > 0:
        normalized_score = int(round((total_earned / total_assessed_possible) * 100))
    else:
        normalized_score = 0

    normalized_score = max(0, min(100, normalized_score))
    letter_grade = calculate_grade(normalized_score, critical_high_count)

    summary = (
        f"Overall Security Configuration Score: {normalized_score}/100 (Grade {letter_grade}). "
        f"Awarded {total_earned:.1f} of {total_assessed_possible} assessed points across {len(breakdown)} rules."
    )
    if critical_high_count > 0:
        summary += f" Attention: {critical_high_count} Critical or High severity configuration gap(s) require remediation."

    methodology = (
        "Methodology: The score is calculated deterministically using weighted security configuration checks "
        "derived from CISA BOD 18-01, NIST SP 800-52, and OWASP Secure Headers. PASS yields 100% of the assigned weight, "
        "WARNING yields 50%, and FAIL yields 0%. Checks marked NOT ASSESSED are excluded from the denominator. "
        "Disclaimer: This configuration audit evaluates web server response headers and TLS observations; "
        "it is not a substitute for comprehensive source code audits or authorized penetration testing."
    )

    return ScoreReport(
        final_score=normalized_score,
        letter_grade=letter_grade,
        total_possible_points=total_assessed_possible,
        earned_points=total_earned,
        breakdown=breakdown,
        critical_high_count=critical_high_count,
        summary_statement=summary,
        methodology_notes=methodology,
    )
