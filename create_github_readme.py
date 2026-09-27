import os

TARGET_DIR = r"c:\Users\cer\OneDrive\Desktop\SIH\SetuX-GitHub"

readme_content = """# SetuX

### *From Reported Progress to Verified Progress*

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://www.sih.gov.in/)
[![Problem Statement](https://img.shields.io/badge/PS_ID-SIH26103-blue.svg)](https://www.sih.gov.in/)
[![Category](https://img.shields.io/badge/Category-Software-green.svg)](https://www.sih.gov.in/)
[![Team](https://img.shields.io/badge/Team-Team_VeriX-purple.svg)](https://github.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)

---

## 📌 Overview

**SetuX** is an integrated government infrastructure project monitoring and intelligence platform designed to help monitoring officers, project directors, and administrators track project execution, identify emerging implementation risks early, verify field progress with geo-tagged evidence, manage milestones, trigger proactive warnings, and generate audit-ready executive reports.

Developed as an MVP solution for **Smart India Hackathon 2026**, SetuX bridges the gap between claimed progress reports and verified on-ground reality.

- **Problem Statement ID:** `SIH26103`
- **Problem Statement Title:** Integrated Government Project Monitoring & Intelligence Platform
- **Category:** Software
- **Team Name:** Team VeriX
- **Hackathon:** Smart India Hackathon 2026

---

## 🎯 Problem Statement

Public infrastructure projects (highways, bridges, corridors, municipal facilities) typically face monitoring challenges due to fragmented data sources:
- **Information Silos:** Financial disbursements, physical milestones, contractor logs, and site photos reside across disconnected spreadsheets and departmental systems.
- **Subjective Progress Reporting:** Progress is frequently reported as static completion percentages without verifiable field evidence or audit logs.
- **Delayed Risk Detection:** Cost overruns and schedule slippages are often recognized only after critical delay thresholds have already been crossed.
- **Geographic Spread:** Monitoring multi-site, multi-district project packages without spatial intelligence limits regional oversight.
- **Administrative Reporting Overhead:** Compiling executive briefing summaries and compliance audits manually requires significant administrative effort.

**SetuX** addresses these challenges by bringing project ingestion, milestone verification, risk intelligence, GIS mapping, and automated reporting into a unified monitoring ecosystem.

---

## 💡 Our Solution

```
┌────────────────────────┐
│   Reported Progress    │ (Plans, DPR, BOQ, Milestones, Contractor Updates)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│   Project Monitoring   │ (Centralized Physical, Financial & Milestone Tracking)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ Evidence & Verification│ (Geo-tagged Photos, BOQ Checkpoints, Inspection Logs)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│   Risk Intelligence    │ (Multi-Factor Scoring, Milestone Drift, Contractor Risk)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│  Predictive Analytics  │ (scikit-learn Cost Overrun Regressor & Delay Estimator)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│     Early Warnings     │ (Threshold Alerts, Escalations & Trigger Notifications)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│     Officer Action     │ (Command Center Review, Milestone Sign-off, Mitigation)
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│  Executive Reporting   │ (Automated Audit Logs & Structured Executive PDF Reports)
└────────────────────────┘
```

---

## ✨ Key Features

- **🔐 Officer Authentication & RBAC:** Secure JWT-based authentication with role-specific dashboards for Project Officers, Department Heads, and Administrators.
- **📊 Unified Command Center:** Real-time visibility into project health, physical completion, financial utilization, and critical alerts.
- **📍 Interactive GIS Project Map:** Built with Leaflet and OpenStreetMap, providing geospatial visualization of project corridors, package locations, and risk heatmaps.
- **📋 Milestone & Timeline Tracking:** Granular breakdown of project phases, baseline vs. revised target dates, and delay detection.
- **📷 Evidence-Backed Verification:** Support for uploading and inspecting geo-tagged inspection photos, BOQ logs, and site verification records.
- **🧠 Risk Intelligence & Predictive Analytics:**
  - Machine learning models for cost overrun percentage estimation and schedule delay prediction.
  - Multi-factor risk engine analyzing contractor history, material inflation, milestone variance, and weather/site factors.
- **⚡ Proactive Early Warning System:** Real-time alert triggers for budget slippage, milestone bottlenecks, and prolonged inactivity.
- **📑 Automated Executive PDF Reports:** One-click generation of comprehensive, audit-ready project status and early-warning reports.
- **🌐 Citizen Transparency Portal:** Public-facing view for citizens to review infrastructure development, project stages, and nearby public works.
- **🌓 Modern Responsive Interface:** Clean, accessible user interface built with Tailwind CSS, featuring full light/dark theme support.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                             │
│  React 18 + Vite | Tailwind CSS | Recharts | Leaflet Maps | Lucide UI  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST API (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                             │
│                  FastAPI Asynchronous Backend (Python)                 │
│  ┌───────────────────────┬──────────────────────┬────────────────────┐ │
│  │  Authentication & RBAC│  Project Management  │ Milestone Tracking │ │
│  ├───────────────────────┼──────────────────────┼────────────────────┤ │
│  │  Evidence Inspection  │  GIS GeoJSON Service │ Issue Management   │ │
│  ├───────────────────────┼──────────────────────┼────────────────────┤ │
│  │  Alerts & Escalations │  PDF Report Engine   │ Audit Trail Engine │ │
│  └───────────────────────┴──────────────────────┴────────────────────┘ │
└───────────────────┬─────────────────────────────────┬──────────────────┘
                    │                                 │
                    ▼                                 ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────┐
│            DATA LAYER                 │ │      INTELLIGENCE LAYER      │
│  SQLAlchemy ORM                       │ │  scikit-learn ML Models      │
│  SQLite (Local MVP) / PostgreSQL Ready│ │  • Cost Overrun Regressor    │
│  Structured Audit Logs & File Uploads │ │  • Schedule Delay Predictor  │
│                                       │ │  • Multi-Factor Risk Fusion  │
└───────────────────────────────────────┘ └──────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18 (SPA) with Vite
- **Styling:** Tailwind CSS, Vanilla CSS
- **Routing:** React Router v6
- **Data Visualization:** Recharts
- **Geospatial Mapping:** Leaflet, React Leaflet, OpenStreetMap
- **Icons & UI:** Lucide React
- **HTTP Client:** Axios

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Data Validation & Schemas:** Pydantic v2
- **ORM & Database Access:** SQLAlchemy 2.0
- **Authentication:** JWT (JSON Web Tokens) with passlib / bcrypt
- **ASGI Server:** Uvicorn
- **Testing:** Pytest

### Database & Storage
- **Database:** SQLite (for local MVP demo) with PostgreSQL-ready schema architecture
- **File Storage:** Local file system for geo-tagged evidence images and generated PDF reports

### AI / ML & Analytics
- **Core Library:** scikit-learn, NumPy, Pandas
- **Models:**
  - Cost Overrun Regressor (Predictive regression on project scale, duration, and milestone variance)
  - Time Overrun Classifier / Estimator (Schedule slippage forecasting)
  - Rule-Based Risk Intelligence Fusion (Ensemble weighted risk index: Low / Medium / High / Critical)

### Reporting & Documentation
- **Report Generation:** PDF Report Generator (structured executive summaries)
- **API Documentation:** OpenAPI / Swagger UI (`/docs`), ReDoc (`/redoc`)

---

## 📁 Project Structure

```
SetuX-GitHub/
├── backend/
│   ├── app/
│   │   ├── api/            # API route controllers (projects, milestones, alerts, etc.)
│   │   ├── auth/           # Authentication routes, security & dependencies
│   │   ├── core/           # Core configuration, database engine & security
│   │   ├── database/       # Database session management & base models
│   │   ├── ml/             # ML overrun predictors & training scripts
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── pipeline/       # Data ingestion & feature engineering pipeline
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic (risk, cost analysis, alerts, reports)
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # Backend pytest test suite
│   ├── uploads/            # Evidence uploads and generated PDF reports
│   ├── .env.example        # Backend environment template
│   ├── pytest.ini          # Pytest configuration
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── public/             # Static public assets, branding & icons
│   ├── src/
│   │   ├── assets/         # Images, SVG icons and styling assets
│   │   ├── components/     # Reusable React components (ProtectedRoute, ErrorBoundary)
│   │   ├── context/        # React context providers (AuthContext, ThemeContext)
│   │   ├── data/           # Client fallback / demo project datasets
│   │   ├── pages/          # Application views (Dashboard, Projects, Analytics, GIS, etc.)
│   │   ├── services/       # Axios API client services
│   │   ├── utils/          # Formatting helpers and utility functions
│   │   ├── App.jsx         # Main application component & routes
│   │   ├── index.css       # Global styles & design system tokens
│   │   └── main.jsx        # React DOM entry point
│   ├── .env.example        # Frontend environment template
│   ├── package.json        # Frontend package manifest & scripts
│   ├── tailwind.config.js  # Tailwind CSS design tokens
│   └── vite.config.js      # Vite build configuration
│
├── docs/                   # System documentation, API contracts & architecture specs
│   └── screenshots/        # Dashboard screenshots and presentation assets
│
├── scripts/
│   └── seed_database.py    # Database initialization and sample data generator
│
├── .env.example            # Global environment configuration template
├── .gitignore              # Git ignore rules for Python, Node, environment & caches
├── docker-compose.yml      # Containerized deployment definition
├── HOW_TO_RUN.md           # Quick setup guide for reviewers
├── setup-first-time.bat    # Automated Windows one-click setup script
├── start-backend.bat       # Windows helper to launch FastAPI backend
├── start-frontend.bat      # Windows helper to launch Vite frontend
├── start-all.bat           # Windows helper to launch both services
└── README.md               # Project documentation (this file)
```

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python 3.10 or newer** (with pip added to PATH)
- **Node.js 18 or newer** (LTS recommended)
- **Git**

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/SetuX.git
cd SetuX
```

---

### Step 2: Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows:**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Seed the local SQLite database with realistic demonstration projects:
   ```bash
   python ../scripts/seed_database.py
   ```

---

### Step 3: Frontend Setup

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

---

## 🚀 Running the Application

### Option A: Using Windows Batch Scripts (Easiest)

From the project root directory:
1. Run `setup-first-time.bat` once to create environments and install dependencies.
2. Run `start-backend.bat` to launch the API server.
3. Run `start-frontend.bat` to launch the Vite development server.

---

### Option B: Manual Execution

#### Terminal 1 — Backend API Server
```bash
cd backend
# Ensure virtual environment is activated
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 — Frontend Development Server
```bash
cd frontend
npm run dev
```

---

## 🌐 Application URLs & Credentials

| Service | URL | Description |
| :--- | :--- | :--- |
| **Web Application** | [http://localhost:5173](http://localhost:5173) | Main SetuX web portal |
| **Interactive API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for exploring REST endpoints |
| **Alternative API Docs** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc interface |
| **API Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Backend health status endpoint |

### Demo Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Monitoring Officer / Admin** | `admin_pune` | `password` |
| **Citizen Portal** | Public Access | No credentials required |

---

## 📖 API Documentation & Modules

SetuX provides a comprehensive REST API organized into modular endpoints:

- **Authentication (`/api/auth`):** Login, token refresh, and user profile management.
- **Projects (`/api/projects`):** Project CRUD, financial/physical progress, status filtering, and GIS coordinates.
- **Milestones (`/api/milestones`):** Milestone lifecycle, completion percentages, target vs. actual dates.
- **Evidence (`/api/evidence`):** Geo-tagged image upload, verification status, and audit metadata.
- **Issues (`/api/issues`):** Project issue logging, severity assignment, resolution workflows.
- **Contractors (`/api/contractors`):** Contractor performance profiles, past delays, and active package allocations.
- **Departments (`/api/departments`):** Departmental portfolio management and aggregated statistics.
- **Analytics & ML (`/api/analytics`):** Risk score computation, cost/schedule overrun predictions, and KPI summaries.
- **Alerts (`/api/alerts`):** Early warning alert triggers, acknowledgment, and escalation logs.
- **Reports (`/api/reports`):** Automated executive briefing and early warning PDF generation.
- **Audit (`/api/audit`):** Immutable event logs capturing administrative actions and milestone approvals.

---

## 🧠 Risk Intelligence & ML Pipeline

The SetuX risk intelligence engine combines deterministic rule-based indicators with supervised statistical machine learning to provide transparent, explainable decision support:

```
Structured Project Ingestion (Baseline dates, BOQ, expenditure, contractor history)
                           ↓
Feature Engineering (Milestone variance ratio, disbursement lag, active issue count)
                           ↓
Supervised Predictive Models (scikit-learn Cost Overrun Regressor & Delay Estimator)
                           ↓
Rule-Based Risk Fusion (Weighted ensemble: Low, Medium, High, Critical)
                           ↓
Explainable Output (Top risk drivers + recommended officer interventions)
```

> **Note on AI/ML Outputs:** Machine learning forecasts are predictive decision-support aids derived from historical and milestone trends. They are designed to assist officers in prioritizing inspections and interventions, not to replace formal administrative audits.

---

## 📷 Screenshots & Visuals

Screenshots and presentation artifacts are available in the [`docs/screenshots/`](docs/screenshots/) folder:
- **Command Center:** Executive project portfolio overview and health metrics.
- **Risk Intelligence & GIS Map:** Spatial risk heatmap and corridor tracking.
- **Milestone & Evidence Inspection:** Geo-tagged validation logs and audit checkpoints.

---

## 📋 Project Status & Verification

SetuX is a prototype / Minimum Viable Product (MVP) developed for **Smart India Hackathon 2026** under Problem Statement `SIH26103`.

---

## 📄 License

License: To be determined.

---

<div align="center">
  <sub>Developed by <b>Team VeriX</b> for <b>Smart India Hackathon 2026</b></sub>
</div>
"""

readme_path = os.path.join(TARGET_DIR, "README.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme_content)

print(f"Created comprehensive README.md at: {readme_path}")
