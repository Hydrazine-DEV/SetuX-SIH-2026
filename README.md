# SetuX — AI-Powered Government Infrastructure Verification System

> **Tagline**: From Reported Progress to Verified Progress.
>
> **Alternative**: See What’s Really Built.
>
> **Scope**: Maharashtra-first (Pune Region Primary Demo) e-Governance prototype designed to help government officers verify physical construction progress against reported milestones using computer vision metadata, proximity geofencing, and historical verification comparison.

---

## 1. Project Concept & Architecture

The system uses site photo/video evidence submitted by field officers, verifies the GPS EXIF proximity coordinates against registered database geometries, runs mock AI computer vision checks (surface, edges, concrete layer detections), and generates an anomaly risk rating (0-100) recommending either **Approved** or **Manual Inspection Required**.

### Directory Structure
```
setux/
├── frontend/           React 18 + Vite + Tailwind CSS + Leaflet Maps
├── backend/            FastAPI (Python) + SQLite database + SQLAlchemy ORM
├── ai/                 Inference & processing pipeline skeleton
└── data/               Simulated seed project databases
```

---

## 2. Setup & Installation

**For a new computer, follow [HOW_TO_RUN.md](HOW_TO_RUN.md).** Windows users can double-click `setup-first-time.bat`, then `start-backend.bat` and `start-frontend.bat`.

### Prerequisite check
Ensure **Python 3.10+** and **Node.js 18+** (LTS) are installed.

### Step 1: Initialize Database & Seed
From the `setux` folder:
```bash
python -m venv backend/venv
backend/venv/Scripts/python -m pip install -r backend/requirements.txt
backend/venv/Scripts/python scripts/seed_database.py
```
(On macOS/Linux use `backend/venv/bin/python`.)

### Step 2: Start Backend API Server
```bash
cd backend
venv/Scripts/python -m uvicorn app.main:app --port 8000
```
API Documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 3: Launch React Frontend App
```bash
cd frontend
npm install
npm run dev
```
The application will launch at: [http://localhost:5173](http://localhost:5173)

Demo login: `admin_pune` / `password`

---

## 3. Demo Flow Presentation Walkthrough

1. **Login Page**: Access the secure e-governance sign-in screen at `http://localhost:5173/`. Click "Secure Sign In" to enter using the pre-filled demo officer credentials.
2. **Dashboard Overview**: Analyze Maharashtra state-wide KPI summaries (Verified, Review Required, High Risk). Check the interactive Leaflet Map for Pune Region markers showing color-coded risk flags.
3. **Inspect Project**: Click on project `MH-PN-001` (Hadapsar Road Development) inside the dashboard list. View the details showing reported completion at 100% vs AI-estimated visible completion at 71%.
4. **Submit Site Evidence**: Click "Report Progress" on the sidebar or "Verify" on the list to launch the 5-step verification submission wizard. Select `MH-PN-001` and run through progress declaration, file attachments, and GPS audit. Try changing GPS proximity checks from "Near site" to "Extreme Gap" to test geofence alert triggering.
5. **AI Pipeline Run**: Click the "Verify & Initiate AI Pipeline" button. Watch the AI Verification pipeline screen animate each stage. Examine the Computer Vision checklists, before/after side-by-side snapshots, and the resulting Anomaly score gauge (78/100) recommending Manual Inspection.
6. **Analytics Insights**: Click "Analytics" in the sidebar. Review state-wide completion trend charts, district comparisons, and the priority lists sorted to show officers which projects should be inspected first.
