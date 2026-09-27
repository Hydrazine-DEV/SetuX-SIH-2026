"""
SetuX / VeriX — Professional PDF Report Generator
SIH26103: Integrated Government Project Monitoring & Intelligence Platform
Phase 17: Report Generation & PDF System

Implements ReportLab 5.0.1 Flowable Architecture with:
- NumberedCanvas (Dynamic Two-Pass Total Page Numbering & Running Headers/Footers)
- Government-Grade Visual Palette (Navy #1A365D, Slate #2B6CB0, Charcoal Text)
- Safe Paragraph Text Wrapping in all Table Cells
- Complete Handling for Missing / Sparse Project Baseline Values
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

from app.services.report_config import ReportType, REPORT_TITLES, PDF_THEME


# ─── Two-Pass Canvas for Page Numbering and Running Headers/Footers ──
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        page_w, page_h = A4
        margin = 36  # 0.5 inch

        # ── Top Running Header (Pages > 1) ──
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PDF_THEME["primary"])
            self.drawString(margin, page_h - 24, "SetuX | Integrated Government Project Monitoring & Intelligence Platform")
            self.setFont("Helvetica", 8)
            self.setFillColor(PDF_THEME["muted_text"])
            self.drawRightString(page_w - margin, page_h - 24, f"Confidential / Official Report")
            self.setStrokeColor(PDF_THEME["border"])
            self.setLineWidth(0.5)
            self.line(margin, page_h - 28, page_w - margin, page_h - 28)

        # ── Bottom Running Footer (All Pages) ──
        self.setStrokeColor(PDF_THEME["border"])
        self.setLineWidth(0.5)
        self.line(margin, 32, page_w - margin, 32)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(PDF_THEME["muted_text"])
        self.drawString(margin, 20, "SetuX • Generated from verified project monitoring data • SIH26103")

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - margin, 20, page_str)

        self.restoreState()


# ─── Stylesheet Setup ───────────────────────────────────────────
def get_pdf_styles() -> Dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="GovTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=PDF_THEME["primary"],
        alignment=TA_LEFT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="GovSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=PDF_THEME["muted_text"],
        alignment=TA_LEFT,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=PDF_THEME["primary"],
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="GovBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=PDF_THEME["dark_text"],
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="GovBodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=PDF_THEME["dark_text"],
    ))
    styles.add(ParagraphStyle(
        name="TableHead",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=HexColor("#FFFFFF"),
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=PDF_THEME["dark_text"],
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=PDF_THEME["dark_text"],
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="DisclaimerText",
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=PDF_THEME["muted_text"],
        spaceBefore=8,
    ))

    return styles


# ─── Helper Functions ───────────────────────────────────────────
def _safe_val(val: Any, default: str = "Not Available") -> str:
    """Format any value safely without None or empty strings."""
    if val is None or val == "" or str(val).strip() == "":
        return default
    return str(val)


def _build_key_value_table(kv_pairs: List[tuple], styles: Dict[str, ParagraphStyle], width: float = 523) -> Table:
    """Construct a clean two-column or four-column key-value summary table."""
    data = []
    for k, v in kv_pairs:
        data.append([
            Paragraph(f"<b>{k}</b>", styles["TableCellBold"]),
            Paragraph(_safe_val(v), styles["TableCell"]),
        ])

    col_w = [width * 0.35, width * 0.65]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PDF_THEME["light_bg"]),
        ("TEXTCOLOR", (0, 0), (-1, -1), PDF_THEME["dark_text"]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
        ("BOX", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _build_header_banner(title: str, project_code: str, report_type: str, styles: Dict[str, ParagraphStyle]) -> List[Any]:
    """Create the standard official SetuX document title banner."""
    flowables = []
    
    # Organization brand line
    flowables.append(Paragraph("GOVERNMENT INFRASTRUCTURE MONITORING PLATFORM • SETUX", styles["GovSubtitle"]))
    flowables.append(Paragraph(title, styles["GovTitle"]))

    meta_text = (
        f"<b>Project Code:</b> {_safe_val(project_code)} &nbsp;|&nbsp; "
        f"<b>Report Type:</b> {report_type} &nbsp;|&nbsp; "
        f"<b>Generated Date:</b> {datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')}"
    )
    flowables.append(Paragraph(meta_text, styles["GovSubtitle"]))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=PDF_THEME["primary"], spaceAfter=10))
    return flowables


# ─── 1. Project Summary PDF Builder ─────────────────────────────
def build_project_summary_pdf(data: Dict[str, Any], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    styles = get_pdf_styles()
    story = []

    p = data.get("project", {})
    code = p.get("project_code", "Unknown")

    # Header
    story.extend(_build_header_banner("Project Summary & Baseline Status Report", code, "PROJECT_SUMMARY", styles))

    # 1. Project Identity & Location
    story.append(Paragraph("1. Project Identity & Administrative Details", styles["SectionHeading"]))
    id_kv = [
        ("Project ID / Code", f"{p.get('id', 'N/A')} / {p.get('project_code', 'N/A')}"),
        ("Project Name", p.get("name")),
        ("Department", p.get("department_name")),
        ("Sector / Type", p.get("sector")),
        ("District / Taluka", f"{_safe_val(p.get('district'))} / {_safe_val(p.get('taluka'))}"),
        ("State / Location", f"{_safe_val(p.get('state'))} — {_safe_val(p.get('location'))}"),
        ("Contractor Name", p.get("contractor_name")),
        ("Current Execution Status", p.get("status")),
    ]
    story.append(_build_key_value_table(id_kv, styles))
    story.append(Spacer(1, 10))

    # 2. Financial Performance
    story.append(Paragraph("2. Financial Status & Budget Allocation", styles["SectionHeading"]))
    orig_c = p.get("original_cost")
    rev_c = p.get("revised_cost")
    exp = p.get("total_expenditure", 0.0)
    overrun_pct = data.get("cost_overrun_pct")
    fin_kv = [
        ("Original Sanctioned Cost", f"₹ {orig_c:.2f} Lakhs" if orig_c is not None else "Not Available"),
        ("Revised Approved Cost", f"₹ {rev_c:.2f} Lakhs" if rev_c is not None else "Not Available"),
        ("Total Disbursed Expenditure", f"₹ {exp:.2f} Lakhs" if exp is not None else "Not Available"),
        ("Cost Overrun Percentage", f"+{overrun_pct:.1f}%" if overrun_pct is not None else "0.0% (Within Budget)"),
        ("Financial Progress", f"{p.get('financial_progress', 0.0):.1f}%"),
    ]
    story.append(_build_key_value_table(fin_kv, styles))
    story.append(Spacer(1, 10))

    # 3. Schedule & Physical Execution Progress
    story.append(Paragraph("3. Schedule & Physical Progress", styles["SectionHeading"]))
    sched_kv = [
        ("Start Date", p.get("start_date")),
        ("Planned Completion Date", p.get("planned_completion_date")),
        ("Revised Completion Date", p.get("revised_completion_date", "None")),
        ("Physical Progress (Actual)", f"{p.get('physical_progress', 0.0):.1f}%"),
        ("Schedule Status", p.get("schedule_status", "Active Monitoring")),
    ]
    story.append(_build_key_value_table(sched_kv, styles))
    story.append(Spacer(1, 10))

    # 4. Milestone Execution Summary
    story.append(Paragraph("4. Milestones Summary", styles["SectionHeading"]))
    milestones = data.get("milestones", [])
    if milestones:
        m_table_data = [[
            Paragraph("<b>#</b>", styles["TableHead"]),
            Paragraph("<b>Milestone Name</b>", styles["TableHead"]),
            Paragraph("<b>Target Date</b>", styles["TableHead"]),
            Paragraph("<b>Status</b>", styles["TableHead"]),
            Paragraph("<b>Completion</b>", styles["TableHead"]),
        ]]
        for idx, m in enumerate(milestones, 1):
            m_table_data.append([
                Paragraph(str(idx), styles["TableCell"]),
                Paragraph(_safe_val(m.get("name")), styles["TableCell"]),
                Paragraph(_safe_val(m.get("planned_date")), styles["TableCell"]),
                Paragraph(_safe_val(m.get("status")), styles["TableCellBold"]),
                Paragraph(f"{m.get('completion_percentage', 0.0):.1f}%", styles["TableCell"]),
            ])
        t_milestones = Table(m_table_data, colWidths=[25, 230, 95, 90, 83])
        t_milestones.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_THEME["primary"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("BOX", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_milestones)
    else:
        story.append(Paragraph("No milestones configured for this project.", styles["GovBody"]))
    story.append(Spacer(1, 10))

    # 5. Issues Summary
    story.append(Paragraph("5. Project Issues & Obstructions", styles["SectionHeading"]))
    issues = data.get("issues", [])
    if issues:
        i_table_data = [[
            Paragraph("<b>ID</b>", styles["TableHead"]),
            Paragraph("<b>Issue Title</b>", styles["TableHead"]),
            Paragraph("<b>Severity</b>", styles["TableHead"]),
            Paragraph("<b>Status</b>", styles["TableHead"]),
            Paragraph("<b>Reported Date</b>", styles["TableHead"]),
        ]]
        for iss in issues:
            i_table_data.append([
                Paragraph(str(iss.get("id")), styles["TableCell"]),
                Paragraph(_safe_val(iss.get("title")), styles["TableCell"]),
                Paragraph(_safe_val(iss.get("severity")), styles["TableCellBold"]),
                Paragraph(_safe_val(iss.get("status")), styles["TableCell"]),
                Paragraph(_safe_val(iss.get("reported_date")), styles["TableCell"]),
            ])
        t_issues = Table(i_table_data, colWidths=[30, 235, 80, 85, 93])
        t_issues.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_THEME["secondary"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("BOX", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_issues)
    else:
        story.append(Paragraph("No open or recorded issues for this project.", styles["GovBody"]))

    doc.build(story, canvasmaker=NumberedCanvas)


# ─── 2. Risk Assessment PDF Builder ─────────────────────────────
def build_risk_assessment_pdf(data: Dict[str, Any], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    styles = get_pdf_styles()
    story = []

    p = data.get("project", {})
    code = p.get("project_code", "Unknown")
    risk_intel = data.get("risk_intelligence", {})
    overall_risk = risk_intel.get("overall_risk", {})

    story.extend(_build_header_banner("Comprehensive Project Risk Assessment Report", code, "RISK_ASSESSMENT", styles))

    # 1. Executive Risk Overview
    story.append(Paragraph("1. Executive Risk Score & Classification", styles["SectionHeading"]))
    score = overall_risk.get("score", 0.0)
    level = overall_risk.get("level", "LOW")
    baseline = overall_risk.get("rule_based_baseline_score", "N/A")
    pred_score = overall_risk.get("predictive_ml_score", "N/A")

    risk_summary_kv = [
        ("Overall Engineering Risk Score", f"{score:.2f} / 100.00"),
        ("Assessed Risk Level", level),
        ("Rule-Based Observed Baseline Score", f"{baseline} / 100.00" if isinstance(baseline, (int, float)) else str(baseline)),
        ("Predictive ML Component Score", f"{pred_score} / 100.00" if isinstance(pred_score, (int, float)) else str(pred_score)),
        ("Calculation Version & Model", f"{overall_risk.get('calculation_name', 'SetuX Risk Engine')} ({overall_risk.get('version', 'v1.0.0')})"),
    ]
    story.append(_build_key_value_table(risk_summary_kv, styles))
    story.append(Spacer(1, 10))

    # 2. Observed Risk Factors (Rule-Based Engine)
    story.append(Paragraph("2. Observed Field Conditions (Deterministic Rule Engine)", styles["SectionHeading"]))
    observed_factors = risk_intel.get("observed_factors", [])
    if observed_factors:
        obs_data = [[
            Paragraph("<b>Risk Factor</b>", styles["TableHead"]),
            Paragraph("<b>Severity</b>", styles["TableHead"]),
            Paragraph("<b>Score Contrib.</b>", styles["TableHead"]),
            Paragraph("<b>Explanation & Evidence</b>", styles["TableHead"]),
        ]]
        for f in observed_factors:
            obs_data.append([
                Paragraph(f.get("factor", "").replace("_", " ").title(), styles["TableCellBold"]),
                Paragraph(f.get("severity", "LOW"), styles["TableCellBold"]),
                Paragraph(f"+{f.get('score_contribution', 0.0):.1f}", styles["TableCell"]),
                Paragraph(_safe_val(f.get("explanation")), styles["TableCell"]),
            ])
        t_obs = Table(obs_data, colWidths=[140, 65, 65, 253])
        t_obs.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_THEME["primary"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("BOX", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t_obs)
    else:
        story.append(Paragraph("No elevated observed risk factors detected on project site.", styles["GovBody"]))
    story.append(Spacer(1, 10))

    # 3. Machine Learning Predictive Overrun Forecasts
    story.append(Paragraph("3. Machine Learning Predictive Forecasts", styles["SectionHeading"]))
    cost_ml = risk_intel.get("cost_overrun_prediction", {})
    time_ml = risk_intel.get("time_overrun_prediction", {})

    cost_prob = cost_ml.get("probability", 0.0) if cost_ml.get("is_available") else None
    time_prob = time_ml.get("probability", 0.0) if time_ml.get("is_available") else None

    ml_kv = [
        ("Cost Overrun ML Prediction", f"Estimated {round(cost_prob * 100, 1)}% Probability of Cost Escalation" if cost_prob is not None else "Model Unavailable (Insufficient Baseline)"),
        ("Cost ML Model Version", cost_ml.get("model_name", "SetuX Cost Predictor v1.0.0")),
        ("Time Overrun ML Prediction", f"Estimated {round(time_prob * 100, 1)}% Probability of Schedule Delay" if time_prob is not None else "Model Unavailable (Insufficient Baseline)"),
        ("Time ML Model Version", time_ml.get("model_name", "SetuX Time Predictor v1.0.0")),
    ]
    story.append(_build_key_value_table(ml_kv, styles))
    story.append(Spacer(1, 10))

    # 4. Data Quality & Limitations
    story.append(Paragraph("4. Data Quality, Completeness & Methodological Disclaimer", styles["SectionHeading"]))
    dq = risk_intel.get("data_quality", {})
    missing = dq.get("missing_data_fields", [])
    dq_text = (
        f"<b>Data Quality Status:</b> {dq.get('status', 'COMPLETE')}<br/>"
        f"<b>Missing Baseline Fields:</b> {', '.join(missing) if missing else 'None (All baseline fields available)'}<br/>"
        f"<i>Disclaimer: The SetuX overall risk score is an engineering decision-support metric combining observed indicators and statistical model outputs. Predictive probabilities indicate statistical risk elevation and are not guarantees of project failure.</i>"
    )
    story.append(Paragraph(dq_text, styles["GovBody"]))

    doc.build(story, canvasmaker=NumberedCanvas)


# ─── 3. Early Warning PDF Builder ───────────────────────────────
def build_early_warning_pdf(data: Dict[str, Any], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    styles = get_pdf_styles()
    story = []

    p = data.get("project", {})
    code = p.get("project_code", "Unknown")
    alerts = data.get("alerts", [])

    story.extend(_build_header_banner("Early Warning & Active Alerts Bulletin", code, "EARLY_WARNING", styles))

    # Alert Count Summary
    critical_cnt = sum(1 for a in alerts if (a.get("severity") or "").upper() == "CRITICAL")
    high_cnt = sum(1 for a in alerts if (a.get("severity") or "").upper() == "HIGH")
    medium_cnt = sum(1 for a in alerts if (a.get("severity") or "").upper() == "MEDIUM")
    low_cnt = sum(1 for a in alerts if (a.get("severity") or "").upper() == "LOW")

    summary_kv = [
        ("Total Monitored Alerts", str(len(alerts))),
        ("Critical Severity Alerts", str(critical_cnt)),
        ("High Severity Alerts", str(high_cnt)),
        ("Medium Severity Alerts", str(medium_cnt)),
        ("Low Severity Notices", str(low_cnt)),
    ]
    story.append(Paragraph("1. Alert Level Distribution", styles["SectionHeading"]))
    story.append(_build_key_value_table(summary_kv, styles))
    story.append(Spacer(1, 10))

    # Alert Table Grouped by Severity
    story.append(Paragraph("2. Active & Historical Alert Details", styles["SectionHeading"]))
    if alerts:
        # Sort by severity priority: CRITICAL -> HIGH -> MEDIUM -> LOW
        sev_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        sorted_alerts = sorted(alerts, key=lambda a: sev_order.get((a.get("severity") or "").upper(), 5))

        a_table_data = [[
            Paragraph("<b>Sev.</b>", styles["TableHead"]),
            Paragraph("<b>Alert Type</b>", styles["TableHead"]),
            Paragraph("<b>Title & Description</b>", styles["TableHead"]),
            Paragraph("<b>Source</b>", styles["TableHead"]),
            Paragraph("<b>Status</b>", styles["TableHead"]),
        ]]
        for a in sorted_alerts:
            title_msg = f"<b>{_safe_val(a.get('title'))}</b><br/>{_safe_val(a.get('message'))}"
            a_table_data.append([
                Paragraph(_safe_val(a.get("severity")), styles["TableCellBold"]),
                Paragraph(_safe_val(a.get("alert_type")), styles["TableCell"]),
                Paragraph(title_msg, styles["TableCell"]),
                Paragraph(_safe_val(a.get("source")), styles["TableCell"]),
                Paragraph(_safe_val(a.get("status")), styles["TableCellBold"]),
            ])
        t_alerts = Table(a_table_data, colWidths=[55, 105, 235, 75, 53])
        t_alerts.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PDF_THEME["primary"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("BOX", (0, 0), (-1, -1), 0.5, PDF_THEME["border"]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_alerts)
    else:
        story.append(Paragraph("No early warning alerts recorded for this project.", styles["GovBody"]))

    doc.build(story, canvasmaker=NumberedCanvas)


# ─── 4. Executive Project Report PDF Builder ────────────────────
def build_executive_report_pdf(data: Dict[str, Any], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=40, bottomMargin=40)
    styles = get_pdf_styles()
    story = []

    p = data.get("project", {})
    code = p.get("project_code", "Unknown")
    risk_intel = data.get("risk_intelligence", {})
    overall_risk = risk_intel.get("overall_risk", {})
    alerts = data.get("alerts", [])

    story.extend(_build_header_banner("Executive Project Intelligence & Performance Brief", code, "EXECUTIVE_PROJECT_REPORT", styles))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary & Overview", styles["SectionHeading"]))
    exec_summary_text = (
        f"This executive brief consolidates operational, financial, and predictive risk telemetry for "
        f"project <b>{_safe_val(p.get('name'))}</b> ({code}), under the <b>{_safe_val(p.get('department_name'))}</b>. "
        f"Overall risk is currently evaluated as <b>{overall_risk.get('level', 'LOW')}</b> with a composite score of "
        f"<b>{overall_risk.get('score', 0.0):.1f}/100</b>."
    )
    story.append(Paragraph(exec_summary_text, styles["GovBody"]))
    story.append(Spacer(1, 6))

    overview_kv = [
        ("Project Name", p.get("name")),
        ("Department / Sector", f"{_safe_val(p.get('department_name'))} / {_safe_val(p.get('sector'))}"),
        ("District / Location", f"{_safe_val(p.get('district'))} — {_safe_val(p.get('location'))}"),
        ("Contractor", p.get("contractor_name")),
        ("Current Execution Status", p.get("status")),
    ]
    story.append(_build_key_value_table(overview_kv, styles))
    story.append(Spacer(1, 10))

    # 2. Key Performance Indicators
    story.append(Paragraph("2. Key Performance Indicators (Physical, Financial, Schedule)", styles["SectionHeading"]))
    orig_c = p.get("original_cost")
    rev_c = p.get("revised_cost")
    exp = p.get("total_expenditure", 0.0)
    overrun_pct = data.get("cost_overrun_pct")

    kpi_kv = [
        ("Physical Progress", f"{p.get('physical_progress', 0.0):.1f}%"),
        ("Financial Progress", f"{p.get('financial_progress', 0.0):.1f}%"),
        ("Original / Revised Budget", f"₹ {orig_c:.2f}L / ₹ {rev_c:.2f}L" if (orig_c is not None and rev_c is not None) else "Not Available"),
        ("Disbursed Expenditure", f"₹ {exp:.2f} Lakhs" if exp is not None else "Not Available"),
        ("Cost Overrun %", f"+{overrun_pct:.1f}%" if overrun_pct is not None else "0.0%"),
        ("Timeline Planned", f"{p.get('start_date')} to {p.get('planned_completion_date')}"),
    ]
    story.append(_build_key_value_table(kpi_kv, styles))
    story.append(Spacer(1, 10))

    # 3. Risk Intelligence & ML Predictive Forecast
    story.append(Paragraph("3. Risk Intelligence & Forecasts", styles["SectionHeading"]))
    cost_ml = risk_intel.get("cost_overrun_prediction", {})
    time_ml = risk_intel.get("time_overrun_prediction", {})
    c_prob = cost_ml.get("probability") if cost_ml.get("is_available") else None
    t_prob = time_ml.get("probability") if time_ml.get("is_available") else None

    risk_kv = [
        ("Overall Assessed Risk", f"{overall_risk.get('level', 'LOW')} ({overall_risk.get('score', 0.0):.1f}/100)"),
        ("Observed Baseline Score", f"{overall_risk.get('rule_based_baseline_score', 'N/A')} / 100"),
        ("Cost Overrun ML Forecast", f"{round(c_prob * 100, 1)}% Probability" if c_prob is not None else "Unavailable"),
        ("Time Overrun ML Forecast", f"{round(t_prob * 100, 1)}% Probability" if t_prob is not None else "Unavailable"),
    ]
    story.append(_build_key_value_table(risk_kv, styles))
    story.append(Spacer(1, 10))

    # 4. Early Warnings & Alerts
    story.append(Paragraph("4. Early Warnings Summary", styles["SectionHeading"]))
    if alerts:
        alert_lines = [f"• <b>[{a.get('severity')}] {a.get('title')}</b>: {a.get('message')}" for a in alerts[:5]]
        story.append(Paragraph("<br/>".join(alert_lines), styles["GovBody"]))
    else:
        story.append(Paragraph("No active alerts triggered for this project.", styles["GovBody"]))
    story.append(Spacer(1, 10))

    # 5. Suggested Officer Actions (Derived from Structured Evidence)
    story.append(Paragraph("5. Recommended Officer Actions", styles["SectionHeading"]))
    recs = []
    if overrun_pct and overrun_pct > 10:
        recs.append("1. Audit financial disbursements against verified on-site milestone progress to control budget deviation.")
    if p.get("status") == "DELAYED" or (t_prob and t_prob > 0.5):
        recs.append("2. Issue a formal schedule rectification notice to the contractor requiring an updated recovery schedule.")
    if any(a.get("severity") == "CRITICAL" for a in alerts):
        recs.append("3. Conduct an immediate joint physical inspection with the department executive engineer.")
    if not recs:
        recs.append("1. Maintain standard periodic progress monitoring and verify photographic milestone evidence.")

    story.append(Paragraph("<br/>".join(recs), styles["GovBody"]))

    doc.build(story, canvasmaker=NumberedCanvas)
