import os
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.core.db import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.accident import AccidentRecord, ImportBatch, ImportIssue
from app.models.hotspot import (
    Hotspot,
    HotspotFactor,
    Recommendation,
    HotspotComment,
    HotspotIntervention,
    hotspot_accidents
)
from app.models.notification import Notification, NotificationSetting
from app.models.system import Report

CENTER_LAT = float(os.getenv("DEMO_CENTER_LAT", 17.4399))
CENTER_LON = float(os.getenv("DEMO_CENTER_LON", 78.4983))

def seed():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("1. Seeding Demo Users...")
        # Users definition
        users_data = [
            # Admin
            {
                "full_name": "Dr. Kiran Rao",
                "email": "admin@police.gov.in",
                "organisation": "State Transport Department",
                "role": UserRoleEnum.ADMIN,
                "status": UserStatusEnum.ACTIVE
            },
            # Safety Analysts
            {
                "full_name": "Asha Reddy",
                "email": "asha.reddy@police.gov.in",
                "organisation": "Road Safety Analysis Cell",
                "role": UserRoleEnum.SAFETY_ANALYST,
                "status": UserStatusEnum.ACTIVE
            },
            # Police Officers
            {
                "full_name": "Ravi Kumar",
                "email": "ravi.kumar@police.gov.in",
                "organisation": "Hyderabad Traffic Police",
                "role": UserRoleEnum.POLICE_OFFICER,
                "status": UserStatusEnum.ACTIVE
            },
            {
                "full_name": "Imran Sheikh",
                "email": "imran.sheikh@police.gov.in",
                "organisation": "Traffic Police Cyberabad",
                "role": UserRoleEnum.POLICE_OFFICER,
                "status": UserStatusEnum.ACTIVE
            },
            # Authority Officials
            {
                "full_name": "Sana Fatima",
                "email": "sana.fatima@transport.gov.in",
                "organisation": "Roads & Buildings Dept",
                "role": UserRoleEnum.AUTHORITY_OFFICIAL,
                "status": UserStatusEnum.ACTIVE
            },
            {
                "full_name": "Meera Iyer",
                "email": "meera.iyer@transport.gov.in",
                "organisation": "Municipal Corporation (GHMC)",
                "role": UserRoleEnum.AUTHORITY_OFFICIAL,
                "status": UserStatusEnum.ACTIVE
            },
            # Deactivated
            {
                "full_name": "Pooja Nair",
                "email": "pooja.nair@police.gov.in",
                "organisation": "Traffic Safety Cell",
                "role": UserRoleEnum.SAFETY_ANALYST,
                "status": UserStatusEnum.DEACTIVATED
            },
            # Pending Approvals
            {
                "full_name": "Vikram Singh",
                "email": "vikram.singh@police.gov.in",
                "organisation": "Traffic Enforcement Unit",
                "role": UserRoleEnum.POLICE_OFFICER,
                "status": UserStatusEnum.PENDING
            },
            {
                "full_name": "Anjali Verma",
                "email": "anjali.verma@transport.gov.in",
                "organisation": "State Highway Authority",
                "role": UserRoleEnum.AUTHORITY_OFFICIAL,
                "status": UserStatusEnum.PENDING
            },
            {
                "full_name": "Harish Babu",
                "email": "harish.babu@police.gov.in",
                "organisation": "Data Intelligence Division",
                "role": UserRoleEnum.SAFETY_ANALYST,
                "status": UserStatusEnum.PENDING
            }
        ]

        user_map = {}
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user_obj = User(
                    id=str(uuid.uuid4()),
                    full_name=u["full_name"],
                    email=u["email"],
                    organisation=u["organisation"],
                    role=u["role"],
                    password_hash=get_password_hash("Password123!"),
                    status=u["status"]
                )
                db.add(user_obj)
                db.flush()
                user_map[u["full_name"]] = user_obj
            else:
                user_map[u["full_name"]] = existing

        db.commit()

        print("2. Seeding Sample Import Batch (3,214 / 187 / 81 split)...")
        batch = db.query(ImportBatch).filter(ImportBatch.file_name == "Telangana_Crash_Data_2026.csv").first()
        if not batch:
            batch = ImportBatch(
                id=str(uuid.uuid4()),
                file_name="Telangana_Crash_Data_2026.csv",
                object_key="imports/Telangana_Crash_Data_2026.csv",
                uploaded_by=user_map["Asha Reddy"].id,
                template_version="v2",
                total_rows=3482,
                accepted_rows=3214,
                corrected_rows=187,
                rejected_rows=81,
                masked_counts={"vehicle_numbers": 1206, "names": 312, "phone_numbers": 74},
                status="imported"
            )
            db.add(batch)
            db.flush()

            # Seed realistic review issues
            issues_samples = [
                (14, "invalid_coordinate", "latitude", "Latitude 91.2405 is outside valid range (-90 to 90)", "Set to 17.4399 (inferred from landmark)", "fix"),
                (28, "duplicate", "record_id", "Exact duplicate of record ACC-2026-0042 (same vehicle, time and location)", "Drop duplicate row", "skip"),
                (45, "address_only", "longitude", "Missing coordinates; geocoded from 'Opposite Metro Pillar 114'", "Verify landmark location", "accept"),
                (89, "typo", "severity", "Severity value 'Grievious' corrected to standardized 'Grievous injury'", "Corrected to standard value", "fix"),
                (112, "missing_field", "accident_date", "Date field was empty in source row", "Reject row until date verified by field officer", "skip")
            ]
            for row_num, itype, field, msg, fix, act in issues_samples:
                db.add(ImportIssue(
                    batch_id=batch.id,
                    row_number=row_num,
                    issue_type=itype,
                    field=field,
                    message=msg,
                    suggested_fix=fix,
                    action=act,
                    resolved=(act in ["fix", "accept"])
                ))
            db.commit()

        print("3. Seeding Top Reference Hotspots & 47 Total Blackspots...")
        # Check if hotspots already exist
        existing_hotspots = db.query(Hotspot).count()
        if existing_hotspots < 47:
            # Clear existing to enforce exact canonical counts and codes
            db.query(Recommendation).delete()
            db.query(HotspotFactor).delete()
            db.query(HotspotIntervention).delete()
            db.query(HotspotComment).delete()
            db.query(Hotspot).delete()
            db.commit()

            # Top 10 Hard-coded Hotspots from Part H
            top_ten = [
                {
                    "code": "H-0142",
                    "name": "NH-65 × Station Road Junction",
                    "road_name": "NH-65",
                    "area": "Zone 5 (NH-65)",
                    "lat": 17.4399,
                    "lon": 78.4983,
                    "accidents": 41,
                    "deaths": 9,
                    "injured": 63,
                    "score": 92.0,
                    "risk": "critical",
                    "status": "Under review",
                    "assignee": None,
                    "peak_text": "6–9 pm, Fri–Sat",
                    "factors": [
                        ("Two-wheelers turning", 58.0),
                        ("Poor street lighting", 46.0),
                        ("Overspeeding on merge", 34.0),
                        ("Wet road surface", 21.0),
                        ("Missing pedestrian crossing", 18.0)
                    ],
                    "recommendations": [
                        ("Install high-mast LED illumination", "Addresses poor nighttime visibility (46% crashes)", "high"),
                        ("Raised table pedestrian zebra crossing", "Addresses missing pedestrian refuge (18% crashes)", "high"),
                        ("Synchronized traffic signal with turn bay", "Separates two-wheeler turning conflicts (58% crashes)", "high"),
                        ("Speed calming rumble strips (50 km/h)", "Reduces approach overspeeding on downhill merge", "medium")
                    ]
                },
                {
                    "code": "H-0087",
                    "name": "Outer Ring Road, Exit 12",
                    "road_name": "ORR Expressway",
                    "area": "Zone 5 (NH-65)",
                    "lat": 17.4125,
                    "lon": 78.5320,
                    "accidents": 37,
                    "deaths": 7,
                    "injured": 48,
                    "score": 88.0,
                    "risk": "critical",
                    "status": "Assigned",
                    "assignee": user_map.get("Ravi Kumar"),
                    "peak_text": "7–10 pm, Daily",
                    "factors": [
                        ("High speed differential", 52.0),
                        ("Lane indiscipline at off-ramp", 44.0),
                        ("Lack of advance signage", 38.0)
                    ],
                    "recommendations": [
                        ("High-friction anti-skid surfacing", "Installed 14 May 2026", "high"),
                        ("Smart ramp meter signaling", "Installed 14 May 2026", "high")
                    ],
                    "intervention": {
                        "type": "Traffic signal and anti-skid surfacing",
                        "date": datetime(2026, 5, 14, tzinfo=timezone.utc),
                        "pre_accidents": 14,
                        "pre_fatalities": 4,
                        "post_accidents": 9,
                        "post_fatalities": 1,
                        "reduction_pct": 35.7
                    }
                },
                {
                    "code": "H-0103",
                    "name": "Market Road Curve",
                    "road_name": "Market Road",
                    "area": "Central Corridor",
                    "lat": 17.4260,
                    "lon": 78.4750,
                    "accidents": 29,
                    "deaths": 4,
                    "injured": 35,
                    "score": 79.0,
                    "risk": "high",
                    "status": "Action in progress",
                    "assignee": user_map.get("Sana Fatima"),
                    "peak_text": "5–8 pm, Mon–Thu",
                    "factors": [("Sharp curve radius", 61.0), ("Sightline obstruction", 49.0)]
                },
                {
                    "code": "H-0215",
                    "name": "Bypass Road Underpass",
                    "road_name": "Bypass Highway",
                    "area": "Zone 3 (Industrial)",
                    "lat": 17.4680,
                    "lon": 78.4410,
                    "accidents": 26,
                    "deaths": 3,
                    "injured": 31,
                    "score": 74.0,
                    "risk": "high",
                    "status": "Identified",
                    "assignee": None,
                    "peak_text": "9 pm – 12 am, Fri–Sun",
                    "factors": [("Waterlogging in monsoon", 54.0), ("Heavy freight merging", 42.0)]
                },
                {
                    "code": "H-0061",
                    "name": "School Crossing, Ring Road",
                    "road_name": "Ring Road Sector 4",
                    "area": "Central Corridor",
                    "lat": 17.3950,
                    "lon": 78.4890,
                    "accidents": 22,
                    "deaths": 1,
                    "injured": 24,
                    "score": 58.0,
                    "risk": "medium",
                    "status": "Implemented",
                    "assignee": user_map.get("Meera Iyer"),
                    "peak_text": "8–10 am & 3–5 pm",
                    "factors": [("School pedestrian rush", 68.0), ("Inadequate crossing time", 45.0)]
                },
                {
                    "code": "H-0178",
                    "name": "Lake View Roundabout",
                    "road_name": "Lake Promenade Road",
                    "area": "Zone 3 (Industrial)",
                    "lat": 17.4510,
                    "lon": 78.4210,
                    "accidents": 19,
                    "deaths": 1,
                    "injured": 20,
                    "score": 54.0,
                    "risk": "medium",
                    "status": "Under review",
                    "assignee": None,
                    "peak_text": "6–9 pm, Weekends",
                    "factors": [("Circular weave congestion", 44.0)]
                },
                {
                    "code": "H-0039",
                    "name": "Industrial Area Gate 2",
                    "road_name": "Industrial Corridor",
                    "area": "Zone 3 (Industrial)",
                    "lat": 17.4820,
                    "lon": 78.4120,
                    "accidents": 24,
                    "deaths": 2,
                    "injured": 28,
                    "score": 68.0,
                    "risk": "high",
                    "status": "Assigned",
                    "assignee": user_map.get("Imran Sheikh"),
                    "peak_text": "11 pm – 3 am",
                    "factors": [("Truck turning blindspot", 56.0)]
                },
                {
                    "code": "H-0124",
                    "name": "Old Town Bridge Approach",
                    "road_name": "Bridge Road",
                    "area": "Central Corridor",
                    "lat": 17.3820,
                    "lon": 78.4620,
                    "accidents": 18,
                    "deaths": 1,
                    "injured": 19,
                    "score": 51.0,
                    "risk": "medium",
                    "status": "Under review",
                    "assignee": None,
                    "peak_text": "6–8 pm, Daily",
                    "factors": [("Narrow bridge abutment", 50.0)]
                },
                {
                    "code": "H-0196",
                    "name": "Canal Road Bend",
                    "road_name": "Canal Bund Road",
                    "area": "Rural Perimeter",
                    "lat": 17.5120,
                    "lon": 78.5420,
                    "accidents": 14,
                    "deaths": 0,
                    "injured": 12,
                    "score": 42.0,
                    "risk": "low",
                    "status": "Closed",
                    "assignee": user_map.get("Asha Reddy"),
                    "peak_text": "Night",
                    "factors": [("Lack of guardrails", 40.0)]
                },
                {
                    "code": "H-0052",
                    "name": "Railway Station Crossing",
                    "road_name": "Station Approach",
                    "area": "Central Corridor",
                    "lat": 17.4320,
                    "lon": 78.5020,
                    "accidents": 25,
                    "deaths": 3,
                    "injured": 26,
                    "score": 71.0,
                    "risk": "high",
                    "status": "Action in progress",
                    "assignee": user_map.get("Sana Fatima"),
                    "peak_text": "Evening rush",
                    "factors": [("Auto-rickshaw congestion", 62.0)]
                }
            ]

            # Insert top 10
            for item in top_ten:
                h = Hotspot(
                    id=str(uuid.uuid4()),
                    code=item["code"],
                    name=item["name"],
                    road_name=item["road_name"],
                    area=item["area"],
                    lat=item["lat"],
                    lon=item["lon"],
                    accidents_count=item["accidents"],
                    fatalities=item["deaths"],
                    injured=item["injured"],
                    risk_score=item["score"],
                    risk_level=item["risk"],
                    status=item["status"],
                    assignee_id=item["assignee"].id if item.get("assignee") else None,
                    peak_time_text=item.get("peak_text", "6–9 pm"),
                    period_start=datetime(2025, 12, 1, tzinfo=timezone.utc),
                    period_end=datetime(2026, 11, 23, tzinfo=timezone.utc),
                    score_breakdown={
                        "deaths": round(item["deaths"] * 4.5, 1),
                        "frequency": round(item["accidents"] * 0.8, 1),
                        "injuries": round(item["injured"] * 0.3, 1)
                    }
                )
                db.add(h)
                db.flush()

                # Add factors
                for f_name, f_pct in item.get("factors", []):
                    db.add(HotspotFactor(
                        hotspot_id=h.id,
                        factor_key=f_name.lower().replace(" ", "_"),
                        label=f_name,
                        percent=float(f_pct),
                        count=int((f_pct / 100) * item["accidents"])
                    ))

                # Add recommendations
                for r_title, r_desc, r_conf in item.get("recommendations", []):
                    db.add(Recommendation(
                        hotspot_id=h.id,
                        title=r_title,
                        linked_factor="Road Environment & Traffic Flow",
                        evidence_text=r_desc,
                        confidence=r_conf,
                        is_ai_generated=True
                    ))

                # Add intervention if present
                if "intervention" in item:
                    inv = item["intervention"]
                    db.add(HotspotIntervention(
                        hotspot_id=h.id,
                        description=f"{inv['type']} - Pre: {inv['pre_accidents']} crashes, Post: {inv['post_accidents']} crashes (-{inv['reduction_pct']}%)",
                        implemented_on=inv["date"],
                        recorded_by=user_map["Sana Fatima"].id
                    ))

            # Remaining 37 hotspots to reach exact 47 total
            # Target split: Critical 12, High 15, Medium 13, Low 7
            # Top 10 already had: Critical 2, High 4, Medium 3, Low 1.
            # Remaining needed: Critical 10, High 11, Medium 10, Low 6.
            remaining_specs = (
                [("critical", 86.0 + random.uniform(0, 4), "Under review")] * 10 +
                [("high", 72.0 + random.uniform(0, 6), "Action in progress")] * 11 +
                [("medium", 52.0 + random.uniform(0, 6), "Identified")] * 10 +
                [("low", 35.0 + random.uniform(0, 8), "Identified")] * 6
            )

            used_codes = {item["code"] for item in top_ten}
            code_counter = 301

            for idx, (risk_lvl, score, st) in enumerate(remaining_specs, start=11):
                while f"H-{code_counter:04d}" in used_codes:
                    code_counter += 1
                code = f"H-{code_counter:04d}"
                used_codes.add(code)
                code_counter += 1
                lat_jitter = CENTER_LAT + random.uniform(-0.08, 0.08)
                lon_jitter = CENTER_LON + random.uniform(-0.08, 0.08)
                deaths = random.randint(4, 8) if risk_lvl == "critical" else (random.randint(1, 3) if risk_lvl == "high" else (1 if risk_lvl == "medium" else 0))
                accidents = random.randint(30, 40) if risk_lvl == "critical" else random.randint(15, 28)
                injuries = random.randint(accidents, accidents * 2)

                h = Hotspot(
                    id=str(uuid.uuid4()),
                    code=code,
                    name=f"Junction Sector {idx} & NH-65 Spur",
                    road_name=f"Sector Highway {idx}",
                    area="Zone 5 (NH-65)" if idx % 2 == 0 else "Zone 3 (Industrial)",
                    lat=round(lat_jitter, 5),
                    lon=round(lon_jitter, 5),
                    accidents_count=accidents,
                    fatalities=deaths,
                    injured=injuries,
                    risk_score=round(score, 1),
                    risk_level=risk_lvl,
                    status=st,
                    peak_time_text="6–9 pm",
                    period_start=datetime(2025, 12, 1, tzinfo=timezone.utc),
                    period_end=datetime(2026, 11, 23, tzinfo=timezone.utc),
                    score_breakdown={"deaths": deaths * 4.5, "frequency": accidents * 0.8, "injuries": injuries * 0.3}
                )
                db.add(h)
                db.flush()

                db.add(HotspotFactor(
                    hotspot_id=h.id,
                    factor_key="intersection_conflict",
                    label="Intersection conflict",
                    percent=float(random.randint(40, 60)),
                    count=random.randint(8, 20)
                ))
                db.add(Recommendation(
                    hotspot_id=h.id,
                    title="Install solar hazard blinker & warning signs",
                    linked_factor="Intersection conflict",
                    evidence_text="Immediate visual alert for night approaches",
                    confidence="high",
                    is_ai_generated=True
                ))

            db.commit()
            print("Successfully populated all 47 Blackspots!")

        print("4. Seeding 4,812 Synthetic Accidents...")
        current_accidents = db.query(AccidentRecord).count()
        if current_accidents < 4800:
            print(f"Current accidents: {current_accidents}. Generating to reach ~4,812...")
            to_generate = 4812 - current_accidents
            batch_records = []
            start_date = datetime(2025, 12, 1, tzinfo=timezone.utc)

            # Hotspots to center accident clusters around
            hotspot_centers = db.query(Hotspot.lat, Hotspot.lon).all()
            if not hotspot_centers:
                hotspot_centers = [(CENTER_LAT, CENTER_LON)]

            severities = ["fatal", "grievous", "minor", "non_injury"]
            weather_types = ["clear", "rain", "fog", "cloudy"]
            road_types = ["national_highway", "state_highway", "city_road", "junction"]

            for i in range(to_generate):
                acc_code = f"ACC-2026-{current_accidents + i + 1:05d}"
                # Cluster 70% around actual hotspot centers, 30% background
                if random.random() < 0.7:
                    center = random.choice(hotspot_centers)
                    lat = center[0] + random.gauss(0, 0.0015)
                    lon = center[1] + random.gauss(0, 0.0015)
                else:
                    lat = CENTER_LAT + random.uniform(-0.09, 0.09)
                    lon = CENTER_LON + random.uniform(-0.09, 0.09)

                days_offset = random.randint(0, 357)
                # Realistic hour distribution with evening peak (6-9pm)
                if random.random() < 0.45:
                    hour = random.randint(18, 21)
                else:
                    hour = random.randint(0, 23)

                occurred = start_date + timedelta(days=days_offset, hours=hour, minutes=random.randint(0, 59))
                sev = random.choices(severities, weights=[0.08, 0.32, 0.40, 0.20])[0]
                fatalities = random.randint(1, 2) if sev == "fatal" else 0
                injuries = random.randint(1, 3) if sev in ["fatal", "grievous"] else (1 if sev == "minor" else 0)

                rec = AccidentRecord(
                    id=str(uuid.uuid4()),
                    accident_code=acc_code,
                    occurred_at=occurred,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    location_text="NH-65 Corridor Sector, Telangana",
                    geocode_confidence=round(random.uniform(0.85, 1.0), 2),
                    severity=sev,
                    fatalities=fatalities,
                    injuries=injuries,
                    vehicle_types=["two_wheeler", "car"] if random.random() < 0.5 else ["two_wheeler"],
                    weather=random.choice(["Clear", "Rain", "Fog"]),
                    road_type=random.choice(["national_highway", "city_road", "junction"]),
                    light_condition="Dark" if (hour >= 18 or hour <= 5) else "Daylight",
                    probable_cause="Overspeeding" if random.random() < 0.5 else "Junction conflict",
                    source_batch_id=batch.id if batch else None
                )
                batch_records.append(rec)

                if len(batch_records) >= 500:
                    db.bulk_save_objects(batch_records)
                    db.commit()
                    batch_records = []

            if batch_records:
                db.bulk_save_objects(batch_records)
                db.commit()
            print("Successfully populated 4,812 accident records!")

        print("5. Seeding Notifications...")
        for u in user_map.values():
            if not db.query(Notification).filter(Notification.user_id == u.id).first():
                db.add_all([
                    Notification(
                        user_id=u.id,
                        type="critical_detected",
                        title="New Critical Hotspot detected: H-0142",
                        body="NH-65 × Station Road Junction reached risk score 92 with 9 fatalities.",
                        entity_id="H-0142",
                        is_read=False
                    ),
                    Notification(
                        user_id=u.id,
                        type="assigned",
                        title="Hotspot H-0087 assigned for review",
                        body="Outer Ring Road, Exit 12 has been assigned for engineering review.",
                        entity_id="H-0087",
                        is_read=False
                    )
                ])
                db.add(NotificationSetting(user_id=u.id))
        db.commit()

        print("6. Creating Test CSV with seeded issues in docs/...")
        os.makedirs("docs", exist_ok=True)
        issue_csv_path = os.path.join("docs", "accident_test_dataset_with_issues.csv")
        with open(issue_csv_path, "w", encoding="utf-8") as f:
            f.write("record_id,occurred_at,latitude,longitude,location_name,severity,fatalities,injuries,vehicle_number,driver_name,driver_phone,weather,road_type\n")
            # Row 1: Valid
            f.write("ACC-TEST-001,2026-03-10 18:30:00,17.4399,78.4983,Station Rd Junction,Fatal,1,2,TS09EA1234,Ramesh Chandra,9876543210,Clear,National Highway\n")
            # Row 2: Duplicate
            f.write("ACC-TEST-001,2026-03-10 18:30:00,17.4399,78.4983,Station Rd Junction,Fatal,1,2,TS09EA1234,Ramesh Chandra,9876543210,Clear,National Highway\n")
            # Row 3: Invalid coordinates (Lat 95)
            f.write("ACC-TEST-002,2026-03-11 20:15:00,95.1234,78.4890,Market Cross,Grievous injury,0,3,AP28Z9999,Sunil Verma,9848022338,Rain,City Road\n")
            # Row 4: Typo in severity
            f.write("ACC-TEST-003,2026-03-12 14:00:00,17.4125,78.5320,ORR Exit 12,Grievious,0,1,DL1CAB1234,John Doe,9988776655,Clear,Expressway\n")
            # Row 5: Address only (coordinates missing)
            f.write("ACC-TEST-004,2026-03-13 19:45:00,,,Near Metro Pillar 114,Minor injury,0,1,TS07AB4321,Praveen Kumar,9123456780,Fog,City Road\n")
        print(f"Generated test dataset with issues: {issue_csv_path}")

        print("\nAll demo data seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
