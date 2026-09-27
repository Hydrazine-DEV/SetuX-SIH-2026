"""
SetuX / VeriX — Report Generation Configuration & Enums
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 17: Report Generation & PDF System
"""
from enum import Enum
from typing import Dict, Any
from reportlab.lib.colors import HexColor


class ReportType(str, Enum):
    PROJECT_SUMMARY = "PROJECT_SUMMARY"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    EARLY_WARNING = "EARLY_WARNING"
    EXECUTIVE_PROJECT_REPORT = "EXECUTIVE_PROJECT_REPORT"


REPORT_TITLES: Dict[str, str] = {
    ReportType.PROJECT_SUMMARY.value: "Project Summary & Baseline Status Report",
    ReportType.RISK_ASSESSMENT.value: "Comprehensive Project Risk Assessment Report",
    ReportType.EARLY_WARNING.value: "Early Warning & Active Alerts Bulletin",
    ReportType.EXECUTIVE_PROJECT_REPORT.value: "Executive Project Intelligence & Performance Brief",
}

# ─── Government-Grade Design System ──────────────────────────────
PDF_THEME = {
    "primary": HexColor("#1A365D"),       # Dark Navy
    "secondary": HexColor("#2B6CB0"),     # Steel Slate Blue
    "accent": HexColor("#2C5282"),        # Deep Accent Blue
    "dark_text": HexColor("#2D3748"),     # Charcoal Body Text
    "muted_text": HexColor("#718096"),    # Subdued Meta Text
    "light_bg": HexColor("#F7FAFC"),      # Off-white / Table Alternating
    "card_bg": HexColor("#EDF2F7"),       # Section Highlight Gray
    "border": HexColor("#CBD5E0"),        # Light Border
    "alert_critical": HexColor("#C53030"),# Crimson
    "alert_high": HexColor("#DD6B20"),    # Amber Orange
    "alert_medium": HexColor("#D69E2E"),  # Ochre Yellow
    "alert_low": HexColor("#319795"),     # Teal Green
}
