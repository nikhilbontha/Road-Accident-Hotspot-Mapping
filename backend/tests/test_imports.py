import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User, UserStatusEnum, UserRoleEnum
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_import_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test analyst user
    analyst = db.query(User).filter(User.email == "import_analyst@test.in").first()
    if not analyst:
        analyst = User(
            full_name="Import Analyst",
            email="import_analyst@test.in",
            organisation="State Road Safety Cell",
            role=UserRoleEnum.SAFETY_ANALYST,
            password_hash=get_password_hash("Password1234!"),
            status=UserStatusEnum.ACTIVE,
        )
        db.add(analyst)
        db.commit()
    db.close()
    yield

def test_template_download():
    response = client.get("/api/v1/imports/template")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "accident_code" in response.text
    assert "NH-65 × Station Road Junction" in response.text

def test_import_pipeline_with_seeded_issues():
    # Login as analyst
    login_res = client.post("/api/v1/auth/login", json={"email": "import_analyst@test.in", "password": "Password1234!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_csv_path = os.path.join(os.path.dirname(__file__), "sample_with_issues.csv")
    with open(sample_csv_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/imports",
            files={"file": ("sample_with_issues.csv", f, "text/csv")},
            headers=headers,
        )

    assert upload_res.status_code == 201
    data = upload_res.json()
    batch_id = data["id"]
    assert data["total_rows"] == 7

    # Verify Privacy Masking (BR-03, FR-12)
    masked = data["masked_counts"]
    assert masked["vehicle_numbers"] > 0
    assert masked["phone_numbers"] > 0
    assert masked["names"] > 0

    # Verify Issues detection (duplicates, invalid coords, invalid time, negative values)
    issues_res = client.get(f"/api/v1/imports/{batch_id}/issues", headers=headers)
    assert issues_res.status_code == 200
    issues = issues_res.json()
    issue_types = {i["issue_type"] for i in issues}

    assert "duplicate" in issue_types
    assert "invalid_coordinate" in issue_types
    assert "invalid_date_time" in issue_types
    assert "negative_value" in issue_types
    assert "address_only" in issue_types

    # Test resolving an issue
    target_issue = next(i for i in issues if i["issue_type"] == "duplicate")
    patch_res = client.patch(
        f"/api/v1/imports/{batch_id}/issues/{target_issue['id']}",
        json={"action": "skip", "resolved": True},
        headers=headers,
    )
    assert patch_res.status_code == 200

    # Test Commit
    commit_res = client.post(f"/api/v1/imports/{batch_id}/commit", headers=headers)
    assert commit_res.status_code == 200
    assert commit_res.json()["committed_records"] > 0
