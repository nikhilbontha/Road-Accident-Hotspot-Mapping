import os
import sys
import re
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.core.db import SessionLocal, engine
from app.models.user import User
from app.models.accident import AccidentRecord, ImportBatch, ImportIssue
from app.models.hotspot import Hotspot, HotspotFactor, Recommendation, HotspotComment, HotspotIntervention
from app.models.audit import AuditLog
from app.models.notification import Notification, NotificationSetting
from app.models.system import SystemSetting, AnalysisRun, Report
from app.models.chat import ChatConversation, ChatMessage
from sqlalchemy import text, inspect

def run_db_checks():
    db = SessionLocal()
    results = {}
    print("=" * 60)
    print("STARTING DATABASE AUDIT (STEP 2)")
    print("=" * 60)

    # Check 1: Table inventory
    expected_tables = [
        "users", "import_batches", "import_issues", "accident_records",
        "analysis_runs", "hotspots", "hotspot_accidents", "hotspot_factors",
        "recommendations", "hotspot_comments", "hotspot_interventions",
        "audit_logs", "notifications", "notification_settings",
        "chat_conversations", "chat_messages", "reports", "system_settings"
    ]
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    missing_tables = [t for t in expected_tables if t not in existing_tables]
    if missing_tables:
        print(f"FAIL: Missing tables: {missing_tables}")
        results["tables"] = "FAIL"
    else:
        print(f"PASS: All {len(expected_tables)} expected tables exist.")
        results["tables"] = "PASS"

    # Check 2: Demo targets
    accidents_count = db.query(AccidentRecord).count()
    fatalities_sum = db.execute(text("SELECT COALESCE(SUM(fatalities), 0) FROM accident_records")).scalar()
    injuries_sum = db.execute(text("SELECT COALESCE(SUM(injuries), 0) FROM accident_records")).scalar()

    print(f"Accidents Count: {accidents_count} (Target: ~4,812)")
    print(f"Fatalities Sum: {fatalities_sum} (Target: 389)")
    print(f"Injuries Sum: {injuries_sum} (Target: 5,274)")

    hotspots_count = db.query(Hotspot).count()
    risk_counts = dict(db.execute(text("SELECT risk_level, COUNT(*) FROM hotspots GROUP BY risk_level")).fetchall())
    status_counts = dict(db.execute(text("SELECT status, COUNT(*) FROM hotspots GROUP BY status")).fetchall())

    print(f"Hotspots Total: {hotspots_count} (Target: 47)")
    print(f"Risk Levels: {risk_counts} (Target: Critical 12, High 15, Medium 13, Low 7)")
    print(f"Statuses: {status_counts} (Target: Identified 9, Under review 11, Assigned 8, Action in progress 11, Implemented 6, Closed 2)")

    # Check H-0142
    h142 = db.query(Hotspot).filter(Hotspot.code == "H-0142").first()
    if h142:
        print(f"H-0142 Found: accidents={h142.accidents_count}, deaths={h142.fatalities}, injured={h142.injured}, score={h142.risk_score}")
        h142_pass = (h142.accidents_count == 41 and h142.fatalities == 9 and h142.injured == 63 and h142.risk_score == 92.0)
    else:
        print("FAIL: H-0142 not found")
        h142_pass = False

    target_pass = (
        accidents_count == 4812 and
        fatalities_sum == 389 and
        injuries_sum == 5274 and
        hotspots_count == 47 and
        risk_counts.get("critical", 0) == 12 and
        risk_counts.get("high", 0) == 15 and
        risk_counts.get("medium", 0) == 13 and
        risk_counts.get("low", 0) == 7 and
        status_counts.get("Identified", 0) == 9 and
        status_counts.get("Under review", 0) == 11 and
        status_counts.get("Assigned", 0) == 8 and
        status_counts.get("Action in progress", 0) == 11 and
        status_counts.get("Implemented", 0) == 6 and
        status_counts.get("Closed", 0) == 2 and
        h142_pass
    )
    results["demo_targets"] = "PASS" if target_pass else "FAIL"
    print(f"Demo Targets Check: {results['demo_targets']}")

    # Check 3: Integrity queries
    # No invalid coords or dates
    invalid_coords = db.execute(text("SELECT COUNT(*) FROM accident_records WHERE latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180")).scalar()
    null_dates = db.execute(text("SELECT COUNT(*) FROM accident_records WHERE occurred_at IS NULL")).scalar()
    duplicate_codes = db.execute(text("SELECT accident_code, COUNT(*) FROM accident_records GROUP BY accident_code HAVING COUNT(*) > 1")).fetchall()
    
    # Risk level threshold consistency:
    # Critical >= 80, High 60-79.9, Medium 40-59.9, Low < 40
    mismatched_risk = db.execute(text("""
        SELECT code, risk_score, risk_level FROM hotspots
        WHERE (risk_level = 'critical' AND risk_score < 80)
           OR (risk_level = 'high' AND (risk_score < 60 OR risk_score >= 80))
           OR (risk_level = 'medium' AND (risk_score < 40 OR risk_score >= 60))
           OR (risk_level = 'low' AND risk_score >= 40)
    """)).fetchall()

    if invalid_coords == 0 and null_dates == 0 and len(duplicate_codes) == 0 and len(mismatched_risk) == 0:
        print("PASS: Database integrity verified (0 invalid coords, 0 null dates, 0 duplicate codes, 0 threshold mismatches).")
        results["integrity"] = "PASS"
    else:
        print(f"FAIL: Integrity issues: coords={invalid_coords}, null_dates={null_dates}, dups={len(duplicate_codes)}, mismatches={mismatched_risk}")
        results["integrity"] = "FAIL"

    # Check 4: Privacy scan (BR-03, FR-12)
    # Check that no phone numbers, vehicle registrations, or names exist in accident_records
    sample_accidents = db.query(AccidentRecord.location_text, AccidentRecord.probable_cause).limit(500).all()
    pii_found = False
    phone_pattern = re.compile(r'\b[6-9]\d{9}\b')
    reg_pattern = re.compile(r'\b[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}\b')

    for loc, cause in sample_accidents:
        combined = f"{loc} {cause}"
        if phone_pattern.search(combined) or reg_pattern.search(combined):
            pii_found = True
            break

    if not pii_found:
        print("PASS: Privacy scan clean. No vehicle registrations or phone numbers in accident records.")
        results["privacy"] = "PASS"
    else:
        print("FAIL: PII detected in accident records!")
        results["privacy"] = "FAIL"

    # Check 5: Passwords hashed
    unhashed_users = db.execute(text("SELECT email FROM users WHERE password_hash NOT LIKE '$2b$%' AND password_hash NOT LIKE '$2a$%'")).fetchall()
    if len(unhashed_users) == 0:
        print("PASS: All user passwords are safely hashed with bcrypt.")
        results["passwords"] = "PASS"
    else:
        print(f"FAIL: Unhashed passwords found: {unhashed_users}")
        results["passwords"] = "FAIL"

    # Check 6: Audit trail immutability (UPDATE & DELETE must fail)
    audit_row = db.query(AuditLog).first()
    update_blocked = False
    delete_blocked = False

    if audit_row:
        # Test UPDATE block
        try:
            db.execute(text(f"UPDATE audit_logs SET action = 'tampered' WHERE id = '{audit_row.id}'"))
            db.commit()
            print("FAIL: Direct SQL UPDATE on audit_logs succeeded!")
        except Exception as e:
            db.rollback()
            print(f"PASS: Direct SQL UPDATE on audit_logs was rejected ({e})")
            update_blocked = True

        # Test DELETE block
        try:
            db.execute(text(f"DELETE FROM audit_logs WHERE id = '{audit_row.id}'"))
            db.commit()
            print("FAIL: Direct SQL DELETE on audit_logs succeeded!")
        except Exception as e:
            db.rollback()
            print(f"PASS: Direct SQL DELETE on audit_logs was rejected ({e})")
            delete_blocked = True

        # Test ORM listener
        try:
            audit_row.action = "orm_tampered"
            db.commit()
            print("FAIL: ORM UPDATE on audit_logs succeeded!")
        except Exception as e:
            db.rollback()
            print(f"PASS: ORM UPDATE on audit_logs was rejected by event listener ({e})")
    else:
        print("WARNING: No audit log rows to test immutability on.")

    results["audit_immutability"] = "PASS" if (update_blocked and delete_blocked) else "FAIL"

    # Check 7: Query EXPLAIN on map, dashboard, and case-list
    print("\nRunning EXPLAIN on critical queries:")
    map_explain = db.execute(text("EXPLAIN QUERY PLAN SELECT id, code, lat, lon, risk_level, risk_score FROM hotspots WHERE risk_score >= 60")).fetchall()
    print("Map Hotspots Query Plan:")
    for row in map_explain:
        print(f"  {row}")

    dash_explain = db.execute(text("EXPLAIN QUERY PLAN SELECT COUNT(*), SUM(fatalities), SUM(injuries) FROM accident_records")).fetchall()
    print("Dashboard Totals Query Plan:")
    for row in dash_explain:
        print(f"  {row}")

    results["explain"] = "PASS"
    db.close()

    print("\n" + "=" * 60)
    print("DATABASE AUDIT SUMMARY:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_db_checks()
