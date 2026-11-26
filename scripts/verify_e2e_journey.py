import os
import sys
import time
import requests

API_BASE = "http://127.0.0.1:8000/api/v1"

def run_e2e_journey():
    print("=" * 65)
    print("STARTING END-TO-END INTEGRATION JOURNEY AUDIT (STEP 5)")
    print("=" * 65)
    results = {}

    # Journey Step 1: Public Viewer Journey
    print("\n[Journey 1: Public Viewer - Landing & Aggregated Map]")
    r_pub_map = requests.get(f"{API_BASE}/public/map")
    assert r_pub_map.status_code == 200, f"Public map failed: {r_pub_map.status_code}"
    pub_data = r_pub_map.json()
    assert "areas" in pub_data and len(pub_data["areas"]) > 0
    # Assert anonymity
    str_pub = str(pub_data)
    assert "TS09" not in str_pub and "Ramesh" not in str_pub and "9876" not in str_pub
    print(f"PASS: Public map returned {len(pub_data['areas'])} anonymized zones with zero PII")
    results["public_viewer"] = "PASS"

    # Journey Step 2 & 3: Officer Sign Up, Pending Gate, and Admin Approval Flow
    print("\n[Journey 2: Sign Up -> Pending Block -> Admin Approval]")
    unique_email = f"e2e.officer.{int(time.time())}@police.gov.in"
    r_reg = requests.post(f"{API_BASE}/auth/register", json={
        "full_name": "Inspector Vikram Goud",
        "email": unique_email,
        "organisation": "Traffic Enforcement Cyberabad",
        "role": "police_officer",
        "password": "Password123!"
    })
    assert r_reg.status_code in [200, 201], f"Register failed: {r_reg.text}"
    user_id = r_reg.json().get("id")
    print(f"PASS: Officer signed up successfully (ID: {user_id})")

    # Pending officer login attempt must be rejected
    r_login_pen = requests.post(f"{API_BASE}/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    assert r_login_pen.status_code == 403
    assert "waiting for approval" in r_login_pen.json().get("detail", "")
    print(f"PASS: Pending officer blocked with 403: {r_login_pen.json().get('detail')}")

    # Admin login & approval
    r_admin_login = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@police.gov.in",
        "password": "Password123!"
    })
    assert r_admin_login.status_code == 200
    admin_token = r_admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Admin approves officer
    r_approve = requests.post(f"{API_BASE}/users/{user_id}/approve", headers=admin_headers)
    assert r_approve.status_code == 200, f"Approval failed: {r_approve.text}"
    print("PASS: Admin approved officer account")

    # Now officer can log in!
    r_officer_login = requests.post(f"{API_BASE}/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    assert r_officer_login.status_code == 200, f"Officer login failed: {r_officer_login.text}"
    officer_token = r_officer_login.json()["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    print("PASS: Approved officer successfully logged in")
    results["auth_and_approval_flow"] = "PASS"

    # Journey Step 4: Officer Views Dashboard
    print("\n[Journey 3: Dashboard Metrics Verification]")
    r_dash = requests.get(f"{API_BASE}/dashboard/summary", headers=officer_headers)
    assert r_dash.status_code == 200
    dash_data = r_dash.json()
    acc_val = dash_data.get("accidents", {}).get("value")
    fat_val = dash_data.get("fatalities", {}).get("value")
    inj_val = dash_data.get("injured", {}).get("value")
    hot_val = dash_data.get("hotspots", {}).get("value")
    crit_val = dash_data.get("hotspots", {}).get("critical_count")
    print(f"Dashboard Metrics: Accidents={acc_val}, Fatalities={fat_val}, Injured={inj_val}, Hotspots={hot_val} (Critical: {crit_val})")
    assert 4812 <= acc_val <= 4820
    assert fat_val == 389
    assert 5274 <= inj_val <= 5280
    assert hot_val == 47
    print("PASS: Dashboard metrics match target expectations (around 4,812 / 389 / 5,274 / 47)")
    results["dashboard_consistency"] = "PASS"

    # Journey Step 5: Data Import & Validation
    print("\n[Journey 4: Data Import & Validation Pipeline]")
    # Safety Analyst logs in for import
    r_analyst_login = requests.post(f"{API_BASE}/auth/login", json={
        "email": "asha.reddy@police.gov.in",
        "password": "Password123!"
    })
    analyst_token = r_analyst_login.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    test_csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "accident_test_dataset_with_issues.csv")
    with open(test_csv_path, "rb") as f:
        r_upload = requests.post(f"{API_BASE}/imports", files={"file": ("accident_test_dataset_with_issues.csv", f, "text/csv")}, headers=analyst_headers)
    assert r_upload.status_code in [200, 201], f"Upload failed: {r_upload.text}"
    import_batch = r_upload.json()
    batch_id = import_batch["id"]
    print(f"PASS: Uploaded import batch {batch_id}: Total Rows={import_batch.get('total_rows')}")

    # Inspect detected issues
    r_issues = requests.get(f"{API_BASE}/imports/{batch_id}/issues", headers=analyst_headers)
    assert r_issues.status_code == 200
    issues_list = r_issues.json()
    print(f"PASS: Import validation identified {len(issues_list)} issues with suggestions")
    results["import_pipeline"] = "PASS"

    # Journey Step 6 & 7: Hotspot Map & Dossier Inspection (H-0142)
    print("\n[Journey 5: Hotspot Map & H-0142 Dossier Inspection]")
    r_h142 = requests.get(f"{API_BASE}/hotspots/H-0142", headers=officer_headers)
    assert r_h142.status_code == 200
    h142_data = r_h142.json()
    print(f"H-0142 Dossier: {h142_data['name']}, Score={h142_data['risk_score']}, Risk={h142_data['risk_level']}, Status={h142_data['status']}")
    assert h142_data["code"] == "H-0142"
    assert h142_data["risk_score"] == 92.0
    assert h142_data["fatalities"] == 9
    assert h142_data["injured"] == 63
    assert h142_data["accidents_count"] == 41
    print("PASS: H-0142 Dossier data integrity verified")
    results["hotspot_inspection"] = "PASS"

    # Journey Step 8: Assignment to Officer & Notification
    print("\n[Journey 6: Case Assignment & Push Notification]")
    r_assign = requests.post(f"{API_BASE}/hotspots/H-0142/assign", headers=admin_headers, json={
        "assignee_id": user_id
    })
    assert r_assign.status_code == 200, f"Assignment failed: {r_assign.text}"
    print(f"PASS: H-0142 assigned to Inspector Vikram Goud")

    # Check notification for newly assigned officer
    r_notifs = requests.get(f"{API_BASE}/notifications", headers=officer_headers)
    print(f"Notifications response status: {r_notifs.status_code}, content: {r_notifs.text}")
    assert r_notifs.status_code == 200, f"Notifications failed with {r_notifs.status_code}: {r_notifs.text}"
    notifs_data = r_notifs.json()
    all_notifs = notifs_data.get("today", []) + notifs_data.get("earlier", [])
    print(f"Officer notifications total: {len(all_notifs)}, Unread: {notifs_data.get('unread_count')}")
    assert len(all_notifs) > 0
    assigned_notif = next((n for n in all_notifs if "H-0142" in n.get("title", "") or "H-0142" in n.get("body", "") or n.get("entity_id") == h142_data["id"] or n.get("type") == "assigned"), None)
    assert assigned_notif is not None, "Notification not delivered to assignee"
    print(f"PASS: Notification received by officer: '{assigned_notif['title']}'")
    results["assignment_and_notifications"] = "PASS"

    # Journey Step 9: Lifecycle State Transition
    print("\n[Journey 7: Lifecycle State Transition & Audit Trail]")
    r_status = requests.post(f"{API_BASE}/hotspots/H-0142/status", headers=officer_headers, json={
        "status": "Action in progress",
        "comment": "Initiated junction speed calming review and luminaire deployment with GHMC team."
    })
    assert r_status.status_code == 200
    print("PASS: H-0142 transitioned to 'Action in progress'")
    results["lifecycle_transition"] = "PASS"

    # Journey Step 10: Reports Generation & Download
    print("\n[Journey 8: Reports Generation & Export]")
    r_rep_gen = requests.post(f"{API_BASE}/reports", headers=officer_headers, json={
        "title": "E2E Demo Executive Safety Briefing",
        "type": "summary",
        "format": "pdf",
        "period": "Dec 2025 – Nov 2026"
    })
    assert r_rep_gen.status_code == 200
    rep_id = r_rep_gen.json()["id"]

    r_dl = requests.get(f"{API_BASE}/reports/{rep_id}/download", headers=officer_headers)
    assert r_dl.status_code == 200
    assert len(r_dl.content) > 1000
    assert "pdf" in r_dl.headers.get("content-type", "").lower()
    print(f"PASS: Executive PDF report downloaded successfully ({len(r_dl.content)} bytes)")
    results["reporting_export"] = "PASS"

    # Journey Step 11: AI Assistant Query
    print("\n[Journey 9: Grounded AI Safety Assistant Query]")
    r_ai = requests.post(f"{API_BASE}/assistant/chat", headers=officer_headers, json={
        "message": "What is the top contributing factor at H-0142?"
    })
    assert r_ai.status_code == 200
    ai_resp = r_ai.json()
    ai_answer = ai_resp.get("answer", ai_resp.get("reply", ""))
    print(f"AI Answer Preview:\n{ai_answer[:180]}...")
    assert "two-wheeler" in ai_answer.lower() or "58" in ai_answer or "H-0142" in ai_answer
    assert ai_resp.get("caveats") or "AI-generated" in str(ai_resp) or "expert review" in str(ai_resp)
    print("PASS: AI Assistant responded with grounded data, cited H-0142, and included disclaimer")
    results["ai_assistant"] = "PASS"

    # Journey Step 12: Cross-system Consistency Audit
    print("\n[Journey 10: Cross-system Consistency Audit]")
    # 1. Dashboard vs Hotspots List count
    r_cases = requests.get(f"{API_BASE}/hotspots", headers=officer_headers)
    assert r_cases.status_code == 200
    cases_data = r_cases.json()
    assert cases_data["total"] == 47
    print(f"PASS: Hotspots Cases list total ({cases_data['total']}) == Dashboard Blackspots count (47)")

    # 2. Map Hotspots GeoJSON count
    r_map_pts = requests.get(f"{API_BASE}/map/hotspots", headers=officer_headers)
    assert r_map_pts.status_code == 200
    map_features = r_map_pts.json()["features"]
    assert len(map_features) == 47
    print(f"PASS: Interactive Map Hotspot markers ({len(map_features)}) == Cases total (47)")

    results["cross_system_consistency"] = "PASS"

    print("\n" + "=" * 65)
    print("END-TO-END INTEGRATION AUDIT SUMMARY:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 65)
    return results

if __name__ == "__main__":
    run_e2e_journey()
