import os
from app.database.database import init_db, SessionLocal, Base, engine
from app.database.models import User, Department
from app.auth.schemas import UserSignUp, UserLogin
from app.auth.routes import sign_up, login, get_me, logout, get_departments
from app.auth.dependencies import get_current_user
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

def run_direct_tests():
    print("=== STARTING DIRECT ROUTE & DB TESTS ===")
    Base.metadata.drop_all(bind=engine)
    init_db()
    db = SessionLocal()

    try:
        # 1. Get Departments
        depts = get_departments(db)
        print(f"[OK] 1. Departments fetched: {len(depts)} items")
        assert len(depts) >= 5

        # 2. Officer Sign Up
        officer_req = UserSignUp(
            full_name="Ayush Salunkhe",
            email="ayush.officer@example.com",
            phone="9876543210",
            password="password123",
            confirm_password="password123",
            role="officer",
            department_id=1
        )
        token_resp = sign_up(officer_req, db)
        assert token_resp.access_token is not None
        assert token_resp.user.role == "officer"
        assert token_resp.user.department_id == 1
        print("[OK] 2. Officer Sign Up successful")

        # 3. Citizen Sign Up
        citizen_req = UserSignUp(
            full_name="Rahul Patil",
            email="rahul.citizen@example.com",
            phone="9876543210",
            password="password123",
            confirm_password="password123",
            role="citizen"
        )
        token_resp = sign_up(citizen_req, db)
        assert token_resp.access_token is not None
        assert token_resp.user.role == "citizen"
        assert token_resp.user.department_id is None
        print("[OK] 3. Citizen Sign Up successful")

        # 4. Duplicate Email
        try:
            sign_up(officer_req, db)
            assert False, "Should have raised duplicate email error"
        except HTTPException as e:
            assert e.status_code == 400
            assert "already exists" in e.detail
            print("[OK] 4. Duplicate email rejected successfully")

        # 5. Password Mismatch
        mismatch_req = UserSignUp(
            full_name="Test User",
            email="mismatch@example.com",
            phone="9876543210",
            password="password123",
            confirm_password="differentpassword",
            role="officer"
        )
        try:
            sign_up(mismatch_req, db)
            assert False, "Should have raised password mismatch error"
        except HTTPException as e:
            assert e.status_code == 400
            assert "do not match" in e.detail
            print("[OK] 5. Password mismatch rejected successfully")

        # 6. Invalid Login Password
        invalid_login_req = UserLogin(
            email="ayush.officer@example.com",
            password="wrongpassword",
            role="officer"
        )
        try:
            login(invalid_login_req, db)
            assert False, "Should have rejected bad password"
        except HTTPException as e:
            assert e.status_code == 401
            assert e.detail == "Invalid email or password."
            print("[OK] 6. Invalid password login rejected successfully")

        # 7. Role Mismatch
        role_mismatch_req = UserLogin(
            email="ayush.officer@example.com",
            password="password123",
            role="citizen"
        )
        try:
            login(role_mismatch_req, db)
            assert False, "Should have rejected role mismatch"
        except HTTPException as e:
            assert e.status_code == 403
            assert "not authorized" in e.detail
            print("[OK] 7. Role mismatch login rejected successfully")

        # 8. Valid Officer Login & JWT Bearer Token Retrieval
        officer_login_req = UserLogin(
            email="ayush.officer@example.com",
            password="password123",
            role="officer"
        )
        officer_token_obj = login(officer_login_req, db)
        assert officer_token_obj.access_token is not None
        print("[OK] 8. Valid Officer Login successful")

        # 9. GET /me dependency verification with Bearer token
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=officer_token_obj.access_token)
        current_user = get_current_user(creds, db)
        me_result = get_me(current_user)
        assert me_result.full_name == "Ayush Salunkhe"
        assert me_result.role == "officer"
        assert me_result.department.name == "Public Works Department"
        print("[OK] 9. GET /api/auth/me token validation successful")

        # 10. Valid Citizen Login & GET /me
        citizen_login_req = UserLogin(
            email="rahul.citizen@example.com",
            password="password123",
            role="citizen"
        )
        citizen_token_obj = login(citizen_login_req, db)
        creds_cit = HTTPAuthorizationCredentials(scheme="Bearer", credentials=citizen_token_obj.access_token)
        current_cit_user = get_current_user(creds_cit, db)
        me_cit_result = get_me(current_cit_user)
        assert me_cit_result.full_name == "Rahul Patil"
        assert me_cit_result.role == "citizen"
        assert me_cit_result.department is None
        print("[OK] 10. Valid Citizen Login and GET /me validation successful")

        # 11. Seed Account Logins
        seed_off_login = UserLogin(email="officer1@setux.demo", password="Officer@123", role="officer")
        assert login(seed_off_login, db).access_token is not None
        print("[OK] 11. Demo Officer seed account login successful")

        seed_cit_login = UserLogin(email="citizen1@setux.demo", password="Citizen@123", role="citizen")
        assert login(seed_cit_login, db).access_token is not None
        print("[OK] 12. Demo Citizen seed account login successful")

        print("\n=== ALL 12 DIRECT BACKEND TESTS PASSED 100%! ===")

    finally:
        db.close()

if __name__ == "__main__":
    run_direct_tests()
