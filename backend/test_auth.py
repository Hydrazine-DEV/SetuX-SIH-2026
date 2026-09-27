import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import init_db, SessionLocal
from app.models import User

init_db()
client = TestClient(app)

def run_tests():
    print("=== STARTING AUTHENTICATION VERIFICATION TESTS ===")
    
    # Cleanup any prior test users to ensure idempotency
    db = SessionLocal()
    try:
        db.query(User).filter(User.email.in_([
            "ayush.officer@example.com",
            "rahul.citizen@example.com",
            "new.officer@example.com",
            "short.officer@example.com"
        ])).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()
    
    # 1. Department Listing
    res = client.get("/api/departments")
    assert res.status_code == 200, f"Get departments failed: {res.text}"
    departments = res.json()
    assert len(departments) >= 5, f"Expected at least 5 departments, got {len(departments)}"
    print("[OK] 1. Departments listing test passed.")

    # 2. Officer Sign Up
    officer_payload = {
        "full_name": "Ayush Salunkhe",
        "email": "ayush.officer@example.com",
        "phone": "9876543210",
        "password": "password123",
        "confirm_password": "password123",
        "role": "officer",
        "department_id": 1
    }
    res = client.post("/api/auth/signup", json=officer_payload)
    assert res.status_code == 200, f"Officer signup failed: {res.text}"
    data = res.json()
    assert "access_token" in data, "Token missing in response"
    assert data["user"]["role"] == "officer"
    assert data["user"]["department_id"] == 1
    assert data["user"]["department"]["name"] == "Public Works Department"
    print("[OK] 2. Officer signup test passed.")

    # 3. Citizen Sign Up
    citizen_payload = {
        "full_name": "Rahul Patil",
        "email": "rahul.citizen@example.com",
        "phone": "9876543210",
        "password": "password123",
        "confirm_password": "password123",
        "role": "citizen"
    }
    res = client.post("/api/auth/signup", json=citizen_payload)
    assert res.status_code == 200, f"Citizen signup failed: {res.text}"
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "citizen"
    assert data["user"]["department_id"] is None
    assert data["user"]["department"] is None
    print("[OK] 3. Citizen signup test passed.")

    # 4. Duplicate Email Prevention
    res = client.post("/api/auth/signup", json=officer_payload)
    assert res.status_code == 400, f"Expected 400 for duplicate email, got {res.status_code}"
    assert "already exists" in res.json()["detail"]
    print("[OK] 4. Duplicate email prevention test passed.")

    # 5. Password Mismatch Validation
    bad_match_payload = {**officer_payload, "email": "new.officer@example.com", "confirm_password": "wrongpassword"}
    res = client.post("/api/auth/signup", json=bad_match_payload)
    assert res.status_code == 400, f"Expected 400 for password mismatch, got {res.status_code}"
    assert "Passwords do not match" in res.json()["detail"]
    print("[OK] 5. Password mismatch validation test passed.")

    # 6. Weak Password Validation
    short_pw_payload = {**officer_payload, "email": "short.officer@example.com", "password": "123", "confirm_password": "123"}
    res = client.post("/api/auth/signup", json=short_pw_payload)
    assert res.status_code in (400, 422), f"Expected 400/422 for short password, got {res.status_code}"
    print("[OK] 6. Password length validation test passed.")

    # 7. Invalid Login Credentials (wrong password)
    res = client.post("/api/auth/login", json={"email": "ayush.officer@example.com", "password": "wrongpassword", "role": "officer"})
    assert res.status_code == 401, f"Expected 401 for bad password, got {res.status_code}"
    assert res.json()["detail"] == "Invalid email or password."
    print("[OK] 7. Invalid login credentials test passed.")

    # 8. Role Mismatch Prevention
    res = client.post("/api/auth/login", json={"email": "ayush.officer@example.com", "password": "password123", "role": "citizen"})
    assert res.status_code == 403, f"Expected 403 for role mismatch, got {res.status_code}"
    assert "not authorized to login as this role" in res.json()["detail"]
    print("[OK] 8. Role mismatch prevention test passed.")

    # 9. Valid Officer Login
    res = client.post("/api/auth/login", json={"email": "ayush.officer@example.com", "password": "password123", "role": "officer"})
    assert res.status_code == 200, f"Officer login failed: {res.text}"
    officer_token = res.json()["access_token"]
    print("[OK] 9. Valid officer login test passed.")

    # 10. Valid Citizen Login
    res = client.post("/api/auth/login", json={"email": "rahul.citizen@example.com", "password": "password123", "role": "citizen"})
    assert res.status_code == 200, f"Citizen login failed: {res.text}"
    citizen_token = res.json()["access_token"]
    print("[OK] 10. Valid citizen login test passed.")

    # 11. GET /api/auth/me for Officer
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {officer_token}"})
    assert res.status_code == 200, f"/me for officer failed: {res.text}"
    user_me = res.json()
    assert user_me["role"] == "officer"
    assert user_me["department"]["name"] == "Public Works Department"
    print("[OK] 11. GET /me for officer test passed.")

    # 12. GET /api/auth/me for Citizen
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 200, f"/me for citizen failed: {res.text}"
    user_me = res.json()
    assert user_me["role"] == "citizen"
    assert user_me["department"] is None
    print("[OK] 12. GET /me for citizen test passed.")

    # 13. Logout
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    print("[OK] 13. Logout test passed.")

    # 14. Demo Seed Account Logins
    res = client.post("/api/auth/login", json={"email": "officer1@setux.demo", "password": "Officer@123", "role": "officer"})
    assert res.status_code == 200, f"Demo officer login failed: {res.text}"
    print("[OK] 14. Demo seed officer login test passed.")

    res = client.post("/api/auth/login", json={"email": "citizen1@setux.demo", "password": "Citizen@123", "role": "citizen"})
    assert res.status_code == 200, f"Demo citizen login failed: {res.text}"
    print("[OK] 15. Demo seed citizen login test passed.")

    print("\nALL 15 AUTHENTICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
