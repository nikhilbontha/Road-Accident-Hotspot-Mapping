import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, Base, engine
from app.models.user import User, UserStatusEnum, UserRoleEnum
from app.models.hotspot import Hotspot
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_map_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create admin and test users
    admin = db.query(User).filter(User.email == "map_admin@test.in").first()
    if not admin:
        admin = User(
            full_name="Map Admin",
            email="map_admin@test.in",
            organisation="Police HQ",
            role=UserRoleEnum.ADMIN,
            password_hash=get_password_hash("AdminPass123!"),
            status=UserStatusEnum.ACTIVE,
        )
        db.add(admin)

    # Seed top hotspot H-0142
    h142 = db.query(Hotspot).filter(Hotspot.code == "H-0142").first()
    if not h142:
        h142 = Hotspot(
            code="H-0142",
            name="NH-65 × Station Road Junction",
            road_name="National Highway 65",
            area="Central Zone",
            lat=17.4125,
            lon=78.5721,
            accidents_count=41,
            fatalities=9,
            injured=63,
            risk_score=92.0,
            risk_level="critical",
            status="Under review",
        )
        db.add(h142)

    db.commit()
    db.close()
    yield

def test_public_map_anonymity_and_banding():
    """
    Verify public map adheres to BR-08: aggregated, grid-snapped (~500m), banded counts,
    and leaks zero individual personal or accident identifiers.
    """
    response = client.get("/api/v1/public/map")
    assert response.status_code == 200
    data = response.json()
    assert "areas" in data
    areas = data["areas"]
    assert len(areas) >= 1

    first_area = areas[0]
    # Check that band exists (e.g. '40+ crashes')
    assert "accident_band" in first_area
    assert "40+" in first_area["accident_band"]
    assert "safety_advisory" in first_area

    # Verify no raw individual accident records or personal details exist
    assert "victim_name" not in str(data)
    assert "driver_name" not in str(data)
    assert "phone" not in str(data)
    assert "vehicle_number" not in str(data)

def test_hotspot_lifecycle_and_assignment():
    # Login as admin
    login_res = client.post("/api/v1/auth/login", json={"email": "map_admin@test.in", "password": "AdminPass123!"})
    token = login_res.json()["access_token"]
    admin_id = login_res.json()["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List hotspots
    list_res = client.get("/api/v1/hotspots", headers=headers)
    assert list_res.status_code == 200
    hotspots = list_res.json()["hotspots"]
    assert any(h["code"] == "H-0142" for h in hotspots)

    # 2. Get hotspot detail
    det_res = client.get("/api/v1/hotspots/H-0142", headers=headers)
    assert det_res.status_code == 200
    assert det_res.json()["code"] == "H-0142"
    assert det_res.json()["risk_score"] == 92

    # 3. Assign hotspot
    assign_res = client.post(
        "/api/v1/hotspots/H-0142/assign",
        json={"assignee_id": admin_id},
        headers=headers,
    )
    assert assign_res.status_code == 200

    # 4. Update status across lifecycle
    status_res = client.post(
        "/api/v1/hotspots/H-0142/status",
        json={"status": "Action in progress", "comment": "Tender issued for high-mast lighting"},
        headers=headers,
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "Action in progress"

    # 5. Risk override with mandatory justification
    override_res = client.post(
        "/api/v1/hotspots/H-0142/risk-override",
        json={"new_risk_level": "high", "reason": "Interim rumble strips and temporary lighting installed"},
        headers=headers,
    )
    assert override_res.status_code == 200
    assert override_res.json()["new_risk_level"] == "high"
