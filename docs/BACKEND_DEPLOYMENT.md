# SetuX / VeriX — Backend Deployment & Operational Guide

**System Name:** SetuX / VeriX — AI-Powered Infrastructure Verification Platform  
**SIH Problem Statement:** SIH26103  
**Backend Architecture:** FastAPI + SQLAlchemy + SQLite / PostgreSQL + Scikit-Learn ML  
**Python Version:** Python 3.10+ (Tested on Python 3.13.2)

---

## 1. System Requirements & Environment Prerequisites

- **Operating System:** Windows 10/11 / Linux (Ubuntu 22.04 LTS) / macOS
- **Python:** Version `3.10.x` or higher (`3.13.2` recommended)
- **RAM:** Minimum 2 GB (4 GB recommended for ML inference loading)
- **Disk Space:** 500 MB for virtual environment and SQLite database

---

## 2. Local Environment Setup & Virtual Environment

1. Navigate to the backend directory:
   ```bash
   cd setux/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   - **Windows (CMD):** `.\venv\Scripts\activate.bat`
   - **Linux / macOS:** `source venv/bin/activate`

4. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Configuration & Environment Variables

Copy `.env.example` to `.env` in the `backend/` directory:

```bash
cp .env.example .env
```

### Supported Environment Variables (`.env`)

| Variable Key | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `verix-setux-sih2026-authentication-secret-key-32bytes` | JWT signing secret key |
| `ALGORITHM` | `HS256` | JWT encoding algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time in minutes |
| `DATABASE_URL` | `sqlite:///./setux.db` | SQLAlchemy database URI |

---

## 4. Database Setup & Initialization

The database auto-initializes on startup if tables do not exist. To pre-seed the database with 30 realistic Maharashtra infrastructure projects:

```bash
$env:PYTHONPATH="."
.\venv\Scripts\python.exe scripts/seed_database.py
```

---

## 5. Development & Production Startup Commands

### Development Server (Uvicorn with Auto-reload)
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Production Server (Multi-worker Gunicorn / Uvicorn)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 6. System Verification Endpoints

- **Health Endpoint:** `http://127.0.0.1:8000/health` (`GET`)
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON Schema:** `http://127.0.0.1:8000/openapi.json`

---

## 7. Common Troubleshooting & Support

- **`ModuleNotFoundError: No module named 'app'`**
  - Fix: Ensure `PYTHONPATH` environment variable is set to the `backend/` directory prior to running scripts or pytest.
- **Port 8000 already in use**
  - Fix: Specify an alternative port (e.g. `--port 8001`) or terminate the existing Uvicorn process.
- **`sqlite3.OperationalError: database is locked`**
  - Fix: Ensure concurrent write processes are closed or migrate `DATABASE_URL` to a PostgreSQL instance for high concurrency.

---

## 8. Backend Test Suite

To run all 188 automated backend security, integration, and ML prediction tests:

```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe -m pytest
```

