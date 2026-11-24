import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User, UserStatusEnum, UserRoleEnum
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_rbac_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.email.like("%@rbac.in")).all()
        for u in users:
            db.delete(u)
        db.commit()

        admin = User(
            full_name="Dr. Kiran Rao",
            email="admin@rbac.in",
            organisation="State Transport Dept",
            role=UserRoleEnum.ADMIN,
            password_hash=get_password_hash("AdminPass123!"),
            status=UserStatusEnum.ACTIVE,
        )
        analyst = User(
            full_name="Analyst User",
            email="analyst@rbac.in",
            organisation="Research Lab",
            role=UserRoleEnum.SAFETY_ANALYST,
            password_hash=get_password_hash("AnalystPass123!"),
            status=UserStatusEnum.ACTIVE,
        )
        db.add_all([admin, analyst])
        db.commit()
    finally:
        db.close()
    yield

def test_admin_can_access_user_management():
    # Login as admin
    login_res = client.post("/api/v1/auth/login", json={"email": "admin@rbac.in", "password": "AdminPass123!"})
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]

    users_res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert users_res.status_code == 200
    users = users_res.json()
    assert len(users) >= 2

def test_non_admin_cannot_access_user_management():
    # Login as analyst
    login_res = client.post("/api/v1/auth/login", json={"email": "analyst@rbac.in", "password": "AnalystPass123!"})
    assert login_res.status_code == 200
    analyst_token = login_res.json()["access_token"]

    users_res = client.get("/api/v1/users", headers={"Authorization": f"Bearer {analyst_token}"})
    assert users_res.status_code == 403
    assert "not permitted" in users_res.json()["detail"].lower()

def test_admin_approve_and_deactivate_flow():
    # Register a new pending user
    reg_payload = {
        "full_name": "New Candidate",
        "email": "candidate@rbac.in",
        "organisation": "City Authority",
        "role": "authority_official",
        "password": "Password1234!",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_id = reg_res.json()["id"]

    # Login as admin
    admin_login = client.post("/api/v1/auth/login", json={"email": "admin@rbac.in", "password": "AdminPass123!"})
    admin_token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin approves user
    approve_res = client.post(f"/api/v1/users/{user_id}/approve", headers=headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "active"

    # User can now log in
    cand_login = client.post("/api/v1/auth/login", json={"email": "candidate@rbac.in", "password": "Password1234!"})
    assert cand_login.status_code == 200

    # Admin deactivates user
    deact_res = client.post(f"/api/v1/users/{user_id}/deactivate", headers=headers)
    assert deact_res.status_code == 200
    assert deact_res.json()["status"] == "deactivated"

    # User can no longer log in
    cand_login_after = client.post("/api/v1/auth/login", json={"email": "candidate@rbac.in", "password": "Password1234!"})
    assert cand_login_after.status_code == 403
