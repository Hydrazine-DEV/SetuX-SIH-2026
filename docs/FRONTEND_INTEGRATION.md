# SetuX / VeriX — Frontend Integration Guide

**Target Application:** React + Vite / Next.js Web Frontend  
**Backend Target URL:** `http://127.0.0.1:8000` (Local Dev) / `http://localhost:8000`  
**API Specification:** `docs/API_CONTRACT.md`

---

## 1. Authentication Flow & Token Management

### 1. Obtaining JWT Access Token
When a user logs in via `POST /api/auth/login` or registers via `POST /api/auth/signup`, the backend returns a JSON payload:

```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "Executive Engineer Patil",
    "email": "patil@setux.gov.in",
    "role": "officer",
    "department_id": 1,
    "department_name": "Public Works Department"
  }
}
```

### 2. Token Storage & Session Persistence
- Store `access_token` in `localStorage` or `sessionStorage` under the key `setux_jwt_token`.
- Store `user` object in your Auth Context / Redux / Zustand state.

### 3. Axios / Fetch Interceptor Setup
Attach the Bearer token to every outgoing HTTP request:

```javascript
// Example Axios Configuration
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("setux_jwt_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 2. HTTP Error Handling Matrix

The frontend must implement structured error handling based on status codes returned by FastAPI:

| HTTP Code | Exception Meaning | Recommended Frontend Action |
| :--- | :--- | :--- |
| `401 Unauthorized` | Invalid, expired, or missing JWT token | Clear stored token and redirect user to `/login`. |
| `403 Forbidden` | Citizen attempting Officer action | Display toast notification: *"Access Restricted: Officer permissions required."* |
| `404 Not Found` | Non-existent Project ID or Resource | Display standard Empty State / "Project Not Found" page component. |
| `422 Unprocessable Entity` | Pydantic validation error (e.g. progress > 100) | Extract `detail[0].msg` and show field validation error on form. |
| `500 Internal Error` | Unexpected backend error | Display fallback error boundary card with retry button. |

---

## 3. UI Component to Backend API Mapping

### A. Main Dashboard Overview
- **API Endpoint:** `GET /api/analytics/summary`
- **Data Displayed:** Total Projects, Total Sanctioned Cost, Total Expenditure, Physical Progress Avg, Risk Level distribution pie chart.

### B. Project Directory / Listing Page
- **API Endpoint:** `GET /api/projects`
- **Query Filters:** `search`, `status`, `department_id`, `risk_level`
- **Data Displayed:** Project card grid, status badges, health score progress bars.

### C. Project Details Page
- **API Endpoint:** `GET /api/projects/{id}`
- **Sub-Entities:**
  - Milestones: `GET /api/projects/{id}/milestones`
  - Progress Updates: `GET /api/projects/{id}/progress`
  - Issues & Observations: `GET /api/projects/{id}/issues`

### D. AI Risk & Intelligence Panel
- **Primary Endpoint:** `GET /api/projects/{id}/risk-intelligence`
- **Fallback / Direct Sub-Endpoints:**
  - Rule-Based Risk Baseline: `GET /api/projects/{id}/risk`
  - Cost ML Overrun Prediction: `GET /api/projects/{id}/prediction/cost-overrun`
  - Time ML Overrun Prediction: `GET /api/projects/{id}/prediction/time-overrun`

---

## 4. Handling AI/ML Risk & Prediction States

ML model predictions are decoupled from rule-based baseline risks. Always check `is_available` in the response before rendering ML cards:

```jsx
// React Component Rendering Pattern for ML Prediction Card
function CostPredictionCard({ predictionData }) {
  if (!predictionData || !predictionData.is_available) {
    return (
      <div className="card-muted">
        <span>Cost Overrun ML Prediction Unavailable</span>
        <small>{predictionData?.error || "Model training artifact pending."}</small>
      </div>
    );
  }

  const { prediction, probability, top_factors } = predictionData;
  const isHighRisk = prediction === "COST_OVERRUN";

  return (
    <div className={`card ${isHighRisk ? "border-danger" : "border-success"}`}>
      <h4>Cost Overrun Risk: {(probability * 100).toFixed(1)}%</h4>
      <p>Prediction: {prediction}</p>
      <ul>
        {top_factors.map((f, i) => (
          <li key={i}>{f.feature}: {(f.importance * 100).toFixed(1)}% impact</li>
        ))}
      </ul>
    </div>
  );
}
```

### Risk Level Color Standard
Match backend risk categories to visual UI badges:
- `LOW`: Soft Green (`#18864B` / `bg-emerald-100 text-emerald-800`)
- `MEDIUM`: Amber Yellow (`#C47A00` / `bg-amber-100 text-amber-800`)
- `HIGH`: Crimson Red (`#C0392B` / `bg-rose-100 text-rose-800`)
- `CRITICAL`: Deep Burgundy / Flashing Alert (`#7F1D1D` / `bg-red-900 text-white animate-pulse`)

---

## 5. Early Warning Alerts & PDF Reports Integration

- **Trigger Alerts:** `POST /api/projects/{id}/alerts/generate`
- **Fetch Project Alerts:** `GET /api/projects/{id}/alerts`
- **Generate Report:** `POST /api/projects/{id}/reports` with payload `{"report_type": "EXECUTIVE_PROJECT_REPORT"}`
- **Download PDF File:** `GET /api/reports/{report_id}/download` (Set browser `window.open` or create hidden download link with response BLOB).

