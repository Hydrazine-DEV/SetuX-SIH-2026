import os
from app.database.database import init_db, SessionLocal, engine
from app.database.models import User, Department
from app.auth.schemas import UserSignUp, UserLogin
from app.auth.routes import sign_up, login, get_me
from app.auth.dependencies import get_current_user
from fastapi.security import HTTPAuthorizationCredentials

def test_persistence():
    print("=== STEP 17: DATABASE PERSISTENCE TEST ===")
    
    # Initialize DB (creates setux.db if not exists, keeps existing data)
    init_db()

    email = "testofficer@setux.demo"
    password = "Officer@123"

    # Step A: Register new test officer
    db1 = SessionLocal()
    try:
        # Cleanup prior test officer if exists
        existing = db1.query(User).filter(User.email == email).first()
        if existing:
            db1.delete(existing)
            db1.commit()

        print("1. Registering new Officer: testofficer@setux.demo ...")
        signup_req = UserSignUp(
            full_name="Test Officer",
            email=email,
            phone="9876543210",
            password=password,
            confirm_password=password,
            role="officer",
            department_id=1
        )
        resp = sign_up(signup_req, db1)
        assert resp.user.email == email
        print("   [OK] Officer account created successfully.")
    finally:
        db1.close()

    # Step B: Dispose database connections to simulate backend restart
    engine.dispose()
    print("2. Backend engine disposed & restarted (Simulating server restart)...")

    # Step C: Re-open DB session and verify officer STILL EXISTS in setux.db
    db2 = SessionLocal()
    try:
        persisted_user = db2.query(User).filter(User.email == email).first()
        assert persisted_user is not None, "FAILED: User record lost after restart!"
        assert persisted_user.full_name == "Test Officer"
        assert persisted_user.role == "officer"
        assert persisted_user.password_hash.startswith("$2b$")
        print(f"   [OK] Verified record exists in setux.db! ID: {persisted_user.id}, Hash: {persisted_user.password_hash[:15]}...")

        # Step D: Login with the persisted account
        print("3. Logging in with persisted credentials ...")
        login_req = UserLogin(
            email=email,
            password=password,
            role="officer"
        )
        login_resp = login(login_req, db2)
        assert login_resp.access_token is not None
        print(f"   [OK] Authentication successful! JWT Token generated: {login_resp.access_token[:25]}...")

        # Step E: Verify /me endpoint
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=login_resp.access_token)
        current = get_current_user(creds, db2)
        me = get_me(current)
        assert me.email == email
        print(f"   [OK] GET /api/auth/me returned authenticated user: {me.full_name} ({me.role})")

        print("\n=== PERSISTENCE TEST PASSED 100%! DATA IS SAFELY STORED IN SETUX.DB ===")

    finally:
        db2.close()

if __name__ == "__main__":
    test_persistence()
