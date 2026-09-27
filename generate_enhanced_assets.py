import os
import math
from PIL import Image, ImageDraw, ImageFont

os.makedirs('presentation_assets', exist_ok=True)

# -------------------------------------------------------------
# 1. SHARP SIH 2026 LOGO
# -------------------------------------------------------------
def create_sih_logo():
    path = "presentation_assets/sih_logo.png"
    img = Image.new("RGBA", (900, 320), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 130, 120
    
    # Left orange lobe
    draw.pieslice([cx-75, cy-75, cx+75, cy+75], 90, 270, fill=(245, 130, 32, 255))
    # Right green lobe
    draw.pieslice([cx-75, cy-75, cx+75, cy+75], 270, 90, fill=(16, 150, 72, 255))
    
    # Circuit tracks on orange lobe
    draw.line([cx-45, cy-35, cx-25, cy-35, cx-25, cy-5], fill=(255, 255, 255, 255), width=4)
    draw.ellipse([cx-29, cy-9, cx-21, cy-1], fill=(255, 255, 255, 255))
    draw.line([cx-55, cy+15, cx-35, cy+15, cx-15, cy+40], fill=(255, 255, 255, 255), width=4)
    draw.ellipse([cx-19, cy+36, cx-11, cy+44], fill=(255, 255, 255, 255))
    
    # Binary text on green lobe
    try:
        f_bin = ImageFont.truetype("consolab.ttf", 16)
        f_sih = ImageFont.truetype("arialbd.ttf", 28)
        f_title = ImageFont.truetype("arialbd.ttf", 36)
    except:
        f_bin = f_sih = f_title = ImageFont.load_default()
        
    draw.text((cx+12, cy-60), "1010", fill=(255, 255, 255, 255), font=f_bin)
    draw.text((cx+12, cy-35), "01010", fill=(255, 255, 255, 255), font=f_bin)
    draw.text((cx+12, cy-10), "101010", fill=(255, 255, 255, 255), font=f_bin)
    draw.text((cx+12, cy+15), "010101", fill=(255, 255, 255, 255), font=f_bin)
    draw.text((cx+12, cy+40), "10101", fill=(255, 255, 255, 255), font=f_bin)
    
    # Base connector
    draw.rectangle([cx-28, cy+80, cx+28, cy+100], fill=(30, 41, 59, 255))
    draw.arc([cx-22, cy+95, cx+22, cy+118], 0, 180, fill=(30, 41, 59, 255), width=5)
    draw.text((cx-24, cy+125), "SIH", fill=(30, 41, 59, 255), font=f_sih)
    
    # Right Text
    tx = 260
    draw.text((tx, 45), "SMART INDIA", fill=(27, 54, 93, 255), font=f_title)
    draw.text((tx, 95), "HACKATHON", fill=(27, 54, 93, 255), font=f_title)
    draw.text((tx, 150), "2026", fill=(27, 54, 93, 255), font=f_title)
    
    img.save(path, "PNG")
    return path

# -------------------------------------------------------------
# 2. SLIDE 1 CENTER/RIGHT EMBLEM
# -------------------------------------------------------------
def create_slide1_emblem():
    path = "presentation_assets/slide1_emblem.png"
    img = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 500, 480
    
    # Background soft gray hexagon
    hex_pts = []
    r = 380
    for i in range(6):
        angle = math.radians(60 * i - 30)
        hex_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(hex_pts, fill=(241, 245, 249, 255))
    
    # Radiating dark tick marks
    for i in range(8):
        angle = math.radians(45 * i + 22.5)
        x1 = cx + 290 * math.cos(angle)
        y1 = cy + 290 * math.sin(angle)
        x2 = cx + 345 * math.cos(angle)
        y2 = cy + 345 * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill=(51, 65, 85, 255), width=14)
        
    # Central Brain / AI Lightbulb
    draw.pieslice([cx-200, cy-220, cx+200, cy+180], 90, 270, fill=(245, 130, 32, 255))
    draw.pieslice([cx-200, cy-220, cx+200, cy+180], 270, 90, fill=(16, 150, 72, 255))
    
    # Circuit details on orange
    draw.line([cx-120, cy-100, cx-50, cy-100, cx-50, cy-15], fill=(255, 255, 255, 255), width=8)
    draw.ellipse([cx-58, cy-23, cx-42, cy-7], fill=(255, 255, 255, 255))
    draw.line([cx-140, cy+10, cx-90, cy+10, cx-40, cy+60], fill=(255, 255, 255, 255), width=8)
    draw.ellipse([cx-48, cy+52, cx-32, cy+68], fill=(255, 255, 255, 255))
    
    # Binary text on green
    try:
        font_bin = ImageFont.truetype("consolab.ttf", 44)
        font_sih = ImageFont.truetype("arialbd.ttf", 62)
    except:
        font_bin = font_sih = ImageFont.load_default()
        
    draw.text((cx+35, cy-160), "1010", fill=(255, 255, 255, 255), font=font_bin)
    draw.text((cx+35, cy-95), "01010", fill=(255, 255, 255, 255), font=font_bin)
    draw.text((cx+35, cy-30), "101010", fill=(255, 255, 255, 255), font=font_bin)
    draw.text((cx+35, cy+35), "010101", fill=(255, 255, 255, 255), font=font_bin)
    draw.text((cx+35, cy+100), "10101", fill=(255, 255, 255, 255), font=font_bin)
    
    # Base connector and SIH badge
    draw.rectangle([cx-80, cy+200, cx+80, cy+245], fill=(30, 41, 59, 255))
    draw.arc([cx-65, cy+230, cx+65, cy+290], 0, 180, fill=(30, 41, 59, 255), width=10)
    draw.text((cx-55, cy+305), "SIH", fill=(30, 41, 59, 255), font=font_sih)
    
    img.save(path, "PNG")
    return path

# -------------------------------------------------------------
# 3. SLIDE 4 FEASIBILITY WHEEL
# -------------------------------------------------------------
def create_feasibility_wheel():
    path = "presentation_assets/feasibility_wheel.png"
    img = Image.new("RGBA", (800, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 400, 400
    outer_r = 340
    inner_r = 160
    
    # 6 Colored Segments
    colors = [
        (16, 185, 129),  # Green
        (59, 130, 246),  # Blue
        (139, 92, 246),  # Purple
        (239, 68, 68),   # Red
        (249, 115, 22),  # Orange
        (245, 158, 11)   # Yellow
    ]
    
    # Draw 6 pie sectors
    for i, col in enumerate(colors):
        start_a = i * 60 - 90
        end_a = (i + 1) * 60 - 90
        draw.pieslice([cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r], start_a, end_a, fill=(*col, 255), outline=(255, 255, 255, 255), width=4)
        
    # Draw white inner circle to make it a donut
    draw.ellipse([cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r], fill=(255, 255, 255, 255), outline=(27, 54, 93, 255), width=6)
    
    # Center Text
    try:
        f_main = ImageFont.truetype("arialbd.ttf", 36)
        f_sub = ImageFont.truetype("arial.ttf", 26)
    except:
        f_main = f_sub = ImageFont.load_default()
        
    draw.text((cx-55, cy-65), "SetuX", fill=(27, 54, 93, 255), font=f_main)
    draw.text((cx-55, cy-15), "Feasible", fill=(71, 85, 105, 255), font=f_sub)
    draw.text((cx-55, cy+18), "Scalable", fill=(71, 85, 105, 255), font=f_sub)
    draw.text((cx-60, cy+51), "Impactful", fill=(71, 85, 105, 255), font=f_sub)
    
    # Icons inside sectors (rendered as clean symbols)
    icons = ["🗄️", "📊", "📱", "🎯", "⚡", "💰"]
    try:
        f_ico = ImageFont.truetype("seguiemj.ttf", 44)
    except:
        f_ico = ImageFont.load_default()
        
    for i, ico in enumerate(icons):
        mid_a = math.radians(i * 60 - 60)
        ic_r = (outer_r + inner_r) / 2
        ix = cx + ic_r * math.cos(mid_a) - 22
        iy = cy + ic_r * math.sin(mid_a) - 22
        try:
            draw.text((ix, iy), ico, font=f_ico)
        except:
            draw.ellipse([ix, iy, ix+40, iy+40], fill=(255, 255, 255, 200))
            
    img.save(path, "PNG")
    return path

# -------------------------------------------------------------
# 4. SLIDE 5 CENTER VS BADGE
# -------------------------------------------------------------
def create_vs_badge():
    path = "presentation_assets/vs_badge.png"
    img = Image.new("RGBA", (900, 500), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    cy = 250
    # Left green circle (Benefits)
    cx1 = 280
    r1 = 170
    draw.ellipse([cx1-r1, cy-r1, cx1+r1, cy+r1], fill=(240, 253, 244, 255), outline=(34, 197, 94, 255), width=8)
    
    # Right orange circle (Impacts)
    cx2 = 620
    r2 = 170
    draw.ellipse([cx2-r2, cy-r2, cx2+r2, cy+r2], fill=(255, 247, 237, 255), outline=(249, 115, 22, 255), width=8)
    
    # Center gold VS circle
    cx_vs = 450
    r_vs = 70
    draw.ellipse([cx_vs-r_vs, cy-r_vs, cx_vs+r_vs, cy+r_vs], fill=(254, 243, 199, 255), outline=(245, 158, 11, 255), width=6)
    
    try:
        f_b = ImageFont.truetype("arialbd.ttf", 36)
        f_vs = ImageFont.truetype("arialbd.ttf", 38)
    except:
        f_b = f_vs = ImageFont.load_default()
        
    draw.text((cx1-95, cy-20), "BENEFITS", fill=(22, 101, 52, 255), font=f_b)
    draw.text((cx2-85, cy-20), "IMPACTS", fill=(194, 65, 12, 255), font=f_b)
    draw.text((cx_vs-28, cy-22), "VS", fill=(180, 83, 9, 255), font=f_vs)
    
    img.save(path, "PNG")
    return path

create_sih_logo()
create_slide1_emblem()
create_feasibility_wheel()
create_vs_badge()
print("All enhanced graphic assets generated.")
