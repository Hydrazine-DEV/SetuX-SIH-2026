"""
SetuX — Database configuration
Supports both SQLite (local development/testing) and PostgreSQL (production).
Re-exports core database components and provides table initialization and baseline seeding.
"""
from sqlalchemy import inspect, text
from app.core.database import engine, SessionLocal, Base, get_db
import app.models  # Ensures all 10 core models are registered with Base.metadata


def init_db():
    from app.models import Department, User
    from app.core.security import hash_password

    inspector = inspect(engine)
    # In development/prototype: detect schema drift on legacy users or projects table
    if inspector.has_table("users"):
        cols = {c["name"] for c in inspector.get_columns("users")}
        expected_cols = {"full_name", "department_id", "department_name", "designation"}
        if not expected_cols.issubset(cols):
            Base.metadata.drop_all(bind=engine)
            
    if inspector.has_table("projects"):
        p_cols = {c["name"] for c in inspector.get_columns("projects")}
        expected_p_cols = {"project_code", "sector", "original_cost", "department_name"}
        if not expected_p_cols.issubset(p_cols):
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    # Safe non-destructive column additions for sqlite tables
    inspector = inspect(engine)
    if inspector.has_table("alerts"):
        alert_cols = {c["name"] for c in inspector.get_columns("alerts")}
        with engine.connect() as conn:
            if "status" not in alert_cols:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN status VARCHAR(50) DEFAULT 'UNREAD'"))
            if "source" not in alert_cols:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN source VARCHAR(100) DEFAULT 'RULE_ENGINE'"))
            if "metadata_json" not in alert_cols:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN metadata_json TEXT"))
            if "resolved_at" not in alert_cols:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN resolved_at DATETIME"))
            if "resolved_by" not in alert_cols:
                conn.execute(text("ALTER TABLE alerts ADD COLUMN resolved_by VARCHAR(255)"))
            conn.commit()

    if inspector.has_table("reports"):
        rpt_cols = {c["name"] for c in inspector.get_columns("reports")}
        with engine.connect() as conn:
            if "file_name" not in rpt_cols:
                conn.execute(text("ALTER TABLE reports ADD COLUMN file_name VARCHAR(255)"))
            if "file_size" not in rpt_cols:
                conn.execute(text("ALTER TABLE reports ADD COLUMN file_size INTEGER DEFAULT 0"))
            if "status" not in rpt_cols:
                conn.execute(text("ALTER TABLE reports ADD COLUMN status VARCHAR(50) DEFAULT 'GENERATED'"))
            conn.commit()

    # Baseline seed: Departments and Demo Officers/Citizens
    db = SessionLocal()
    try:
        if db.query(Department).count() == 0:
            departments_data = [
                Department(id=1, name="Public Works Department", code="PWD", description="Roads, bridges, government buildings"),
                Department(id=2, name="Municipal Corporation", code="PMC", description="Civic infrastructure and local utilities"),
                Department(id=3, name="Rural Development", code="RD", description="Rural connectivity, water and sanitation"),
                Department(id=4, name="Water Resources", code="WR", description="Irrigation, dams and water supply"),
                Department(id=5, name="Urban Development", code="UD", description="Urban planning, metro and smart cities"),
            ]
            db.add_all(departments_data)
            db.commit()

        if db.query(User).count() == 0:
            demo_users = [
                User(
                    full_name="Officer Ramesh Patil",
                    email="officer1@setux.demo",
                    phone="9876543210",
                    password_hash=hash_password("Officer@123"),
                    role="officer",
                    department_id=1,
                    is_active=True,
                    is_verified=True,
                ),
                User(
                    full_name="Officer Sunita Sharma",
                    email="officer2@setux.demo",
                    phone="9876543211",
                    password_hash=hash_password("Officer@123"),
                    role="officer",
                    department_id=2,
                    is_active=True,
                    is_verified=True,
                ),
                User(
                    full_name="Citizen Rahul Deshmukh",
                    email="citizen1@setux.demo",
                    phone="9876543212",
                    password_hash=hash_password("Citizen@123"),
                    role="citizen",
                    department_id=None,
                    is_active=True,
                    is_verified=True,
                ),
                User(
                    full_name="Citizen Priya Verma",
                    email="citizen2@setux.demo",
                    phone="9876543213",
                    password_hash=hash_password("Citizen@123"),
                    role="citizen",
                    department_id=None,
                    is_active=True,
                    is_verified=True,
                ),
            ]
            db.add_all(demo_users)
            db.commit()
    finally:
        db.close()
