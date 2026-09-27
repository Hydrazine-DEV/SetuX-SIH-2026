import os
import shutil
import re
import subprocess
import glob

SOURCE_DIR = r"c:\Users\cer\OneDrive\Desktop\SIH\setux"
TARGET_DIR = r"c:\Users\cer\OneDrive\Desktop\SIH\SetuX-GitHub"

print(f"Source: {SOURCE_DIR}")
print(f"Target: {TARGET_DIR}")

# Folders to exclude completely
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "env",
    "ENV",
    "__pycache__",
    "dist",
    "build",
    ".cache",
    ".vite",
    "coverage",
    ".pytest_cache",
    ".idea",
    ".vscode",
    ".kilo",
}

# Files to exclude completely
EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    ".env",          # We will create clean .env.example
    "setux.db",      # Runtime sqlite database (can be generated via seed script)
    "qa-temp.png",
    "tatus --short", # stray file
}

def should_exclude(dirpath, filename=None):
    parts = os.path.normpath(dirpath).split(os.sep)
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    if filename:
        if filename in EXCLUDE_FILES:
            return True
        if filename.endswith((".pyc", ".pyo", ".pyd", ".log", ".tmp", ".temp")):
            return True
    return False

# 1. Clean / Create TARGET_DIR
if os.path.exists(TARGET_DIR):
    print(f"Removing existing target folder: {TARGET_DIR}")
    shutil.rmtree(TARGET_DIR)

os.makedirs(TARGET_DIR, exist_ok=True)
print(f"Created clean directory: {TARGET_DIR}")

# 2. Copy source tree
copied_files = 0
excluded_files_list = []

for root, dirs, files in os.walk(SOURCE_DIR):
    # Filter out dirs in-place
    dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
    
    rel_root = os.path.relpath(root, SOURCE_DIR)
    if rel_root == ".":
        target_root = TARGET_DIR
    else:
        target_root = os.path.join(TARGET_DIR, rel_root)
        
    os.makedirs(target_root, exist_ok=True)
    
    for f in files:
        src_file = os.path.join(root, f)
        if should_exclude(root, f):
            excluded_files_list.append(os.path.relpath(src_file, SOURCE_DIR))
            continue
            
        dst_file = os.path.join(target_root, f)
        shutil.copy2(src_file, dst_file)
        copied_files += 1

print(f"Successfully copied {copied_files} files to {TARGET_DIR}")
print(f"Excluded {len(excluded_files_list)} files/directories.")

# 3. Create .env.example files with clean placeholders
backend_env_example = """# ==============================================================================
# SetuX Backend Configuration Example
# ==============================================================================
# Copy this file to .env before running the backend application.

# Application Security
SECRET_KEY=change-this-to-a-secure-random-32-byte-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration (SQLite for local demo, or PostgreSQL for production)
DATABASE_URL=sqlite:///./setux.db
# DATABASE_URL=postgresql://user:password@localhost:5432/setux_db

# Environment Mode
ENVIRONMENT=development
LOG_LEVEL=INFO
"""

frontend_env_example = """# ==============================================================================
# SetuX Frontend Configuration Example
# ==============================================================================
# Copy this file to .env before running the frontend application.

VITE_API_BASE_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000
"""

root_env_example = """# ==============================================================================
# SetuX Global Environment Configuration
# ==============================================================================
VITE_API_URL=http://localhost:8000
DATABASE_URL=sqlite:///setux.db
ENVIRONMENT=development
"""

with open(os.path.join(TARGET_DIR, "backend", ".env.example"), "w", encoding="utf-8") as f:
    f.write(backend_env_example)

with open(os.path.join(TARGET_DIR, "frontend", ".env.example"), "w", encoding="utf-8") as f:
    f.write(frontend_env_example)

with open(os.path.join(TARGET_DIR, ".env.example"), "w", encoding="utf-8") as f:
    f.write(root_env_example)

# 4. Create strong root .gitignore
gitignore_content = """# ==============================================================================
# SetuX Git Ignore Rules
# ==============================================================================

# Python & Virtual Environments
__pycache__/
*.py[cod]
*$py.class
*.pyo
*.pyd
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
htmlcov/
*.cover
*.log

# Node.js & Frontend Build
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
dist-ssr/
build/
.cache/
.vite/
.eslintcache

# Environment Variables & Secrets
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
!.env.example

# Local SQLite / Runtime Databases
*.sqlite3
*.db-journal
*.db-wal
*.db-shm
backend/setux.db
backend/setux_demo.db

# Generated Uploads & Temporary Reports
backend/uploads/reports/*.pdf
!backend/uploads/reports/.gitkeep

# IDEs & Operating System Artifacts
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Presentation generation scratch
slide_qa_images/
"""

with open(os.path.join(TARGET_DIR, ".gitignore"), "w", encoding="utf-8") as f:
    f.write(gitignore_content)

# 5. Organize screenshots into docs/screenshots/
docs_screenshots_dir = os.path.join(TARGET_DIR, "docs", "screenshots")
os.makedirs(docs_screenshots_dir, exist_ok=True)

# Copy presentation assets / dashboard screenshots if available
for img_name in ["setux_dashboard_1.png", "setux_dashboard_2.png", "sih_logo.png"]:
    src_img = os.path.join(SOURCE_DIR, "presentation_assets", img_name)
    if os.path.exists(src_img):
        shutil.copy2(src_img, os.path.join(docs_screenshots_dir, img_name))

# Copy citizen and officer portal images
for p_img in ["citizen-portal.jpg.png", "officer-portal.jpg.png"]:
    src_p = os.path.join(SOURCE_DIR, "frontend", p_img)
    if os.path.exists(src_p):
        shutil.copy2(src_p, os.path.join(docs_screenshots_dir, p_img))

print("Organized screenshots into docs/screenshots/")
