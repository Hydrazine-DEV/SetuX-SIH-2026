# SetuX / VeriX — Frontend Developer Handoff Document

**Target Audience:** Frontend AI / Full-Stack Developer  
**Status:** BACKEND API FROZEN & PRODUCTION-READY  
**Base URL:** `http://127.0.0.1:8000`  
**Swagger UI:** `http://127.0.0.1:8000/docs`  
**API Specification Document:** `docs/API_CONTRACT.md`  
**Frontend Integration Guide:** `docs/FRONTEND_INTEGRATION.md`

---

## 1. Executive Summary

The SetuX / VeriX backend system is completely implemented, hardened, tested, and frozen. The API endpoints provide full coverage for authentication, RBAC, project management, milestone tracking, progress update logging, issue reporting, site evidence uploads, platform analytics, rule-based risk evaluation, cost/time machine learning predictions, risk intelligence aggregation, early warning alerts, and executive PDF report generation.

---

## 2. Quick Integration Reference

### A. Authentication & Headers
- **Login Endpoint:** `POST /api/auth/login`
- **Signup Endpoint:** `POST /api/auth/signup`
- **Current User Profile:** `GET /api/auth/me`
- **Header:** Include `Authorization: Bearer <access_token>` on all requests requiring authentication.

### B. Core Data Endpoints
- **List Monitored Projects:** `GET /api/projects` (Supports `search`, `status`, `department_id`, `risk_level` query params)
- **Get Project Details:** `GET /api/projects/{id}`
- **Project Milestones:** `GET /api/projects/{id}/milestones`
- **Project Progress Updates:** `GET /api/projects/{id}/progress`
- **Project Issues:** `GET /api/projects/{id}/issues`

### C. AI Intelligence & Risk Panel Endpoints
- **Rule-Based Risk Baseline:** `GET /api/projects/{id}/risk`
- **Cost Overrun ML Classifier:** `GET /api/projects/{id}/prediction/cost-overrun` *(Alias: `/cost-prediction`)*
- **Time Overrun ML Classifier:** `GET /api/projects/{id}/prediction/time-overrun` *(Alias: `/time-prediction`)*
- **Overall Risk Intelligence:** `GET /api/projects/{id}/risk-intelligence` *(Alias: `/intelligence`)*

---

## 3. Recommended User Journeys & Screen Wiring

```
[ 1. Login / Signup Screen ]
       │
       ▼
[ 2. Executive Dashboard ] ──────────► GET /api/analytics/summary
       │
       ├──────────────────────────────► GET /api/alerts
       │
       ▼
[ 3. Project Directory Screen ] ──────► GET /api/projects
       │
       ▼
[ 4. Project Details Screen ] ────────► GET /api/projects/{id}
       │
       ├── Milestones Tab ────────────► GET /api/projects/{id}/milestones
       ├── Progress History Tab ──────► GET /api/projects/{id}/progress
       ├── Issues & Observations Tab ─► GET /api/projects/{id}/issues
       │
       ▼
[ 5. AI Risk Intelligence Panel ] ───► GET /api/projects/{id}/risk-intelligence
       │
       ├── PDF Report Generation ─────► POST /api/projects/{id}/reports
       └── Download PDF ──────────────► GET /api/reports/{id}/download
```

---

## 4. Key Developer Policies & Guidelines

1. **API Freeze:** The backend contract is strictly frozen. No fields will be renamed or restructured arbitrarily.
2. **Handling Nulls & Unfilled Fields:** Optional parameters (e.g. `actual_completion_date`, `revised_cost`) return `null` if unpopulated. Always use optional chaining (`project?.revised_cost ?? project?.original_cost`) in JavaScript.
3. **ML Feature Availability:** Check `is_available: true` in prediction responses before attempting to render prediction probabilities or top factor attributions.
4. **Backend Change Requests:** If an unexpected integration blocker is encountered, request a targeted backend hotfix adhering to the frozen contract schema.

---

## 5. Contact & Support

For API questions or integration support, refer to the OpenAPI docs at `http://127.0.0.1:8000/docs` or consult `docs/API_CONTRACT.md`.

