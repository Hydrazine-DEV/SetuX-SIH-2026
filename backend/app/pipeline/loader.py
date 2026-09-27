"""
SetuX / VeriX — Data Loader Module
Phase 12: Multi-Source Raw Data Loading & Synthetic Dev Data Generation
"""
import os
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.project import Project
from app.models.milestone import Milestone
from app.models.progress import ProgressUpdate
from app.models.issue import Issue


def load_raw_project_data(
    db: Optional[Session] = None,
    csv_path: Optional[str] = None,
    json_records: Optional[List[Dict[str, Any]]] = None,
) -> pd.DataFrame:
    """
    Load raw project data from Database, CSV, or JSON records into a pandas DataFrame.
    """
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df["data_source"] = f"CSV:{os.path.basename(csv_path)}"
        return df

    if json_records is not None:
        df = pd.DataFrame(json_records)
        df["data_source"] = "JSON_RECORDS"
        return df

    # Load from SQLAlchemy Database
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        projects = db.query(Project).all()
        records = []

        for p in projects:
            milestones = db.query(Milestone).filter(Milestone.project_id == p.id).all()
            progress_updates = db.query(ProgressUpdate).filter(ProgressUpdate.project_id == p.id).all()
            issues = db.query(Issue).filter(Issue.project_id == p.id).all()

            rec = {
                "project_id": p.id,
                "project_code": p.project_code,
                "name": p.name,
                "sector": p.sector,
                "department_name": p.department_name,
                "district": p.district,
                "state": p.state,
                "contractor_name": p.contractor_name,
                "original_cost": p.original_cost,
                "revised_cost": p.revised_cost,
                "expenditure": p.total_expenditure if p.total_expenditure is not None else 0.0,
                "total_expenditure": p.total_expenditure if p.total_expenditure is not None else 0.0,
                "start_date": p.start_date,
                "planned_completion_date": p.planned_completion_date,
                "revised_completion_date": p.revised_completion_date,
                "actual_completion_date": p.actual_completion_date,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "status": p.status,
                "risk_level": p.risk_level,
                "anomaly_score": p.anomaly_score,
                "created_at": str(p.created_at) if p.created_at else None,
                # Aggregated sub-entity metrics
                "total_milestones": len(milestones),
                "completed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "COMPLETED"),
                "delayed_milestones": sum(1 for m in milestones if (m.status or "").upper() == "DELAYED"),
                "progress_update_count": len(progress_updates),
                "latest_update_progress": progress_updates[-1].physical_progress if progress_updates else None,
                "total_issues": len(issues),
                "open_issues": sum(1 for i in issues if (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
                "critical_issues": sum(1 for i in issues if (i.severity or "").upper() == "CRITICAL" and (i.status or "").upper() in ("OPEN", "IN_PROGRESS")),
                "data_source": "SQL_DATABASE",
            }
            records.append(rec)

        df = pd.DataFrame(records)
        return df

    finally:
        if should_close and db:
            db.close()


def load_project_data_from_db(db: Optional[Session] = None) -> pd.DataFrame:
    """Load project data from database."""
    return load_raw_project_data(db=db)


def load_project_data_from_csv(csv_path: str) -> pd.DataFrame:
    """Load project data from CSV file."""
    return load_raw_project_data(csv_path=csv_path)


def load_project_data_from_json(json_records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Load project data from JSON records."""
    return load_raw_project_data(json_records=json_records)


def generate_synthetic_dev_dataset(
    n_samples: int = 50,
    random_state: int = 42,
    num_projects: Optional[int] = None,
    random_seed: Optional[int] = None,
) -> pd.DataFrame:
    """
    Generate a synthetic development dataset ONLY for data pipeline testing.
    Explicitly labeled as SYNTHETIC_DEVELOPMENT_ONLY — never presented as government/historical data.
    """
    if num_projects is not None:
        n_samples = num_projects
    if random_seed is not None:
        random_state = random_seed

    np.random.seed(random_state)

    sectors = ["Road Construction", "Bridge", "School", "Water Pipeline", "Drainage", "Government Building"]
    districts = ["Pune", "Nashik", "Nagpur", "Thane", "Satara", "Kolhapur"]
    departments = ["Public Works Department", "PMC", "PCMC", "MIDC", "ZP Education", "NMC"]
    statuses = ["Under Review", "Verified", "Review Required", "Delayed", "Completed"]

    records = []
    for i in range(1, n_samples + 1):
        orig_cost = float(np.random.choice([100, 250, 500, 750, 1000, 1500, 2000]))
        has_overrun = np.random.rand() > 0.6
        rev_cost = round(orig_cost * np.random.uniform(1.10, 1.40), 2) if has_overrun else orig_cost
        expenditure = round(orig_cost * np.random.uniform(0.20, 0.95), 2)

        is_completed = np.random.rand() < 0.35
        if is_completed:
            phys_prog = 100.0
            fin_prog = 100.0
            status = "Completed"
        else:
            phys_prog = round(float(np.random.uniform(10.0, 95.0)), 1)
            fin_prog = round(float(np.random.uniform(10.0, 95.0)), 1)
            status = np.random.choice(statuses[:4])

        start_year = np.random.choice([2024, 2025])
        start_month = np.random.randint(1, 12)
        start_date = f"{start_year}-{start_month:02d}-01"

        planned_year = start_year + 1
        planned_completion_date = f"{planned_year}-{start_month:02d}-28"

        actual_completion_date = None
        revised_completion_date = None

        if status == "Completed":
            delay_months = int(np.random.choice([0, 0, 1, 2, 4, 6]))
            comp_m = start_month + delay_months
            comp_year = planned_year + (comp_m - 1) // 12
            comp_month = ((comp_m - 1) % 12) + 1
            actual_completion_date = f"{comp_year}-{comp_month:02d}-28"
        elif status == "Delayed" or np.random.rand() < 0.25:
            rev_m = start_month + int(np.random.choice([2, 4, 6, 8]))
            rev_year = planned_year + (rev_m - 1) // 12
            rev_month = ((rev_m - 1) % 12) + 1
            revised_completion_date = f"{rev_year}-{rev_month:02d}-28"

        total_m = int(np.random.randint(3, 8))
        delayed_m = int(np.random.randint(0, min(3, total_m)))

        total_iss = int(np.random.randint(0, 5))
        open_iss = int(np.random.randint(0, max(1, total_iss + 1))) if total_iss > 0 else 0
        crit_iss = 1 if (open_iss > 0 and np.random.rand() > 0.7) else 0

        rec = {
            "project_id": i,
            "project_code": f"SYN-MH-{i:03d}",
            "name": f"Synthetic Development Project {i}",
            "sector": np.random.choice(sectors),
            "department_name": np.random.choice(departments),
            "district": np.random.choice(districts),
            "state": "Maharashtra",
            "contractor_name": f"Synthetic Contractor {i % 5 + 1}",
            "original_cost": orig_cost,
            "revised_cost": rev_cost,
            "expenditure": expenditure,
            "start_date": start_date,
            "planned_completion_date": planned_completion_date,
            "revised_completion_date": revised_completion_date,
            "actual_completion_date": actual_completion_date,
            "physical_progress": phys_prog,
            "financial_progress": fin_prog,
            "status": status,
            "total_milestones": total_m,
            "completed_milestones": total_m - delayed_m,
            "delayed_milestones": delayed_m,
            "progress_update_count": np.random.randint(1, 5),
            "total_issues": total_iss,
            "open_issues": open_iss,
            "critical_issues": crit_iss,
            "data_source": "SYNTHETIC_DEVELOPMENT_ONLY",
        }
        records.append(rec)

    return pd.DataFrame(records)
