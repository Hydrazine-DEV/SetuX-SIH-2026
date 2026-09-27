# How to run SetuX on another computer

This zip contains the **source code only** (no `node_modules` or Python `venv`).  
Install dependencies once on the new machine, then start backend + frontend.

## What you need

- **Python 3.10 or newer** — https://www.python.org/downloads/  
  During install, tick **Add Python to PATH**.
- **Node.js 18 or newer** (LTS recommended) — https://nodejs.org/
- A modern browser (Chrome / Edge / Firefox)

Open **two terminals** after setup. Keep both running while you demo.

---

## First-time setup (once)

From the unzipped `setux` folder:

### Windows (easiest)

Double-click **`setup-first-time.bat`**, wait until it finishes.

Or run the same steps yourself:

```bat
cd setux
python -m venv backend\venv
backend\venv\Scripts\python -m pip install -r backend\requirements.txt
backend\venv\Scripts\python scripts\seed_database.py
cd frontend
npm install
```

### macOS / Linux

```bash
cd setux
python3 -m venv backend/venv
backend/venv/bin/python -m pip install -r backend/requirements.txt
backend/venv/bin/python scripts/seed_database.py
cd frontend
npm install
```

---

## Start the app (every time)

### Windows

1. Double-click **`start-backend.bat`** — wait until you see the API start.
2. Double-click **`start-frontend.bat`**
3. Open **http://localhost:5173**

### macOS / Linux

**Terminal 1 — API**

```bash
cd setux/backend
source venv/bin/activate
python -m uvicorn app.main:app --port 8000
```

**Terminal 2 — UI**

```bash
cd setux/frontend
npm run dev
```

Then open **http://localhost:5173**

---

## Demo login

- Username: `admin_pune`
- Password: `password`

## URLs

| What | URL |
|------|-----|
| App | http://localhost:5173 |
| API health | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |

---

## If something fails

| Problem | Fix |
|---------|-----|
| `python` not found | Reinstall Python and enable **Add to PATH**, then open a new terminal |
| `npm` not found | Install Node.js LTS, then open a new terminal |
| Port 8000 already in use | Close other apps using 8000, or change `--port` in the backend start command |
| Port 5173 already in use | Vite will pick the next free port — use the URL printed in the frontend terminal |
| Empty / old database | Run `backend\venv\Scripts\python scripts\seed_database.py` again from the `setux` folder |
| Map tiles missing | Needs internet (OpenStreetMap). The rest of the app still works offline |

The frontend still works if the API is down: it falls back to built-in demo project data.
