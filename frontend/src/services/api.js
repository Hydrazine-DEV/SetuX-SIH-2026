/**
 * SetuX — API Service Layer
 * All backend communication goes through this module.
 */
import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// ─── Authorization Header Interceptor ────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem("setux_jwt_token") || localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor (Handle Token Expiry) ──────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear invalid / expired tokens
      localStorage.removeItem("setux_jwt_token");
      localStorage.removeItem("token");
    }
    return Promise.reject(error);
  }
);

// ─── Authentication ───────────────────────────────────────────────────────
export const authApi = {
  signup: (data) => api.post("/api/auth/signup", data),
  login: (data) => api.post("/api/auth/login", data),
  getMe: () => api.get("/api/auth/me"),
  logout: () => api.post("/api/auth/logout"),
  getDepartments: () => api.get("/api/departments"),
};

// ─── Projects ────────────────────────────────────────────────────────────
export const projectsApi = {
  list: (params = {}) => api.get("/api/projects/", { params }),
  getById: (id) => api.get(`/api/projects/${id}`),
  update: (id, data) => api.put(`/api/projects/${id}`, data),
  getMilestones: (id) => api.get(`/api/projects/${id}/milestones`),
  getProgress: (id) => api.get(`/api/projects/${id}/progress`),
  getLatestProgress: (id) => api.get(`/api/projects/${id}/progress/latest`),
  createProgress: (id, data) => api.post(`/api/projects/${id}/progress`, data),
  getStats: () => api.get("/api/projects/stats"),
  updateStatus: (id, status, risk_level) =>
    api.put(`/api/projects/${id}/status`, null, { params: { status, risk_level } }),

  // ─── Phase 6: Risk Intelligence ──────────────────────────────────────────
  getRiskIntelligence: (id) => api.get(`/api/projects/${id}/risk-intelligence`),
  getProjectRisk: (id) => api.get(`/api/projects/${id}/risk`),
  getCostOverrunPrediction: (id) => api.get(`/api/projects/${id}/prediction/cost-overrun`),
  getTimeOverrunPrediction: (id) => api.get(`/api/projects/${id}/prediction/time-overrun`),
};

// ─── Evidence / Field Updates ─────────────────────────────────────────────
export const evidenceApi = {
  submit: (data) =>
    api.post("/api/evidence/upload", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  getByProject: (projectId) => api.get(`/api/evidence/${projectId}`),
};

// ─── Verification / AI Analytics ──────────────────────────────────────────
export const verificationApi = {
  run: (data) => api.post("/api/verification/run", data),
  getByProject: (projectId) => api.get(`/api/verification/${projectId}`),
};

// ─── Analytics & Reports ──────────────────────────────────────────────────
export const analyticsApi = {
  getSummary: () => api.get("/api/analytics/summary"),
  getDistricts: () => api.get("/api/analytics/districts"),
  getPriority: () => api.get("/api/analytics/priority"),
  getTrends: () => api.get("/api/analytics/trends"),
};

// ─── Audit ────────────────────────────────────────────────────────────────
export const auditApi = {
  list: (limit = 50) => api.get("/api/audit/", { params: { limit } }),
  getByProject: (projectId) => api.get(`/api/audit/${projectId}`),
};

// ─── Report Generation ────────────────────────────────────────────────────
export const reportApi = {
  getByProject: (projectId) => api.get(`/api/projects/${projectId}/reports`),
  getMetadata: (reportId) => api.get(`/api/reports/${reportId}`),
  generate: (projectId, reportType = "PROJECT_SUMMARY") =>
    api.post(`/api/projects/${projectId}/reports`, { report_type: reportType }),
  download: (reportId) =>
    api.get(`/api/reports/${reportId}/download`, { responseType: "blob" }),
};

// ─── Early Warning Alerts ──────────────────────────────────────────────────
export const alertsApi = {
  list: (params = {}) => api.get("/api/alerts", { params }),
  getById: (alertId) => api.get(`/api/alerts/${alertId}`),
  getByProject: (projectId, params = {}) => api.get(`/api/projects/${projectId}/alerts`, { params }),
  generateForProject: (projectId) => api.post(`/api/projects/${projectId}/alerts/generate`),
  generateAll: () => api.post("/api/alerts/generate-all"),
  markRead: (alertId) => api.patch(`/api/alerts/${alertId}/read`),
  markResolved: (alertId) => api.patch(`/api/alerts/${alertId}/resolve`),
  markDismissed: (alertId) => api.patch(`/api/alerts/${alertId}/dismiss`),
};

export default api;
