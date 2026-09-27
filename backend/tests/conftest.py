"""
Pytest configuration and shared fixtures for SetuX backend testing.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.core.database import Base
from app.database.database import get_db, init_db
from app.main import app
from app.models.user import Department, User
from app.core.security import hash_password, create_access_token

# Test database in memory or temp file
TEST_DATABASE_URL = "sqlite:///./test_setux.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables and seed required initial data before running tests."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    # Seed initial test departments if needed
    departments = [
        {"name": "Public Works Department", "code": "PWD", "description": "Roads, Bridges and Buildings"},
        {"name": "Water Resources Department", "code": "WRD", "description": "Irrigation, Canals, and Water Supply"},
        {"name": "Rural Development Department", "code": "RDD", "description": "Rural roads, Gram Panchayat works"},
        {"name": "Urban Development Department", "code": "UDD", "description": "Municipal corporations and smart cities"},
        {"name": "Energy Department", "code": "ENG", "description": "Power infrastructure and electrification"},
    ]
    for d in departments:
        dept = Department(name=d["name"], code=d["code"], description=d["description"])
        db.add(dept)

    # Seed test users
    officer = User(
        full_name="Officer Test",
        email="test.officer@setux.gov",
        password_hash=hash_password("OfficerPass123"),
        role="officer",
        department_id=1,
        department_name="Public Works Department",
        is_active=True,
    )
    citizen = User(
        full_name="Citizen Test",
        email="test.citizen@setux.gov",
        password_hash=hash_password("CitizenPass123"),
        role="citizen",
        department_id=None,
        is_active=True,
    )
    inactive_user = User(
        full_name="Inactive Officer",
        email="inactive.officer@setux.gov",
        password_hash=hash_password("OfficerPass123"),
        role="officer",
        department_id=1,
        is_active=False,
    )
    db.add_all([officer, citizen, inactive_user])
    db.commit()
    db.close()

    yield

    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_setux.db"):
        try:
            os.remove("./test_setux.db")
        except Exception:
            pass


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def officer_token():
    return create_access_token({"sub": "test.officer@setux.gov", "role": "officer", "name": "Officer Test"})


@pytest.fixture
def citizen_token():
    return create_access_token({"sub": "test.citizen@setux.gov", "role": "citizen", "name": "Citizen Test"})
