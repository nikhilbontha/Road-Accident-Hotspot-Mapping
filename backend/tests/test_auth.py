import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User, UserStatusEnum, UserRoleEnum
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.notification import Notification
        db.query(Notification).delete()
        users = db.query(User).filter(User.email.like("%@test.in")).all()
        for u in users:
            db.delete(u)
        db.commit()
    finally:
        db.close()
    yield

def test_register_creates_pending_user():
    payload = {
        "full_name": "Test Vikram Singh",
        "email": "vikram@test.in",
        "organisation": "Hyderabad Traffic Police",
        "role": "police_officer",
        "password": "Password1234!",
        "policy_agreement": True,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert "approves new accounts" in data["message"].lower()

def test_pending_user_cannot_login():
    # Register pending user
    payload = {
        "full_name": "Pending User",
        "email": "pending@test.in",
        "organisation": "Road Safety Cell",
        "role": "safety_analyst",
        "password": "Password1234!",
    }
    client.post("/api/v1/auth/register", json=payload)

    # Attempt login
    login_res = client.post("/api/v1/auth/login", json={"email": "pending@test.in", "password": "Password1234!"})
    assert login_res.status_code == 403
    assert "waiting for approval" in login_res.json()["detail"].lower()

def test_invalid_credentials():
    login_res = client.post("/api/v1/auth/login", json={"email": "nonexistent@test.in", "password": "WrongPassword!"})
    assert login_res.status_code == 401
    assert "invalid email or password" in login_res.json()["detail"].lower()

def test_active_user_login_and_me():
    db = SessionLocal()
    try:
        active_user = User(
            full_name="Asha Reddy",
            email="asha@test.in",
            organisation="National Highway Authority",
            role=UserRoleEnum.SAFETY_ANALYST,
            password_hash=get_password_hash("Password1234!"),
            status=UserStatusEnum.ACTIVE,
        )
        db.add(active_user)
        db.commit()
    finally:
        db.close()

    # Login
    login_res = client.post("/api/v1/auth/login", json={"email": "asha@test.in", "password": "Password1234!"})
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["user"]["email"] == "asha@test.in"

    # Test /auth/me
    token = tokens["access_token"]
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "asha@test.in"

def test_deactivated_user_cannot_login():
    db = SessionLocal()
    try:
        deactivated_user = User(
            full_name="Deactivated User",
            email="deactivated@test.in",
            organisation="Police Dept",
            role=UserRoleEnum.POLICE_OFFICER,
            password_hash=get_password_hash("Password1234!"),
            status=UserStatusEnum.DEACTIVATED,
        )
        db.add(deactivated_user)
        db.commit()
    finally:
        db.close()

    login_res = client.post("/api/v1/auth/login", json={"email": "deactivated@test.in", "password": "Password1234!"})
    assert login_res.status_code == 403
    assert "deactivated" in login_res.json()["detail"].lower()
