import os
import math
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------------------------------
# CONSTANTS & COLOR PALETTE MATCHING THE REFERENCE SLIDES
# -------------------------------------------------------------
# Dimensions: 16:9 widescreen (13.333 x 7.5 inches)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Primary Colors from Reference:
NAVY_TITLE = RGBColor(27, 54, 93)        # #1B365D - Deep Navy for main headings
TEXT_DARK = RGBColor(30, 41, 59)          # #1E293B - Charcoal Black for body/labels
TEXT_MUTED = RGBColor(71, 85, 105)        # #475569 - Secondary text
BG_WHITE = RGBColor(255, 255, 255)       # #FFFFFF - Background
BG_OFFWHITE = RGBColor(248, 250, 252)    # #F8FAFC
CARD_BG_BLUE = RGBColor(235, 241, 246)   # #EBF1F6 - Slide 2 left card
CARD_BORDER_BLUE = RGBColor(203, 213, 225) # #CBD5E1
PEACH_BG = RGBColor(254, 237, 222)       # #FEEDE6 - Slide 3 tech boxes
PEACH_BORDER = RGBColor(249, 115, 22)    # #F97316
LIGHT_BLUE_BOX = RGBColor(235, 245, 255) # #EBF5FF - Flowchart boxes
BOX_BORDER_BLUE = RGBColor(59, 130, 246) # #3B82F6

# Sequential Workflow Colors (Slide 2):
WF_COLORS = [
    (RGBColor(37, 99, 235), "1. Project Ingestion"),      # Blue
    (RGBColor(22, 163, 74), "2. Field Evidence"),        # Green
    (RGBColor(124, 58, 237), "3. AI / ML Prediction"),   # Purple
    (RGBColor(220, 38, 38), "4. Risk Fusion"),           # Red
    (RGBColor(217, 119, 6), "5. Delay & Cost Impact"),    # Amber
    (RGBColor(13, 148, 136), "6. Early Alerts"),         # Teal
    (RGBColor(2, 132, 199), "7. Officer Action"),        # Cyan
    (RGBColor(109, 40, 217), "8. Stakeholders & Audit")  # Violet
]

# Feasibility Colors (Slide 4):
FEAS_COLORS = [
    RGBColor(16, 185, 129),  # Green
    RGBColor(59, 130, 246),  # Blue
    RGBColor(139, 92, 246),  # Purple
    RGBColor(245, 158, 11),  # Amber
    RGBColor(249, 115, 22),  # Orange
    RGBColor(239, 68, 68)    # Red
]

# Impact Colors (Slide 5):
GREEN_BENEFIT = RGBColor(34, 197, 94)
ORANGE_IMPACT = RGBColor(249, 115, 22)

os.makedirs('presentation_assets', exist_ok=True)

# -------------------------------------------------------------
# ASSET GENERATION: SIH LOGO, ICONS, DIAGRAMS & SCREENSHOTS
# -------------------------------------------------------------
def create_sih_logo():
    path = "presentation_assets/sih_logo.png"
    img = Image.new("RGBA", (800, 280), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Brain / Lightbulb graphic on the left
    # Left hemisphere (Orange circuit), Right hemisphere (Green binary)
    cx, cy = 120, 110
    
    # Left orange lobe
    draw.pieslice([cx-70, cy-70, cx+70, cy+70], 90, 270, fill=(245, 130, 32, 255))
    # Right green lobe
    draw.pieslice([cx-70, cy-70, cx+70, cy+70], 270, 90, fill=(16, 150, 72, 255))
    
    # Inner circuitry lines (white/orange)
    draw.line([cx-40, cy-30, cx-20, cy-30, cx-20, cy], fill=(255, 255, 255), width=3)
    draw.line([cx-50, cy+10, cx-30, cy+10, cx-10, cy+30], fill=(255, 255, 255), width=3)
    
    # Binary text simulated on right
    # Base connector
    draw.rectangle([cx-25, cy+75, cx+25, cy+95], fill=(30, 41, 59, 255))
    draw.arc([cx-20, cy+90, cx+20, cy+110], 0, 180, fill=(30, 41, 59, 255), width=4)
    
    # "SIH" label below bulb
    # We will use simple clean text for SIH
    # Text on right: SMART INDIA HACKATHON 2026
    # Right Text:
    # Line 1: SMART INDIA
    # Line 2: HACKATHON
    # Line 3: 2026
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 36)
        font_sih = ImageFont.truetype("arialbd.ttf", 26)
    except:
        font_large = font_sih = ImageFont.load_default()
        
    draw.text((cx-22, cy+118), "SIH", fill=(30, 41, 59, 255), font=font_sih)
    
    tx = 240
    draw.text((tx, 45), "SMART INDIA", fill=(27, 54, 93, 255), font=font_large)
    draw.text((tx, 90), "HACKATHON", fill=(27, 54, 93, 255), font=font_large)
    draw.text((tx, 140), "2026", fill=(27, 54, 93, 255), font=font_large)
    
    img.save(path, "PNG")
    return path

def create_slide1_emblem():
    path = "presentation_assets/slide1_emblem.png"
    img = Image.new("RGBA", (800, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 400, 380
    
    # Background soft gray hexagon
    hex_pts = []
    r = 280
    for i in range(6):
        angle = math.radians(60 * i - 30)
        hex_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(hex_pts, fill=(241, 245, 249, 255))
    
    # Tick marks radiating
    for i in range(8):
        angle = math.radians(45 * i + 22.5)
        x1 = cx + 220 * math.cos(angle)
        y1 = cy + 220 * math.sin(angle)
        x2 = cx + 260 * math.cos(angle)
        y2 = cy + 260 * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill=(71, 85, 105, 255), width=10)
        
    # Central Brain / AI Lightbulb
    # Left hemisphere: Orange
    draw.pieslice([cx-150, cy-170, cx+150, cy+130], 90, 270, fill=(245, 130, 32, 255))
    # Right hemisphere: Green
    draw.pieslice([cx-150, cy-170, cx+150, cy+130], 270, 90, fill=(16, 150, 72, 255))
    
    # Circuit details on orange
    draw.line([cx-90, cy-80, cx-40, cy-80, cx-40, cy-10], fill=(255, 255, 255), width=6)
    draw.ellipse([cx-46, cy-16, cx-34, cy-4], fill=(255, 255, 255))
    draw.line([cx-110, cy, cx-70, cy, cx-30, cy+40], fill=(255, 255, 255), width=6)
    draw.ellipse([cx-36, cy+34, cx-24, cy+46], fill=(255, 255, 255))
    
    # Binary text on green
    try:
        font_bin = ImageFont.truetype("consolab.ttf", 32)
        font_sih = ImageFont.truetype("arialbd.ttf", 46)
    except:
        font_bin = font_sih = ImageFont.load_default()
        
    draw.text((cx+30, cy-120), "1010", fill=(255, 255, 255), font=font_bin)
    draw.text((cx+30, cy-70), "01010", fill=(255, 255, 255), font=font_bin)
    draw.text((cx+30, cy-20), "101010", fill=(255, 255, 255), font=font_bin)
    draw.text((cx+30, cy+30), "010101", fill=(255, 255, 255), font=font_bin)
    draw.text((cx+30, cy+80), "10101", fill=(255, 255, 255), font=font_bin)
    
    # Base connector and SIH badge
    draw.rectangle([cx-60, cy+145, cx+60, cy+180], fill=(30, 41, 59, 255))
    draw.arc([cx-50, cy+170, cx+50, cy+215], 0, 180, fill=(30, 41, 59, 255), width=8)
    draw.text((cx-42, cy+225), "SIH", fill=(30, 41, 59, 255), font=font_sih)
    
    img.save(path, "PNG")
    return path

def create_ui_screenshots():
    # Let's create two ultra-clean SetuX Dashboard UI mock screenshots matching the theme
    p1 = "presentation_assets/setux_dashboard_1.png"
    p2 = "presentation_assets/setux_dashboard_2.png"
    
    # Dashboard 1: Command Center
    img1 = Image.new("RGB", (1200, 680), (15, 23, 42)) # Dark slate theme
    d1 = ImageDraw.Draw(img1)
    
    # Top navbar
    d1.rectangle([0, 0, 1200, 60], fill=(30, 41, 59))
    try:
        f_title = ImageFont.truetype("arialbd.ttf", 22)
        f_sub = ImageFont.truetype("arial.ttf", 16)
        f_bold = ImageFont.truetype("arialbd.ttf", 18)
        f_stat = ImageFont.truetype("arialbd.ttf", 32)
    except:
        f_title = f_sub = f_bold = f_stat = ImageFont.load_default()
        
    d1.text((25, 18), "SetuX — Infrastructure Project Monitoring Platform", fill=(241, 245, 249), font=f_title)
    d1.text((950, 20), "National Highway / Urban Infra Portal", fill=(148, 163, 184), font=f_sub)
    
    # 4 Stat KPI Cards
    kpis = [
        ("Monitored Projects", "48", (59, 130, 246)),
        ("Critical Risk Alerts", "4", (239, 68, 68)),
        ("Delayed Milestones", "9", (245, 158, 11)),
        ("Total Capital Monitored", "₹14,250 Cr", (16, 185, 129))
    ]
    for i, (label, val, col) in enumerate(kpis):
        x = 25 + i * 290
        d1.rectangle([x, 80, x+275, 180], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        d1.rectangle([x, 80, x+275, 86], fill=col)
        d1.text((x+20, 100), label, fill=(148, 163, 184), font=f_sub)
        d1.text((x+20, 130), val, fill=(255, 255, 255), font=f_stat)
        
    # Main Content Area: Left Map / Right Project List
    # Map area
    d1.rectangle([25, 200, 680, 650], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    d1.text((45, 220), "GIS Project Geography & Corridor Risk Heatmap", fill=(241, 245, 249), font=f_bold)
    # Draw simulated map corridors
    d1.line([80, 400, 250, 320, 420, 450, 600, 300], fill=(59, 130, 246), width=6)
    d1.line([150, 550, 300, 480, 500, 520], fill=(239, 68, 68), width=6)
    # Pins
    d1.ellipse([240, 310, 260, 330], fill=(34, 197, 94))
    d1.ellipse([410, 440, 430, 460], fill=(245, 158, 11))
    d1.ellipse([290, 470, 310, 490], fill=(239, 68, 68))
    
    # Right Project Status Table
    d1.rectangle([725, 200, 1175, 650], fill=(30, 41, 59), outline=(51, 65, 85), width=2)
    d1.text((745, 220), "Active Projects & Risk Index", fill=(241, 245, 249), font=f_bold)
    
    rows = [
        ("NH-44 Expressway Ext.", "Physical: 68%", "Cost Risk: Low", (34, 197, 94)),
        ("Brahmaputra Bridge P3", "Physical: 42%", "Cost Risk: Critical", (239, 68, 68)),
        ("Metro Corridor Phase 2", "Physical: 81%", "Cost Risk: Medium", (245, 158, 11)),
        ("Coastal Freight Corridor", "Physical: 29%", "Cost Risk: Low", (34, 197, 94)),
        ("Ring Road Flyover Jn.", "Physical: 55%", "Cost Risk: Critical", (239, 68, 68))
    ]
    for j, (pname, prog, risk, rcol) in enumerate(rows):
        y = 270 + j * 72
        d1.rectangle([745, y, 1155, y+60], fill=(15, 23, 42), outline=(51, 65, 85))
        d1.text((760, y+10), pname, fill=(255, 255, 255), font=f_bold)
        d1.text((760, y+34), prog, fill=(148, 163, 184), font=f_sub)
        d1.rectangle([1010, y+14, 1140, y+44], fill=rcol)
        d1.text((1020, y+20), risk, fill=(255, 255, 255), font=f_sub)
        
    img1.save(p1, "PNG")
    
    # Dashboard 2: Risk Intelligence & Predictive Analytics
    img2 = Image.new("RGB", (1200, 680), (15, 23, 42))
    d2 = ImageDraw.Draw(img2)
    
    # Header
    d2.rectangle([0, 0, 1200, 60], fill=(30, 41, 59))
    d2.text((25, 18), "SetuX — Risk Intelligence & Overrun Prediction Engine", fill=(241, 245, 249), font=f_title)
    
    # 3 Summary Cards
    d2.rectangle([25, 80, 390, 180], fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((45, 95), "Predicted Cost Overrun", fill=(148, 163, 184), font=f_sub)
    d2.text((45, 125), "+14.8% Est.", fill=(239, 68, 68), font=f_stat)
    
    d2.rectangle([415, 80, 785, 180], fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((435, 95), "Predicted Schedule Delay", fill=(148, 163, 184), font=f_sub)
    d2.text((435, 125), "+4.2 Months", fill=(245, 158, 11), font=f_stat)
    
    d2.rectangle([810, 80, 1175, 180], fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((830, 95), "Audit Trail Integrity", fill=(148, 163, 184), font=f_sub)
    d2.text((830, 125), "100% Verified", fill=(34, 197, 94), font=f_stat)
    
    # Charts area
    d2.rectangle([25, 200, 585, 650], fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((45, 220), "Multi-Factor Risk Breakdown (SHAP / ML Indicators)", fill=(241, 245, 249), font=f_bold)
    
    factors = [
        ("Milestone Variance", 0.85, (239, 68, 68)),
        ("Contractor Past Performance", 0.65, (245, 158, 11)),
        ("Material Inflation & BOQ Drift", 0.72, (239, 68, 68)),
        ("Site Weather / Environmental Delays", 0.40, (59, 130, 246)),
        ("Disbursement & Fund Flow Lag", 0.55, (245, 158, 11))
    ]
    for k, (fname, fval, fcol) in enumerate(factors):
        y = 270 + k * 70
        d2.text((45, y), fname, fill=(241, 245, 249), font=f_sub)
        d2.rectangle([45, y+26, 545, y+44], fill=(15, 23, 42))
        d2.rectangle([45, y+26, 45 + int(500 * fval), y+44], fill=fcol)
        
    d2.rectangle([615, 200, 1175, 650], fill=(30, 41, 59), outline=(51, 65, 85))
    d2.text((635, 220), "Project Evidence & Verification Logs", fill=(241, 245, 249), font=f_bold)
    
    ev_logs = [
        ("Pier Foundation Concrete Pour", "Geo: 26.14°N, 91.73°E", "Verified", (34, 197, 94)),
        ("Girder Segment Launching #14", "Geo: 26.15°N, 91.75°E", "Under Review", (245, 158, 11)),
        ("Sub-Base Compaction Layer 3", "Geo: 26.18°N, 91.80°E", "Verified", (34, 197, 94)),
        ("Deck Slab Reinforcement Inspection", "Geo: 26.19°N, 91.82°E", "Flagged Anomaly", (239, 68, 68)),
        ("Drainage & Retaining Wall", "Geo: 26.21°N, 91.85°E", "Verified", (34, 197, 94))
    ]
    for m, (etitle, ecoord, estat, ecol) in enumerate(ev_logs):
        y = 270 + m * 70
        d2.rectangle([635, y, 1155, y+58], fill=(15, 23, 42), outline=(51, 65, 85))
        d2.text((650, y+10), etitle, fill=(255, 255, 255), font=f_bold)
        d2.text((650, y+34), ecoord, fill=(148, 163, 184), font=f_sub)
        d2.rectangle([1010, y+14, 1140, y+44], fill=ecol)
        d2.text((1020, y+20), estat, fill=(255, 255, 255), font=f_sub)
        
    img2.save(p2, "PNG")
    return p1, p2

create_sih_logo()
create_slide1_emblem()
create_ui_screenshots()
print("All graphic assets created successfully.")
