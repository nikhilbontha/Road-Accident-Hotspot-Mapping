import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.notification import Notification

client = TestClient(app)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    # Clean up existing if any
    existing = db_session.query(User).filter(User.email == "analyst.phase5@police.gov.in").first()
    if existing:
        db_session.query(Notification).filter(Notification.user_id == existing.id).delete()
        db_session.delete(existing)
        db_session.commit()

    user = User(
        email="analyst.phase5@police.gov.in",
        full_name="Asha Phase5",
        role=UserRoleEnum.SAFETY_ANALYST,
        organisation="Traffic Safety Division",
        password_hash=get_password_hash("Password123!"),
        status=UserStatusEnum.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.query(Notification).filter(Notification.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()

@pytest.fixture
def auth_headers(test_user):
    role_val = test_user.role.value if hasattr(test_user.role, "value") else str(test_user.role)
    token = create_access_token(subject=test_user.id, role=role_val)
    return {"Authorization": f"Bearer {token}"}

def test_dashboard_summary(auth_headers):
    res = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "accidents" in data
    assert "fatalities" in data
    assert "hotspots" in data
    assert data["accidents"]["value"] > 0

def test_dashboard_monthly(auth_headers):
    res = client.get("/api/v1/dashboard/monthly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    assert "accidents" in data[0]

def test_dashboard_risk_distribution(auth_headers):
    res = client.get("/api/v1/dashboard/risk-distribution", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] > 0
    assert "critical" in data

def test_dashboard_heat_grid(auth_headers):
    res = client.get("/api/v1/dashboard/heat-grid", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "matrix" in data
    assert len(data["days"]) == 7
    assert len(data["time_blocks"]) == 8

def test_dashboard_top_hotspots(auth_headers):
    res = client.get("/api/v1/dashboard/top-hotspots", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_notifications_lifecycle(auth_headers, test_user, db_session):
    # Get initial notifications
    res = client.get("/api/v1/notifications", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "unread_count" in data

    # Create real notification for user
    notif = Notification(
        user_id=test_user.id,
        type="critical_detected",
        title="Test Alert",
        body="Test alert body",
        is_read=False
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    # Mark single read
    res = client.post(f"/api/v1/notifications/{notif.id}/read", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    # Mark all read
    res = client.post("/api/v1/notifications/read-all", headers=auth_headers)
    assert res.status_code == 200

    # Settings get & put
    res = client.get("/api/v1/notifications/settings", headers=auth_headers)
    assert res.status_code == 200
    assert "critical_detected" in res.json()

    res = client.put("/api/v1/notifications/settings", json={"critical_detected": False}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["critical_detected"] is False

def test_reports_crud(auth_headers):
    # Create PDF report
    res = client.post("/api/v1/reports", json={
        "type": "summary",
        "format": "pdf",
        "period": "Dec 2025 – Nov 2026"
    }, headers=auth_headers)
    assert res.status_code == 200
    rep_pdf = res.json()
    assert "download_url" in rep_pdf

    # Create CSV report
    res = client.post("/api/v1/reports", json={
        "type": "trends",
        "format": "csv",
        "period": "Dec 2025 – Nov 2026"
    }, headers=auth_headers)
    assert res.status_code == 200
    rep_csv = res.json()
    assert rep_csv["format"] == "csv"

    # List reports
    res = client.get("/api/v1/reports", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 2

    # Download report
    res = client.get(f"/api/v1/reports/{rep_csv['id']}/download", headers=auth_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")

def test_ai_assistant(auth_headers):
    # Suggestions
    res = client.get("/api/v1/assistant/suggestions")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # Grounded query for H-0142
    res = client.post("/api/v1/assistant/chat", json={"message": "What caused crashes at H-0142?"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "H-0142" in data["citations"]
    assert len(data["cited_hotspots"]) > 0
    assert "caveats" in data

    # Out of scope query
    res = client.post("/api/v1/assistant/chat", json={"message": "Who will win the next election?"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data.get("is_out_of_scope") is True
