# SetuX / VeriX — Backend API Contract (Frozen Specification)

**Platform:** SIH 2026 — Problem Statement SIH26103  
**Backend Stack:** Python 3.13 + FastAPI + SQLAlchemy + SQLite / PostgreSQL + Scikit-Learn ML  
**Version:** `2.0.0-frozen`  
**Base URL (Local Development):** `http://127.0.0.1:8000`  
**Interactive API Docs (Swagger):** `http://127.0.0.1:8000/docs`  
**ReDoc UI:** `http://127.0.0.1:8000/redoc`

---

## 1. Authentication & Security Policy

All protected endpoints require HTTP Bearer authentication via standard JWT tokens.

### Authorization Header Format
```http
Authorization: Bearer <jwt_access_token>
```

### User Roles & Access Control Matrix (RBAC)
- **OFFICER (`officer`):** Full read/write access. Can create/update projects, add milestones, submit progress updates, generate alerts, trigger verification runs, generate/download PDF reports.
- **CITIZEN (`citizen`):** Read-only access to public project listings, analytics summaries, and risk intelligence dashboards. Restricted from administrative POST/PUT/DELETE actions.

### Authentication Endpoints

#### `POST /api/auth/signup`
Registers a new user account (Officer or Citizen).

- **Auth Required:** No
- **Request Body (`UserSignUp`):**
  ```json
  {
    "full_name": "Executive Engineer Patil",
    "email": "patil@setux.gov.in",
    "phone": "9876543210",
    "password": "SecurePassword@123",
    "confirm_password": "SecurePassword@123",
    "role": "officer",
    "department_id": 1
  }
  ```
- **Success Response (`200 OK` - `TokenResponse`):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "user": {
      "id": 5,
      "full_name": "Executive Engineer Patil",
      "email": "patil@setux.gov.in",
      "role": "officer",
      "department_id": 1,
      "department_name": "Public Works Department",
      "is_active": true,
      "is_verified": false,
      "created_at": "2026-09-22T23:30:00Z"
    }
  }
  ```
- **Error Responses:** `400 Bad Request` (Password < 8 chars, mismatch, invalid role, or email already registered).

#### `POST /api/auth/login`
Authenticates credentials, validates active status & role match, returns signed JWT access token.

- **Auth Required:** No
- **Request Body (`UserLogin`):**
  ```json
  {
    "email": "patil@setux.gov.in",
    "password": "SecurePassword@123",
    "role": "officer"
  }
  ```
- **Success Response (`200 OK` - `TokenResponse`):** Returns JWT access token and user profile object.
- **Error Responses:** `401 Unauthorized` (Invalid credentials), `403 Forbidden` (Role mismatch).

#### `GET /api/auth/me`
Retrieves current authenticated user profile.

- **Auth Required:** Yes (`Bearer`)
- **Success Response (`200 OK` - `UserResponse`):** Returns authenticated user schema.
- **Error Responses:** `401 Unauthorized` (Missing/invalid/expired token).

#### `POST /api/auth/logout`
Terminates current user session context.

- **Auth Required:** Optional / Client-side token discard.
- **Success Response (`200 OK`):** `{"message": "Successfully logged out"}`

---

## 2. Core Operational Endpoints

### Departments & Contractors

- `GET /api/departments` — List all infrastructure departments (`200 OK`)
- `POST /api/departments` — Create department (Officer only, `201 Created`)
- `GET /api/contractors` — List registered contractors (`200 OK`)
- `POST /api/contractors` — Register new contractor (Officer only, `201 Created`)

---

## 3. Project Management API Contract

### `GET /api/projects`
Retrieves list of monitored infrastructure projects with filtering and search.

- **Auth Required:** Yes
- **Query Parameters:**
  - `search` (string, optional) — Filter by project code, name, contractor, district.
  - `status` (string, optional) — Filter by project status (`PLANNED`, `IN_PROGRESS`, `DELAYED`, `COMPLETED`).
  - `department_id` (integer, optional) — Filter by department.
  - `risk_level` (string, optional) — Filter by evaluated risk (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Success Response (`200 OK`):** Array of Project objects.

### `GET /api/projects/{project_id}`
Retrieves complete details for a single project by database ID or string project code (`e.g., MH-PN-009`).

- **Auth Required:** Yes
- **Success Response (`200 OK` - `ProjectResponse`):**
  ```json
  {
    "id": 9,
    "project_code": "MH-PN-009",
    "name": "Kondhwa Road Repair & Pothole Filling",
    "department_id": 1,
    "department_name": "Public Works Department",
    "sector": "Roads & Bridges",
    "district": "Pune",
    "taluka": "Haveli",
    "state": "Maharashtra",
    "contractor_id": 2,
    "contractor_name": "Prakash Construction Ltd",
    "original_cost": 85.0,
    "revised_cost": 102.0,
    "total_expenditure": 65.0,
    "start_date": "2026-01-15",
    "planned_completion_date": "2026-08-30",
    "revised_completion_date": "2026-10-15",
    "actual_completion_date": null,
    "physical_progress": 62.5,
    "financial_progress": 76.47,
    "status": "IN_PROGRESS",
    "health_score": 68.5,
    "risk_level": "MEDIUM",
    "created_at": "2026-01-10T10:00:00Z"
  }
  ```
- **Error Response:** `404 Not Found` if project ID does not exist.

### `POST /api/projects`
Creates a new monitored infrastructure project.

- **Auth Required:** Yes (Officer only)
- **Request Body (`ProjectCreate`):** Required fields: `project_code`, `name`, `department_id`, `original_cost`.

---

## 4. Sub-Entity APIs (Milestones, Progress, Issues, Evidence)

- `GET /api/projects/{project_id}/milestones` — List project milestones.
- `POST /api/projects/{project_id}/milestones` — Add milestone.
- `GET /api/projects/{project_id}/progress` — List progress updates.
- `POST /api/projects/{project_id}/progress` — Log physical & financial progress update.
- `GET /api/projects/{project_id}/issues` — List reported site issues & observations.
- `POST /api/projects/{project_id}/issues` — Submit site issue.
- `POST /api/evidence/upload` — Upload site evidence image (`.jpg`, `.jpeg`, `.png`, `.webp`, max 10MB).

---

## 5. Analytics, Risk Engine & Machine Learning Contracts

### `GET /api/projects/{project_id}/risk`
Evaluates Phase 11 Rule-Based Risk baseline.

- **Success Response (`200 OK`):**
  ```json
  {
    "project_id": 9,
    "project_code": "MH-PN-009",
    "risk_score": 14.72,
    "risk_level": "LOW",
    "factors": [
      {
        "factor": "COST_OVERRUN",
        "severity": "MEDIUM",
        "score_contribution": 10.0,
        "details": "Revised cost exceeds original budget by 20.0%."
      }
    ]
  }
  ```

### `GET /api/projects/{project_id}/prediction/cost-overrun` *(Alias: `/cost-prediction`)*
Runs Phase 13 Cost Overrun ML Classifier model inference.

- **Success Response (`200 OK`):**
  ```json
  {
    "is_available": true,
    "project_id": 9,
    "project_code": "MH-PN-009",
    "prediction": "COST_OVERRUN",
    "probability": 1.0,
    "has_overrun_risk": true,
    "cost_overrun_threshold_pct": 5.0,
    "model_name": "Cost Overrun ML Classifier",
    "model_version": "v1.0.0",
    "top_factors": [
      {"feature": "cost_escalation_ratio", "importance": 0.35, "current_value": 1.20},
      {"feature": "financial_physical_diff", "importance": 0.28, "current_value": 13.97}
    ],
    "disclaimer": "Estimates cost-overrun risk from historical data."
  }
  ```

### `GET /api/projects/{project_id}/prediction/time-overrun` *(Alias: `/time-prediction`)*
Runs Phase 14 Time Overrun ML Classifier model inference.

- **Success Response (`200 OK`):**
  ```json
  {
    "is_available": true,
    "project_id": 9,
    "project_code": "MH-PN-009",
    "prediction": "TIME_OVERRUN",
    "probability": 0.5675,
    "has_overrun_risk": true,
    "time_overrun_threshold_days": 30,
    "model_name": "Time Overrun ML Classifier",
    "model_version": "v1.0.0",
    "top_factors": [
      {"feature": "schedule_elapsed_pct", "importance": 0.40, "current_value": 82.5},
      {"feature": "delayed_milestones_ratio", "importance": 0.25, "current_value": 0.33}
    ]
  }
  ```

### `GET /api/projects/{project_id}/risk-intelligence` *(Alias: `/intelligence`)*
Comprehensive Phase 15 Risk Intelligence endpoint combining observed operational signals, rule engine baseline, Cost ML, Time ML, data quality audit, and natural language summary.

- **Success Response (`200 OK`):**
  ```json
  {
    "is_available": true,
    "project_id": 9,
    "project_code": "MH-PN-009",
    "overall_risk": {
      "score": 34.98,
      "level": "MEDIUM",
      "rule_based_baseline_score": 14.72,
      "predictive_ml_score": 78.38,
      "calculation_name": "SetuX Overall Risk Intelligence Score",
      "version": "v1.0.0"
    },
    "cost_overrun_prediction": {
      "is_available": true,
      "prediction": "COST_OVERRUN",
      "probability": 1.0,
      "model_name": "Cost Overrun ML Classifier"
    },
    "time_overrun_prediction": {
      "is_available": true,
      "prediction": "TIME_OVERRUN",
      "probability": 0.5675,
      "model_name": "Time Overrun ML Classifier"
    },
    "prioritized_risk_factors": [
      {
        "factor": "COST_OVERRUN_ML_PREDICTION",
        "category": "COST",
        "type": "PREDICTIVE",
        "severity": "CRITICAL",
        "explanation": "Machine Learning model predicts 100.0% probability of budget cost overrun."
      }
    ],
    "data_quality": {
      "status": "COMPLETE",
      "available_components": ["rule_based_risk_engine", "cost_overrun_ml_model", "time_overrun_ml_model"],
      "missing_components": [],
      "missing_data_fields": []
    },
    "summary": "Project overall risk is classified as MEDIUM (Score: 35.0/100) driven primarily by Cost Overrun ML Prediction, Time Overrun ML Prediction.",
    "recommended_actions": [
      "Audit financial disbursement progress against verified physical work completed to control cost overspending.",
      "Review project completion schedule and request an updated milestone recovery plan from contractor."
    ],
    "disclaimer": "Engineering decision-support score combining observed indicators and predictive models."
  }
  ```

---

## 6. Alerts & Reports Contracts

- `GET /api/alerts` — List all early warning alerts (`200 OK`).
- `POST /api/projects/{project_id}/alerts/generate` — Trigger automated alert evaluation (`200 OK`).
- `POST /api/projects/{project_id}/reports` — Generate executive PDF report (`201 Created`).
- `GET /api/projects/{project_id}/reports` — List generated reports for project (`200 OK`).
- `GET /api/reports/{report_id}/download` — Stream PDF binary (`application/pdf`, `200 OK`).

---

## 7. System Health Endpoint

- `GET /health` — `{"status": "ok", "demo": true, "uploads_mounted": true}` (`200 OK`).

