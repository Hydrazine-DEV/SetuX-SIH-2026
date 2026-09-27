# API Specifications

All endpoints are hosted at `http://localhost:8000/api/` by default.

## Projects

* **GET `/projects/`**: Lists all projects. Supports query filtering by `district`, `department`, `status`, `risk_level`, `project_type`.
* **GET `/projects/stats`**: Aggregated status count KPIs.
* **GET `/projects/{project_id}`**: Retrieves a single project detail by its project ID code.
* **PUT `/projects/{project_id}/status`**: Updates project verification status.

## Evidence

* **POST `/evidence/submit`**: Field officers submit progress status, coordinate geolocations, and remarks.
* **GET `/evidence/{project_id}`**: List all submitted media logs for a specific project.

## Verification

* **POST `/verification/run`**: Triggers the verification engine pipeline and calculates anomalies.
* **GET `/verification/{project_id}`**: Fetches the latest computed verification results.

## Analytics

* **GET `/analytics/summary`**: Renders general state completion percentages and manual audit rates.
* **GET `/analytics/districts`**: Breakdown counts by district.
* **GET `/analytics/priority`**: Retrieves prioritized list of projects requiring inspection first.
