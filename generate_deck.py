import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import win32com.client

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Colors
    NAVY = RGBColor(27, 54, 93)          # #1B365D
    DARK_TEXT = RGBColor(15, 23, 42)     # #0F172A
    MUTED_TEXT = RGBColor(71, 85, 105)   # #475569
    CARD_BG = RGBColor(241, 245, 249)    # #F1F5F9
    CARD_BORDER = RGBColor(203, 213, 225)# #CBD5E1
    WHITE = RGBColor(255, 255, 255)
    PEACH_BG = RGBColor(254, 237, 222)   # #FEEDE6
    PEACH_BORDER = RGBColor(249, 115, 22)# #F97316
    LIGHT_BLUE = RGBColor(235, 245, 255) # #EBF5FF
    BLUE_BORDER = RGBColor(59, 130, 246) # #3B82F6
    GREEN = RGBColor(34, 197, 94)
    ORANGE = RGBColor(249, 115, 22)
    GRAY_LINE = RGBColor(148, 163, 184)
    
    SIH_LOGO_PATH = os.path.abspath("presentation_assets/sih_logo.png")
    SLIDE1_EMBLEM_PATH = os.path.abspath("presentation_assets/slide1_emblem.png")
    DASH1_PATH = os.path.abspath("presentation_assets/setux_dashboard_1.png")
    DASH2_PATH = os.path.abspath("presentation_assets/setux_dashboard_2.png")

    # Helper function to add standard header for slides 2-6
    def add_standard_header(slide, title_text, subtitle_text=None):
        # 1. Top Left Badge (Team VeriX)
        badge = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(0.4), Inches(0.25), Inches(1.35), Inches(0.8)
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(226, 232, 240)
        badge.line.color.rgb = NAVY
        badge.line.width = Pt(2)
        tf = badge.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = "Team\nVeriX"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        p.alignment = PP_ALIGN.CENTER

        # 2. Top Center Title
        title_box = slide.shapes.add_textbox(
            Inches(2.0), Inches(0.15), Inches(8.8), Inches(1.0)
        )
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(32)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        p_title.font.name = "Georgia"
        p_title.alignment = PP_ALIGN.CENTER
        
        if subtitle_text:
            p_sub = tf_title.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(15)
            p_sub.font.italic = True
            p_sub.font.color.rgb = MUTED_TEXT
            p_sub.font.name = "Georgia"
            p_sub.alignment = PP_ALIGN.CENTER

        # 3. Top Right SIH Logo
        if os.path.exists(SIH_LOGO_PATH):
            slide.shapes.add_picture(
                SIH_LOGO_PATH,
                Inches(11.0), Inches(0.2), width=Inches(2.0), height=Inches(0.85)
            )

    # Helper function to add slide number
    def add_slide_number(slide, num_str):
        num_box = slide.shapes.add_textbox(
            Inches(12.5), Inches(7.0), Inches(0.6), Inches(0.4)
        )
        tf = num_box.text_frame
        p = tf.paragraphs[0]
        p.text = num_str
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.alignment = PP_ALIGN.RIGHT

    # =========================================================
    # SLIDE 1: SMART INDIA HACKATHON 2026 / PROBLEM STATEMENT
    # =========================================================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Title
    tbox1 = slide1.shapes.add_textbox(Inches(0.8), Inches(0.3), Inches(9.5), Inches(0.9))
    tf1 = tbox1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "SMART INDIA HACKATHON 2026"
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = NAVY
    p1.font.name = "Georgia"
    
    # Top Right SIH Logo
    if os.path.exists(SIH_LOGO_PATH):
        slide1.shapes.add_picture(
            SIH_LOGO_PATH,
            Inches(11.0), Inches(0.2), width=Inches(2.0), height=Inches(0.85)
        )
        
    # Left Content Box
    cbox1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.4))
    tf_c1 = cbox1.text_frame
    tf_c1.word_wrap = True
    
    items1 = [
        ("Problem Statement ID – ", "SIH26103"),
        ("Problem Statement Title - ", "Integrated Government Project Monitoring & Intelligence Platform"),
        ("Theme - ", "Infrastructure & Governance"),
        ("PS Category - ", "Software"),
        ("Team ID - ", "SIH2026-VX103"),
        ("Team Name - ", "Team VeriX"),
        ("Project Name - ", "SetuX (\"From Reported Progress to Verified Progress\")")
    ]
    
    for i, (k, v) in enumerate(items1):
        p = tf_c1.paragraphs[0] if i == 0 else tf_c1.add_paragraph()
        p.space_after = Pt(18)
        p.level = 0
        
        # Bullet symbol
        run_bullet = p.add_run()
        run_bullet.text = "• "
        run_bullet.font.bold = True
        run_bullet.font.size = Pt(17)
        run_bullet.font.color.rgb = DARK_TEXT
        
        # Key
        run_k = p.add_run()
        run_k.text = k
        run_k.font.bold = True
        run_k.font.size = Pt(17)
        run_k.font.color.rgb = DARK_TEXT
        
        # Value
        run_v = p.add_run()
        run_v.text = v
        run_v.font.bold = False
        run_v.font.size = Pt(17)
        run_v.font.color.rgb = DARK_TEXT

    # Right Emblem
    if os.path.exists(SLIDE1_EMBLEM_PATH):
        slide1.shapes.add_picture(
            SLIDE1_EMBLEM_PATH,
            Inches(8.0), Inches(1.3), width=Inches(4.8), height=Inches(5.6)
        )

    # =========================================================
    # SLIDE 2: PROPOSED SOLUTION / APPROACH
    # =========================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_standard_header(slide2, "SetuX", "Bridging Infrastructure Monitoring to Verified Progress")
    
    # Left Card Container (Proposed Solution & Approach)
    left_card = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.4), Inches(1.2), Inches(4.3), Inches(5.6)
    )
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = RGBColor(235, 241, 246)
    left_card.line.color.rgb = CARD_BORDER
    left_card.line.width = Pt(1.5)
    
    # Card Header
    lhead = slide2.shapes.add_textbox(Inches(0.6), Inches(1.25), Inches(3.9), Inches(0.7))
    tf_lh = lhead.text_frame
    tf_lh.word_wrap = True
    p = tf_lh.paragraphs[0]
    p.text = "Proposed Solution\n& Approach"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = DARK_TEXT
    
    # 6 Numbered badges inside Left Card
    sol_items = [
        ("01", "Project Monitoring:", "Centralized tracking of physical, financial, and milestone status across all projects."),
        ("02", "Progress & Evidence:", "Multi-source progress backed by geo-tagged photos, documents & inspection logs."),
        ("03", "Risk Intelligence:", "Multi-factor scoring evaluating milestone delays, cost escalation & vendor risk."),
        ("04", "Predictive Analytics:", "Machine learning models forecasting potential cost overruns and schedule delays."),
        ("05", "Early Warnings:", "Proactive alerts and trigger thresholds notifying officers before slippage escalates."),
        ("06", "Executive Reporting:", "Automated, audit-ready briefing reports and executive dashboards for quick decisions.")
    ]
    
    # Vertical connector line
    vline = slide2.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.82), Inches(2.1), Inches(0.04), Inches(4.4)
    )
    vline.fill.solid()
    vline.fill.fore_color.rgb = RGBColor(148, 163, 184)
    vline.line.fill.background()
    
    for idx, (num, title, desc) in enumerate(sol_items):
        y_pos = 2.05 + idx * 0.77
        
        # Circle badge
        cbadge = slide2.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(0.65), Inches(y_pos), Inches(0.38), Inches(0.38)
        )
        cbadge.fill.solid()
        cbadge.fill.fore_color.rgb = RGBColor(100, 116, 139)
        cbadge.line.fill.background()
        tf = cbadge.text_frame
        p = tf.paragraphs[0]
        p.text = str(idx + 1)
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
        # Text box
        tbox = slide2.shapes.add_textbox(Inches(1.1), Inches(y_pos - 0.08), Inches(3.5), Inches(0.72))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0)
        tf.margin_left = Inches(0)
        p = tf.paragraphs[0]
        
        r_title = p.add_run()
        r_title.text = title + " "
        r_title.font.bold = True
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = DARK_TEXT
        
        r_desc = p.add_run()
        r_desc.text = desc
        r_desc.font.size = Pt(10)
        r_desc.font.color.rgb = MUTED_TEXT

    # Right Top Flow Progression (5 stages)
    stages = [
        ("Project Ingestion", "📋"),
        ("Field Evidence", "📷"),
        ("Risk Intelligence", "⚡"),
        ("Command Center", "📊"),
        ("Verified Outcomes", "👥")
    ]
    for s_idx, (stitle, sicon) in enumerate(stages):
        x = 5.0 + s_idx * 1.6
        sbox = slide2.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(1.2), Inches(1.35), Inches(0.7)
        )
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = CARD_BG
        sbox.line.color.rgb = CARD_BORDER
        tf = sbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{sicon} {stitle}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        p.alignment = PP_ALIGN.CENTER
        
        # Arrow between stages
        if s_idx < len(stages) - 1:
            arr = slide2.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(x + 1.38), Inches(1.42), Inches(0.18), Inches(0.2)
            )
            arr.fill.solid()
            arr.fill.fore_color.rgb = RGBColor(100, 116, 139)
            arr.line.fill.background()

    # Right Middle: "End-to-End Workflow" Container
    wf_box = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(4.9), Inches(2.1), Inches(8.0), Inches(3.7)
    )
    wf_box.fill.solid()
    wf_box.fill.fore_color.rgb = WHITE
    wf_box.line.color.rgb = CARD_BORDER
    
    # Workflow Header Badge
    wf_badge = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(7.6), Inches(2.2), Inches(2.5), Inches(0.35)
    )
    wf_badge.fill.solid()
    wf_badge.fill.fore_color.rgb = RGBColor(235, 245, 255)
    wf_badge.line.color.rgb = BLUE_BORDER
    tf = wf_badge.text_frame
    p = tf.paragraphs[0]
    p.text = "End-to-End Workflow"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    
    # 8 Workflow Steps
    wf_steps = [
        ("1. Data Ingestion", "Project Plans, BOQ, Milestones", RGBColor(37, 99, 235)),
        ("2. Field Evidence", "Geo-photos, Inspections", RGBColor(22, 163, 74)),
        ("3. AI/ML Predict", "Delay & Cost Forecaster", RGBColor(124, 58, 237)),
        ("4. Risk Fusion", "Multi-Factor Scoring", RGBColor(220, 38, 38)),
        ("5. Risk & Impact", "GIS Heatmap & Slippage", RGBColor(217, 119, 6)),
        ("6. Early Alerts", "Escalation Warnings", RGBColor(13, 148, 136)),
        ("7. Officer Action", "Intervention & Review", RGBColor(2, 132, 199)),
        ("8. Stakeholders", "Audit Logs & Public View", RGBColor(109, 40, 217))
    ]
    
    for w_idx, (w_title, w_sub, w_col) in enumerate(wf_steps):
        wx = 5.05 + w_idx * 0.96
        
        # Step Header Card
        wcard = slide2.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(wx), Inches(2.7), Inches(0.9), Inches(0.4)
        )
        wcard.fill.solid()
        wcard.fill.fore_color.rgb = w_col
        wcard.line.fill.background()
        tf = wcard.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = w_title
        p.font.size = Pt(8)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
        # Step Detail Box Below
        wdet = slide2.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(wx), Inches(3.2), Inches(0.9), Inches(1.5)
        )
        wdet.fill.solid()
        wdet.fill.fore_color.rgb = RGBColor(248, 250, 252)
        wdet.line.color.rgb = CARD_BORDER
        tf = wdet.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = w_sub
        p.font.size = Pt(8)
        p.font.color.rgb = DARK_TEXT
        p.alignment = PP_ALIGN.CENTER
        
        # Arrow
        if w_idx < len(wf_steps) - 1:
            arr = slide2.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(wx + 0.91), Inches(3.8), Inches(0.04), Inches(0.12)
            )
            arr.fill.solid()
            arr.fill.fore_color.rgb = RGBColor(148, 163, 184)
            arr.line.fill.background()

    # Continuous Verification Loop Bar
    loop_box = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.8), Inches(4.9), Inches(4.2), Inches(0.7)
    )
    loop_box.fill.solid()
    loop_box.fill.fore_color.rgb = RGBColor(235, 245, 255)
    loop_box.line.color.rgb = BLUE_BORDER
    tf = loop_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Continuous Verification & Audit Trail"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "(Field inspections, milestone validations, verified outcomes)"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = MUTED_TEXT
    p2.alignment = PP_ALIGN.CENTER

    # Right Bottom Link Badges
    btn1 = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(5.6), Inches(5.95), Inches(2.8), Inches(0.65)
    )
    btn1.fill.solid()
    btn1.fill.fore_color.rgb = WHITE
    btn1.line.color.rgb = CARD_BORDER
    tf = btn1.text_frame
    p = tf.paragraphs[0]
    p.text = "🌐 Hosted Application\nClick here"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    
    btn2 = slide2.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(9.2), Inches(5.95), Inches(2.8), Inches(0.65)
    )
    btn2.fill.solid()
    btn2.fill.fore_color.rgb = WHITE
    btn2.line.color.rgb = CARD_BORDER
    tf = btn2.text_frame
    p = tf.paragraphs[0]
    p.text = "🐙 GitHub Repository\nClick Here"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DARK_TEXT
    p.alignment = PP_ALIGN.CENTER

    # Bottom Full Width Navy Banner
    bot_banner = slide2.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(6.9), Inches(13.333), Inches(0.6)
    )
    bot_banner.fill.solid()
    bot_banner.fill.fore_color.rgb = NAVY
    bot_banner.line.fill.background()
    tf = bot_banner.text_frame
    p = tf.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    # =========================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_standard_header(slide3, "TECHNICAL APPROACH")
    add_slide_number(slide3, "3")
    
    # Left Sidebar: "Technology Used"
    l_tech_title = slide3.shapes.add_textbox(Inches(0.4), Inches(1.15), Inches(2.4), Inches(0.4))
    tf = l_tech_title.text_frame
    p = tf.paragraphs[0]
    p.text = "Technology Used"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_TEXT
    
    tech_stacks = [
        ("Data Sources", "• Project Plans / DPR\n• Milestone Schedules\n• Financials / BOQ\n• Geo-coordinates"),
        ("Data Processing", "• Python / FastAPI\n• Pydantic Schemas\n• SQLAlchemy ORM\n• NumPy / Pandas"),
        ("AI/ML Model", "• scikit-learn Engine\n• Cost Overrun Regr.\n• Delay Risk Classifier\n• Rule Risk Indicators"),
        ("Database", "• SQLite (MVP)\n• PostgreSQL Schema\n• Audit Event Logs"),
        ("Maps & GIS", "• Leaflet / OSM\n• GeoJSON Pins & Poly\n• Spatial Risk Heatmap"),
        ("User Interface", "• React 18 / Vite\n• Tailwind CSS\n• Recharts Analytics\n• Lucide Icons"),
        ("Deployment", "• Uvicorn ASGI\n• RESTful Architecture\n• GitHub / Docker")
    ]
    
    for t_idx, (t_name, t_body) in enumerate(tech_stacks):
        ty = 1.6 + t_idx * 0.77
        tcard = slide3.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.4), Inches(ty), Inches(2.2), Inches(0.72)
        )
        tcard.fill.solid()
        tcard.fill.fore_color.rgb = PEACH_BG
        tcard.line.color.rgb = PEACH_BORDER
        tcard.line.width = Pt(1.5)
        tf = tcard.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        
        p = tf.paragraphs[0]
        p.text = t_name
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        
        p2 = tf.add_paragraph()
        p2.text = t_body
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = DARK_TEXT

    # Right Area: "Work Flow Diagram" Container
    wf_main = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(2.8), Inches(1.2), Inches(10.1), Inches(5.6)
    )
    wf_main.fill.solid()
    wf_main.fill.fore_color.rgb = WHITE
    wf_main.line.color.rgb = CARD_BORDER
    
    # Workflow Header Badge
    wf_hdr = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.8), Inches(1.35), Inches(2.4), Inches(0.35)
    )
    wf_hdr.fill.solid()
    wf_hdr.fill.fore_color.rgb = RGBColor(235, 245, 255)
    wf_hdr.line.color.rgb = BLUE_BORDER
    tf = wf_hdr.text_frame
    p = tf.paragraphs[0]
    p.text = "Work Flow Diagram"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    
    # Flowchart Blocks
    # 1. User -> Open SetuX
    b_user = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(3.0), Inches(2.5), Inches(0.65), Inches(0.55)
    )
    b_user.fill.solid()
    b_user.fill.fore_color.rgb = LIGHT_BLUE
    b_user.line.color.rgb = BLUE_BORDER
    b_user.text_frame.paragraphs[0].text = "User / Officer"
    b_user.text_frame.paragraphs[0].font.size = Pt(8.5)
    b_user.text_frame.paragraphs[0].font.bold = True
    b_user.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    b_open = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(3.8), Inches(2.5), Inches(0.85), Inches(0.55)
    )
    b_open.fill.solid()
    b_open.fill.fore_color.rgb = LIGHT_BLUE
    b_open.line.color.rgb = BLUE_BORDER
    b_open.text_frame.paragraphs[0].text = "Open SetuX Platform"
    b_open.text_frame.paragraphs[0].font.size = Pt(8.5)
    b_open.text_frame.paragraphs[0].font.bold = True
    b_open.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 2. Ingestion & Map
    b_live = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(4.8), Inches(1.9), Inches(1.2), Inches(0.85)
    )
    b_live.fill.solid()
    b_live.fill.fore_color.rgb = LIGHT_BLUE
    b_live.line.color.rgb = BLUE_BORDER
    tf = b_live.text_frame
    p = tf.paragraphs[0]
    p.text = "View Live GIS Map\n(Leaflet + OSM)"
    p.font.size = Pt(8.5)
    p.alignment = PP_ALIGN.CENTER
    
    b_up = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(4.8), Inches(3.0), Inches(1.2), Inches(0.85)
    )
    b_up.fill.solid()
    b_up.fill.fore_color.rgb = LIGHT_BLUE
    b_up.line.color.rgb = BLUE_BORDER
    tf = b_up.text_frame
    p = tf.paragraphs[0]
    p.text = "Submit Evidence\n(Photos / Logs / BOQ)\n(FastAPI + SQLite)"
    p.font.size = Pt(8)
    p.alignment = PP_ALIGN.CENTER

    # 3. Data Processing & AI Prediction
    b_proc = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.2), Inches(1.9), Inches(1.7), Inches(2.0)
    )
    b_proc.fill.solid()
    b_proc.fill.fore_color.rgb = LIGHT_BLUE
    b_proc.line.color.rgb = BLUE_BORDER
    tf = b_proc.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Data Processing & AI\n"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf.add_paragraph()
    p2.text = "• Ingestion Preprocessing\n• Feature Engineering (Milestone drift, BOQ variance)\n• Overrun Prediction (scikit-learn)\n• Rule Risk Scoring"
    p2.font.size = Pt(8)
    p2.font.color.rgb = DARK_TEXT

    # 4. Risk Fusion
    b_fuse = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(8.1), Inches(1.9), Inches(1.25), Inches(2.0)
    )
    b_fuse.fill.solid()
    b_fuse.fill.fore_color.rgb = LIGHT_BLUE
    b_fuse.line.color.rgb = BLUE_BORDER
    tf = b_fuse.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Risk Fusion\n\nIntegrated Risk Score (Low / Medium / High / Critical Weighted Ensemble)"
    p.font.size = Pt(8.5)
    p.alignment = PP_ALIGN.CENTER

    # 5. Risk & Impact Analysis
    b_imp = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(9.55), Inches(1.9), Inches(1.4), Inches(2.0)
    )
    b_imp.fill.solid()
    b_imp.fill.fore_color.rgb = LIGHT_BLUE
    b_imp.line.color.rgb = BLUE_BORDER
    tf = b_imp.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Risk & Impact Analysis\n\n• Slippage Heatmap (GIS)\n• Financial Impact on Corridors & Packages"
    p.font.size = Pt(8.5)
    p.alignment = PP_ALIGN.CENTER

    # 6. Early Warning & Alerts
    b_alrt = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(11.15), Inches(1.9), Inches(1.5), Inches(2.0)
    )
    b_alrt.fill.solid()
    b_alrt.fill.fore_color.rgb = LIGHT_BLUE
    b_alrt.line.color.rgb = BLUE_BORDER
    tf = b_alrt.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Early Warning & Alerts\n\n• Officer In-App Alerts\n• Audit Log Generation\n• Executive PDF Reports"
    p.font.size = Pt(8.5)
    p.alignment = PP_ALIGN.CENTER

    # Fork to Roles: Field Engineers vs Senior Authorities
    b_role1 = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.4), Inches(4.3), Inches(2.8), Inches(2.1)
    )
    b_role1.fill.solid()
    b_role1.fill.fore_color.rgb = LIGHT_BLUE
    b_role1.line.color.rgb = BLUE_BORDER
    tf = b_role1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Field Engineers / Project Leads"
    p.font.size = Pt(10)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "\n• Submit milestone progress updates\n• Upload geo-tagged inspection photos\n• View assigned task schedules\n• Log delay reasons & site constraints"
    p2.font.size = Pt(8.5)

    b_role2 = slide3.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(9.5), Inches(4.3), Inches(3.1), Inches(2.1)
    )
    b_role2.fill.solid()
    b_role2.fill.fore_color.rgb = LIGHT_BLUE
    b_role2.line.color.rgb = BLUE_BORDER
    tf = b_role2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Senior Authorities / Administrators"
    p.font.size = Pt(10)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = "\n• Monitor nationwide project risk dashboard\n• Review predicted cost & time overruns\n• Verify evidence & approve milestones\n• Export executive audit & briefing reports"
    p2.font.size = Pt(8.5)

    # =========================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_standard_header(slide4, "FEASIBILITY AND VIABILITY")
    add_slide_number(slide4, "4")
    
    # Vertical divider line in center
    div_line = slide4.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(6.6), Inches(1.3), Inches(0.02), Inches(5.8)
    )
    div_line.fill.solid()
    div_line.fill.fore_color.rgb = RGBColor(148, 163, 184)
    div_line.line.fill.background()
    
    # Left Header: "Feasibility of the Idea"
    f_badge = slide4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(2.0), Inches(1.3), Inches(2.8), Inches(0.4)
    )
    f_badge.fill.solid()
    f_badge.fill.fore_color.rgb = WHITE
    f_badge.line.color.rgb = CARD_BORDER
    tf = f_badge.text_frame
    p = tf.paragraphs[0]
    p.text = "Feasibility of the Idea"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_TEXT
    p.alignment = PP_ALIGN.CENTER
    
    # Left Center Wheel Card
    c_wheel = slide4.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(2.7), Inches(3.2), Inches(1.6), Inches(1.6)
    )
    c_wheel.fill.solid()
    c_wheel.fill.fore_color.rgb = WHITE
    c_wheel.line.color.rgb = NAVY
    c_wheel.line.width = Pt(2)
    tf = c_wheel.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SetuX\nFeasible\nScalable\nImpactful"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    
    # 6 Radial Feasibility Points
    feas_pts = [
        ("Available Data Sources", "Standard DPRs, milestone schedules, financial allocations, and field progress logs.", Inches(0.4), Inches(2.0), RGBColor(16, 185, 129)),
        ("Technically Viable", "Proven React + FastAPI stack with scikit-learn predictive modeling & Leaflet GIS.", Inches(0.4), Inches(3.6), RGBColor(59, 130, 246)),
        ("Field Practical", "Lightweight web architecture with responsive UI & offline-tolerant data entry.", Inches(0.4), Inches(5.2), RGBColor(139, 92, 246)),
        ("Cost-Effective", "Built on modern open-source stack, eliminating expensive proprietary licensing.", Inches(4.4), Inches(2.0), RGBColor(245, 158, 11)),
        ("Scalable Solution", "Modular REST API architecture easily expanding from local works to national portfolios.", Inches(4.4), Inches(3.6), RGBColor(249, 115, 22)),
        ("Actionable Insights", "Intuitive risk scores, time/cost overrun forecasts, and spatial project maps.", Inches(4.4), Inches(5.2), RGBColor(239, 68, 68))
    ]
    
    for fname, fdesc, fx, fy, fcol in feas_pts:
        fcard = slide4.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            fx, fy, Inches(2.05), Inches(1.15)
        )
        fcard.fill.solid()
        fcard.fill.fore_color.rgb = CARD_BG
        fcard.line.color.rgb = fcol
        fcard.line.width = Pt(1.5)
        tf = fcard.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        
        p = tf.paragraphs[0]
        p.text = fname
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = fcol
        
        p2 = tf.add_paragraph()
        p2.text = fdesc
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = DARK_TEXT

    # Right Header: "Challenges Faced & Strategies to Overcome"
    c_badge = slide4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(7.4), Inches(1.3), Inches(4.8), Inches(0.4)
    )
    c_badge.fill.solid()
    c_badge.fill.fore_color.rgb = RGBColor(235, 245, 255)
    c_badge.line.color.rgb = BLUE_BORDER
    tf = c_badge.text_frame
    p = tf.paragraphs[0]
    p.text = "Challenges Faced & Strategies to Overcome"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    
    # 5 Challenge -> Strategy Rows
    challenges = [
        ("Fragmented Project Data in Silos", "Multi-source disparate spreadsheets delay decision visibility.", "Unified Ingestion & Dashboard", "Standardized REST API ingestion creates a single pane of glass monitoring system.", RGBColor(59, 130, 246)),
        ("Subjective Progress Reporting", "Field claims without evidence lead to unaccounted project delays.", "Evidence-Backed Verification", "Geo-tagged photos, BOQ logs & inspection checkpoints validate field progress.", RGBColor(16, 185, 129)),
        ("Unforeseen Cost & Time Overruns", "Delays discovered only after critical budget slippages occur.", "ML Risk Intelligence Engine", "scikit-learn predictive models forecast overrun probability & schedule drift.", RGBColor(245, 158, 11)),
        ("Complex Multi-Site Spread", "Difficult to track geographical progress across highway corridors.", "GIS Interactive Mapping", "Leaflet + OpenStreetMap maps all projects with visual risk heatmaps.", RGBColor(139, 92, 246)),
        ("Administrative Reporting Burden", "Manual compilation of executive summaries wastes officer time.", "Automated Executive Reports", "Instant PDF generation with structured KPI summaries & audit logs.", RGBColor(16, 185, 129))
    ]
    
    for c_idx, (c_title, c_desc, s_title, s_desc, r_col) in enumerate(challenges):
        cy = 1.85 + c_idx * 1.05
        
        # Challenge Card (Left)
        c_box = slide4.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(6.8), Inches(cy), Inches(2.6), Inches(0.95)
        )
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = CARD_BG
        c_box.line.color.rgb = CARD_BORDER
        tf = c_box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = c_title
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = DARK_TEXT
        p2 = tf.add_paragraph()
        p2.text = c_desc
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = MUTED_TEXT
        
        # Arrow
        arr = slide4.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW,
            Inches(9.5), Inches(cy + 0.35), Inches(0.25), Inches(0.22)
        )
        arr.fill.solid()
        arr.fill.fore_color.rgb = RGBColor(59, 130, 246)
        arr.line.fill.background()
        
        # Strategy Card (Right)
        s_box = slide4.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(9.85), Inches(cy), Inches(3.05), Inches(0.95)
        )
        s_box.fill.solid()
        s_box.fill.fore_color.rgb = RGBColor(240, 253, 244)
        s_box.line.color.rgb = RGBColor(34, 197, 94)
        tf = s_box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = s_title
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(22, 101, 52)
        p2 = tf.add_paragraph()
        p2.text = s_desc
        p2.font.size = Pt(7.5)
        p2.font.color.rgb = DARK_TEXT

    # =========================================================
    # SLIDE 5: BENEFIT AND IMPACT
    # =========================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_standard_header(slide5, "BENEFIT AND IMPACT")
    add_slide_number(slide5, "5")
    
    # Center Circular Comparison Badge: BENEFITS (Green) vs IMPACTS (Orange)
    c_ben = slide5.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(5.2), Inches(3.2), Inches(1.3), Inches(1.3)
    )
    c_ben.fill.solid()
    c_ben.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c_ben.line.color.rgb = GREEN
    c_ben.line.width = Pt(2)
    tf = c_ben.text_frame
    p = tf.paragraphs[0]
    p.text = "🌿\nBENEFITS"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = RGBColor(22, 101, 52)
    p.alignment = PP_ALIGN.CENTER
    
    c_vs = slide5.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(6.4), Inches(3.6), Inches(0.55), Inches(0.55)
    )
    c_vs.fill.solid()
    c_vs.fill.fore_color.rgb = RGBColor(254, 243, 199)
    c_vs.line.color.rgb = RGBColor(245, 158, 11)
    tf = c_vs.text_frame
    p = tf.paragraphs[0]
    p.text = "VS"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = RGBColor(180, 83, 9)
    p.alignment = PP_ALIGN.CENTER

    c_imp = slide5.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(6.85), Inches(3.2), Inches(1.3), Inches(1.3)
    )
    c_imp.fill.solid()
    c_imp.fill.fore_color.rgb = RGBColor(255, 247, 237)
    c_imp.line.color.rgb = ORANGE
    c_imp.line.width = Pt(2)
    tf = c_imp.text_frame
    p = tf.paragraphs[0]
    p.text = "📈\nIMPACTS"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = RGBColor(194, 65, 12)
    p.alignment = PP_ALIGN.CENTER
    
    # Left Column: 5 Benefits
    benefits = [
        ("01", "Unified Project Monitoring", "Centralized real-time visibility across physical, financial, and milestone metrics."),
        ("02", "Evidence-Supported Progress", "Geo-tagged photos, documents, and inspection logs validate claimed progress."),
        ("03", "Predictive Risk Intelligence", "Multi-factor risk engine detects schedule slippages and cost anomalies early."),
        ("04", "Geospatial Infrastructure Mapping", "Interactive GIS tracking enables regional and corridor-level oversight."),
        ("05", "Audit-Ready Reporting", "Automated executive briefings and complete audit trails streamline compliance.")
    ]
    
    for b_idx, (b_num, b_title, b_desc) in enumerate(benefits):
        by = 1.35 + b_idx * 1.08
        
        # Card
        b_card = slide5.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.6), Inches(by), Inches(3.8), Inches(0.95)
        )
        b_card.fill.solid()
        b_card.fill.fore_color.rgb = RGBColor(240, 253, 244)
        b_card.line.color.rgb = RGBColor(187, 247, 208)
        tf = b_card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = b_title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(22, 101, 52)
        p2 = tf.add_paragraph()
        p2.text = b_desc
        p2.font.size = Pt(8)
        p2.font.color.rgb = DARK_TEXT
        
        # Number Badge
        n_badge = slide5.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(4.55), Inches(by + 0.25), Inches(0.45), Inches(0.45)
        )
        n_badge.fill.solid()
        n_badge.fill.fore_color.rgb = RGBColor(187, 247, 208)
        n_badge.line.fill.background()
        tf = n_badge.text_frame
        p = tf.paragraphs[0]
        p.text = b_num
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(22, 101, 52)
        p.alignment = PP_ALIGN.CENTER

    # Right Column: 4 Impacts
    impacts = [
        ("01", "Timely Officer Intervention", "Proactive alerts enable administrative action before minor delays become critical overruns."),
        ("02", "Enhanced Accountability", "Verifiable progress submissions reduce discrepancy between reported and actual field status."),
        ("03", "Optimized Resource Allocation", "High-risk projects are highlighted for targeted intervention and budget management."),
        ("04", "Improved Governance Visibility", "Standardized monitoring framework ensures consistent oversight across departments.")
    ]
    
    for i_idx, (i_num, i_title, i_desc) in enumerate(impacts):
        iy = 1.6 + i_idx * 1.3
        
        # Number Badge
        n_badge = slide5.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(8.4), Inches(iy + 0.3), Inches(0.45), Inches(0.45)
        )
        n_badge.fill.solid()
        n_badge.fill.fore_color.rgb = RGBColor(254, 215, 170)
        n_badge.line.fill.background()
        tf = n_badge.text_frame
        p = tf.paragraphs[0]
        p.text = i_num
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(194, 65, 12)
        p.alignment = PP_ALIGN.CENTER
        
        # Card
        i_card = slide5.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(9.0), Inches(iy), Inches(3.9), Inches(1.1)
        )
        i_card.fill.solid()
        i_card.fill.fore_color.rgb = RGBColor(255, 247, 237)
        i_card.line.color.rgb = RGBColor(254, 215, 170)
        tf = i_card.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.04)
        tf.margin_left = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = i_title
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(194, 65, 12)
        p2 = tf.add_paragraph()
        p2.text = i_desc
        p2.font.size = Pt(8)
        p2.font.color.rgb = DARK_TEXT

    # =========================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_standard_header(slide6, "RESEARCH AND REFERENCES")
    add_slide_number(slide6, "6")
    
    # Left Column: Research & References
    ref_box = slide6.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(6.8), Inches(5.8))
    tf_ref = ref_box.text_frame
    tf_ref.word_wrap = True
    
    refs = [
        ("Ministry of Statistics and Programme Implementation (MoSPI)", 
         "Infrastructure and Project Monitoring Division (IPMD) — National project monitoring norms & flash reporting system.",
         "https://mospi.gov.in/infrastructure-and-project-monitoring-division-ipmd"),
         
        ("Government of India — PM GatiShakti National Master Plan", 
         "Multi-modal infrastructure connectivity, spatial planning and institutional project monitoring framework.",
         "https://gati-shakti.gov.in/"),
         
        ("Project Monitoring Group (PMG) / DPIIT", 
         "Institutional mechanism for fast-tracking resolution of issues and milestone monitoring in mega projects.",
         "https://pmg.dpiit.gov.in/"),
         
        ("scikit-learn: Machine Learning in Python — 2026", 
         "Pedregosa et al., JMLR. Applied for infrastructure cost overrun regression and schedule delay risk classification.",
         "https://scikit-learn.org/stable/"),
         
        ("FastAPI & High-Performance Asynchronous Python Framework", 
         "Production-ready REST API architecture with Pydantic schema validation for robust government data pipelines.",
         "https://fastapi.tiangolo.com/"),
         
        ("Leaflet & OpenStreetMap Open Geospatial Standards", 
         "Open-source interactive GIS visualization for project corridors, geo-tagged checkpoints and spatial heatmaps.",
         "https://leafletjs.com/")
    ]
    
    for r_idx, (r_title, r_desc, r_url) in enumerate(refs):
        p = tf_ref.paragraphs[0] if r_idx == 0 else tf_ref.add_paragraph()
        p.space_after = Pt(8)
        
        # Bullet & Title
        r_t = p.add_run()
        r_t.text = f"• {r_title}\n"
        r_t.font.bold = True
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = DARK_TEXT
        
        # Description
        r_d = p.add_run()
        r_d.text = f"  • {r_desc}\n"
        r_d.font.size = Pt(8.5)
        r_d.font.color.rgb = MUTED_TEXT
        
        # URL
        r_u = p.add_run()
        r_u.text = f"  {r_url}"
        r_u.font.size = Pt(8)
        r_u.font.color.rgb = RGBColor(37, 99, 235)
        r_u.font.underline = True

    # Right Column: UI Screenshots with "DASHBOARD" vertical ribbon
    # Screenshot 1 (Top)
    if os.path.exists(DASH1_PATH):
        slide6.shapes.add_picture(
            DASH1_PATH,
            Inches(7.4), Inches(1.2), width=Inches(5.0), height=Inches(2.7)
        )
    # Screenshot 2 (Bottom)
    if os.path.exists(DASH2_PATH):
        slide6.shapes.add_picture(
            DASH2_PATH,
            Inches(7.4), Inches(4.05), width=Inches(5.0), height=Inches(2.7)
        )
        
    # Vertical DASHBOARD Ribbon on Right Edge
    dash_ribbon = slide6.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(12.5), Inches(1.2), Inches(0.4), Inches(5.55)
    )
    dash_ribbon.fill.solid()
    dash_ribbon.fill.fore_color.rgb = NAVY
    dash_ribbon.line.fill.background()
    tf_ribbon = dash_ribbon.text_frame
    tf_ribbon.word_wrap = True
    p = tf_ribbon.paragraphs[0]
    p.text = "D\nA\nS\nH\nB\nO\nA\nR\nD"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    # Save presentation
    pptx_filename = "SetuX_SIH2026_Presentation.pptx"
    prs.save(pptx_filename)
    print(f"Presentation saved successfully as {pptx_filename}")

    # Export to PDF and Slide Images using PowerPoint COM
    try:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        ppt_path = os.path.abspath(pptx_filename)
        pdf_path = os.path.abspath("SetuX_SIH2026_Presentation.pdf")
        
        presentation = ppt_app.Presentations.Open(ppt_path, WithWindow=False)
        # 32 = ppSaveAsPDF
        presentation.SaveAs(pdf_path, 32)
        print(f"PDF exported successfully as {pdf_path}")
        
        # Export each slide to PNG for visual QA
        img_dir = os.path.abspath("slide_qa_images")
        os.makedirs(img_dir, exist_ok=True)
        for s_num in range(1, presentation.Slides.Count + 1):
            s_img_path = os.path.join(img_dir, f"slide_{s_num}.png")
            presentation.Slides(s_num).Export(s_img_path, "PNG", 1920, 1080)
            print(f"Exported slide {s_num} to {s_img_path}")
            
        presentation.Close()
        ppt_app.Quit()
        print("PowerPoint automation complete.")
    except Exception as e:
        print("Error during PDF / Image export:", e)

if __name__ == "__main__":
    build_presentation()
