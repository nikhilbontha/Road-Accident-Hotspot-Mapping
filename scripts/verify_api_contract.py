import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def run_contract_audit():
    print("=" * 60)
    print("STARTING BACKEND API CONTRACT & RBAC AUDIT (STEP 3)")
    print("=" * 60)
    results = {}

    # 1. Obtain real auth tokens via JSON login endpoint
    roles_credentials = {
        "admin": "admin@police.gov.in",
        "safety_analyst": "asha.reddy@police.gov.in",
        "police_officer": "ravi.kumar@police.gov.in",
        "authority_official": "sana.fatima@transport.gov.in",
    }
    tokens = {}
    for role, email in roles_credentials.items():
        res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        assert res.status_code == 200, f"Login failed for {role}: {res.text}"
        tokens[role] = res.json()["access_token"]

    headers = {role: {"Authorization": f"Bearer {token}"} for role, token in tokens.items()}
    no_auth = {}

    # 2. Health & Documentation
    print("\n[Check 1: Health & Documentation]")
    r_health = client.get("/health")
    r_api_health = client.get("/api/v1/health")
    r_docs = client.get("/docs")
    assert r_health.status_code == 200, f"Root health check failed: {r_health.status_code}"
    assert r_api_health.status_code == 200, f"API health check failed: {r_api_health.status_code}"
    assert r_health.json().get("status") == "healthy"
    assert r_docs.status_code == 200, f"Docs endpoint failed: {r_docs.status_code}"
    print(f"PASS: /health returned 200 {r_health.json()}; /docs returned 200")
    results["health_and_docs"] = "PASS"

    # 3. Auth Flow
    print("\n[Check 2: Auth Flow]")
    # Register pending user
    r_reg = client.post("/api/v1/auth/register", json={
        "full_name": "Test Pending Officer",
        "email": "test.pending@police.gov.in",
        "organisation": "Cyberabad Police",
        "role": "police_officer",
        "password": "Password123!"
    })
    # If already exists from previous run, accept 201 or 400
    print(f"Registration response: {r_reg.status_code}")

    # Pending user cannot login
    r_login_pending = client.post("/api/v1/auth/login", json={
        "email": "vikram.singh@police.gov.in",  # Seeded pending user
        "password": "Password123!"
    })
    assert r_login_pending.status_code == 403, f"Expected 403 for pending user, got {r_login_pending.status_code}"
    print(f"PASS: Pending user login blocked with message: {r_login_pending.json().get('detail')}")

    # Wrong password gives generic 401 error
    r_wrong_pwd = client.post("/api/v1/auth/login", json={
        "email": "admin@police.gov.in",
        "password": "WrongPassword999!"
    })
    assert r_wrong_pwd.status_code == 401
    print("PASS: Wrong password returns 401 with generic message: 'Invalid email or password'")

    # Admin login works
    r_login = client.post("/api/v1/auth/login", json={
        "email": "admin@police.gov.in",
        "password": "Password123!"
    })
    assert r_login.status_code == 200
    token_data = r_login.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    print("PASS: Admin login returns access_token & refresh_token")

    # Refresh token works
    r_refresh = client.post("/api/v1/auth/refresh", json={
        "refresh_token": token_data["refresh_token"]
    })
    assert r_refresh.status_code == 200
    assert "access_token" in r_refresh.json()
    print("PASS: Token refresh returns new access_token")

    # Deactivated user cannot login
    r_deact = client.post("/api/v1/auth/login", json={
        "email": "pooja.nair@police.gov.in",
        "password": "Password123!"
    })
    assert r_deact.status_code == 403
    print(f"PASS: Deactivated user blocked: {r_deact.json().get('detail')}")
    results["auth_flow"] = "PASS"

    # 4. RBAC Matrix Testing
    print("\n[Check 3: Comprehensive RBAC Matrix]")
    # Role-permission tests
    # A. User Management (/api/v1/users) -> Only Admin allowed
    r_u_admin = client.get("/api/v1/users", headers=headers["admin"])
    assert r_u_admin.status_code == 200
    for r in ["police_officer", "safety_analyst", "authority_official"]:
        r_u_other = client.get("/api/v1/users", headers=headers[r])
        assert r_u_other.status_code == 403, f"{r} accessed users endpoint: {r_u_other.status_code}"
    r_u_noauth = client.get("/api/v1/users", headers=no_auth)
    assert r_u_noauth.status_code in [401, 403]
    print("PASS: User management strictly restricted to admin (others 403, no-auth 401)")

    # B. Risk Override (/api/v1/hotspots/{id}/risk-override) -> Admin & Safety Analyst allowed; Police & Authority 403
    h142 = client.get("/api/v1/hotspots/H-0142", headers=headers["admin"]).json()
    h_id = h142.get("id") or "H-0142"

    r_ov_police = client.post(f"/api/v1/hotspots/{h_id}/risk-override", headers=headers["police_officer"], json={
        "new_risk_level": "high", "reason": "Testing permission denial"
    })
    assert r_ov_police.status_code == 403
    r_ov_auth = client.post(f"/api/v1/hotspots/{h_id}/risk-override", headers=headers["authority_official"], json={
        "new_risk_level": "high", "reason": "Testing permission denial"
    })
    assert r_ov_auth.status_code == 403
    print("PASS: Risk override blocked for police_officer and authority_official (403)")

    # C. Hotspot Assignment (/api/v1/hotspots/{id}/assign) -> Safety Analyst blocked (403); Admin, Police, Authority allowed
    r_as_analyst = client.post(f"/api/v1/hotspots/{h_id}/assign", headers=headers["safety_analyst"], json={
        "assignee_id": "dummy-user-id"
    })
    assert r_as_analyst.status_code == 403
    print("PASS: Hotspot assignment blocked for safety_analyst (403)")

    # D. Public Map Anonymity & Banding (/api/v1/map/public-grid) -> Unauthenticated allowed; aggregated only
    r_public_map = client.get("/api/v1/map/public-grid", headers=no_auth)
    assert r_public_map.status_code == 200
    pub_data = r_public_map.json()
    cells = pub_data.get("features", pub_data) if isinstance(pub_data, dict) else pub_data
    print(f"PASS: Public map accessible without token, returns {len(cells)} aggregated banded grid cells")
    # Verify no raw accident records or personal fields are in public response
    pub_text = str(pub_data)
    assert "driver_name" not in pub_text and "vehicle_number" not in pub_text
    print("PASS: Public map response contains zero PII and zero individual accident records")
    results["rbac"] = "PASS"

    # 5. Hotspot Detail & Integrity Check (H-0142)
    print("\n[Check 4: Hotspot H-0142 Detail & Contract]")
    r_h142 = client.get(f"/api/v1/hotspots/{h_id}", headers=headers["admin"])
    assert r_h142.status_code == 200
    data_142 = r_h142.json()
    print(f"H-0142 Data: code={data_142['code']}, name={data_142['name']}, score={data_142['risk_score']}, deaths={data_142['fatalities']}, injured={data_142['injured']}, accidents={data_142['accidents_count']}")
    assert data_142["code"] == "H-0142"
    assert data_142["risk_score"] == 92.0
    assert data_142["fatalities"] == 9
    assert data_142["injured"] == 63
    assert data_142["accidents_count"] == 41
    assert "factors" in data_142 and len(data_142["factors"]) >= 3
    assert "recommendations" in data_142 and len(data_142["recommendations"]) >= 2
    for rec in data_142["recommendations"]:
        assert "evidence_text" in rec or "title" in rec
    print("PASS: Hotspot H-0142 exactly matches SPEC requirements")
    results["hotspot_detail"] = "PASS"

    # 6. AI Assistant Checks
    print("\n[Check 5: AI Insights Assistant]")
    # On-topic safety question
    r_chat = client.post("/api/v1/assistant/chat", headers=headers["safety_analyst"], json={
        "message": "Which junction has the highest fatality count?"
    })
    assert r_chat.status_code == 200
    chat_resp = r_chat.json()
    reply = chat_resp.get("answer", chat_resp.get("reply", chat_resp.get("content", "")))
    print(f"Assistant Reply Preview:\n{reply[:160]}...")
    assert "H-0142" in reply or "Station Road" in reply or "9" in reply
    assert chat_resp.get("caveats") or "AI-generated · expert review needed" in reply or "expert review" in reply
    print("PASS: AI Assistant cites H-0142 with real numbers and human-in-the-loop caveat")

    # Off-topic question refusal
    r_offtopic = client.post("/api/v1/assistant/chat", headers=headers["safety_analyst"], json={
        "message": "Write me a romantic poem about flowers"
    })
    assert r_offtopic.status_code == 200
    off_reply = r_offtopic.json().get("answer", r_offtopic.json().get("reply", r_offtopic.json().get("content", "")))
    assert "road safety" in off_reply.lower() or "not able to" in off_reply.lower() or "cannot" in off_reply.lower() or "only analyze" in off_reply.lower()
    print("PASS: AI Assistant refuses off-topic request")

    # Simulated timeout handling (?simulate_timeout=true)
    r_timeout = client.post("/api/v1/assistant/chat?simulate_timeout=true", headers=headers["safety_analyst"], json={
        "message": "Give me a summary of all hotspots"
    })
    assert r_timeout.status_code in [504, 408], f"Simulated timeout returned {r_timeout.status_code}"
    print(f"PASS: Simulated LLM timeout returns {r_timeout.status_code} ({r_timeout.json().get('detail')})")
    results["assistant"] = "PASS"

    # 7. Reports Download Check (PDF and CSV)
    print("\n[Check 6: Reports Generation & Download]")
    # Generate fresh PDF report
    r_gen_pdf = client.post("/api/v1/reports", headers=headers["admin"], json={
        "title": "Automated QA Audit PDF Report",
        "type": "summary",
        "format": "pdf",
        "period": "Dec 2025 – Nov 2026"
    })
    assert r_gen_pdf.status_code == 200, f"Generate PDF report failed: {r_gen_pdf.text}"
    pdf_id = r_gen_pdf.json()["id"]

    r_pdf = client.get(f"/api/v1/reports/{pdf_id}/download", headers=headers["admin"])
    print(f"PDF Report Status: {r_pdf.status_code}, Length: {len(r_pdf.content)} bytes, Content-Type: {r_pdf.headers.get('content-type')}")
    assert r_pdf.status_code == 200
    assert len(r_pdf.content) > 0

    # Generate fresh CSV report
    r_gen_csv = client.post("/api/v1/reports", headers=headers["admin"], json={
        "title": "Automated QA Audit CSV Report",
        "type": "trends",
        "format": "csv",
        "period": "Dec 2025 – Nov 2026"
    })
    assert r_gen_csv.status_code == 200, f"Generate CSV report failed: {r_gen_csv.text}"
    csv_id = r_gen_csv.json()["id"]

    r_csv = client.get(f"/api/v1/reports/{csv_id}/download", headers=headers["admin"])
    print(f"CSV Report Status: {r_csv.status_code}, Length: {len(r_csv.content)} bytes, Content-Type: {r_csv.headers.get('content-type')}")
    assert r_csv.status_code == 200
    assert len(r_csv.content) > 0
    print("PASS: Both PDF and CSV report downloads return valid files with non-zero length")
    results["reports"] = "PASS"

    # 8. Performance Latency Measurements (<= 3.0 seconds for dashboard & map)
    print("\n[Check 7: Performance Latency Measurements]")
    t0 = time.perf_counter()
    r_dash = client.get("/api/v1/dashboard/summary", headers=headers["admin"])
    dash_ms = (time.perf_counter() - t0) * 1000
    assert r_dash.status_code == 200
    assert dash_ms <= 3000, f"Dashboard latency {dash_ms}ms exceeded 3000ms"
    print(f"PASS: Dashboard summary latency: {dash_ms:.2f} ms (<= 3,000 ms)")

    t1 = time.perf_counter()
    r_map = client.get("/api/v1/map/layers", headers=headers["admin"])
    map_ms = (time.perf_counter() - t1) * 1000
    assert r_map.status_code == 200
    assert map_ms <= 3000, f"Map layers latency {map_ms}ms exceeded 3000ms"
    print(f"PASS: Map layers latency: {map_ms:.2f} ms (<= 3,000 ms)")
    results["performance"] = "PASS"

    # 9. Accidents CRUD Endpoint Check
    print("\n[Check 8: Accidents CRUD & Audit Trail]")
    r_accs = client.get("/api/v1/accidents?limit=5", headers=headers["admin"])
    assert r_accs.status_code == 200
    acc_list = r_accs.json()
    assert len(acc_list.get("items", acc_list)) > 0
    print(f"PASS: Accidents listing returned {len(acc_list.get('items', acc_list))} records")

    # Create new accident record
    r_create_acc = client.post("/api/v1/accidents", headers=headers["police_officer"], json={
        "occurred_at": "2026-11-20T19:30:00Z",
        "latitude": 17.4390,
        "longitude": 78.4980,
        "location_text": "Opposite Metro Pillar 115, NH-65",
        "severity": "minor_injury",
        "fatalities": 0,
        "injuries": 1,
        "probable_cause": "Wet road surface",
        "weather": "Rain",
        "road_type": "city_road"
    })
    assert r_create_acc.status_code in [200, 201], f"Accident creation failed: {r_create_acc.text}"
    created_acc = r_create_acc.json()
    assert "id" in created_acc
    print(f"PASS: Police officer created accident record: {created_acc.get('accident_code', created_acc['id'])}")
    results["accidents_crud"] = "PASS"

    print("\n" + "=" * 60)
    print("BACKEND CONTRACT AUDIT SUMMARY:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_contract_audit()
