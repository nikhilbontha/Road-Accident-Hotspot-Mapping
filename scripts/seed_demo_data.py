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
from app.models.system import SystemSetting, AnalysisRun, Report
from app.models.chat import ChatConversation, ChatMessage
from app.models.audit import AuditLog

CENTER_LAT = float(os.getenv("DEMO_CENTER_LAT", 17.4399))
CENTER_LON = float(os.getenv("DEMO_CENTER_LON", 78.4983))

def reset_database():
    print("Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("All tables recreated cleanly.")

def seed(reset: bool = False):
    if reset:
        reset_database()
    else:
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("1. Seeding Demo Users...")
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

        print("3. Seeding 47 Hotspots (Critical 12 / High 15 / Medium 13 / Low 7; Statuses 9/11/8/11/6/2)...")
        existing_hotspots = db.query(Hotspot).count()
        if existing_hotspots < 47:
            # Clear to ensure exact match if partial exists
            db.query(Recommendation).delete()
            db.query(HotspotFactor).delete()
            db.query(HotspotIntervention).delete()
            db.query(HotspotComment).delete()
            db.query(Hotspot).delete()
            db.commit()

            # Top 10 Reference Hotspots
            # Critical: 2, High: 4, Medium: 3, Low: 1
            # Status: Under review 3, Assigned 2, Action in progress 2, Identified 1, Implemented 1, Closed 1
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
                    "score": 34.0,  # Low score < 40
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

                for f_name, f_pct in item.get("factors", []):
                    db.add(HotspotFactor(
                        hotspot_id=h.id,
                        factor_key=f_name.lower().replace(" ", "_"),
                        label=f_name,
                        percent=float(f_pct),
                        count=int((f_pct / 100) * item["accidents"])
                    ))

                for r_title, r_desc, r_conf in item.get("recommendations", []):
                    db.add(Recommendation(
                        hotspot_id=h.id,
                        title=r_title,
                        linked_factor="Road Environment & Traffic Flow",
                        evidence_text=r_desc,
                        confidence=r_conf,
                        is_ai_generated=True
                    ))

                if "intervention" in item:
                    inv = item["intervention"]
                    db.add(HotspotIntervention(
                        hotspot_id=h.id,
                        description=f"{inv['type']} - Pre: {inv['pre_accidents']} crashes, Post: {inv['post_accidents']} crashes (-{inv['reduction_pct']}%)",
                        implemented_on=inv["date"],
                        recorded_by=user_map["Sana Fatima"].id
                    ))

            # Remaining 37 hotspots to reach exact targets:
            # Target total: 47
            # Risk: Critical 12 (10 remaining), High 15 (11 remaining), Medium 13 (10 remaining), Low 7 (6 remaining)
            # Status: Identified 9 (8 remaining), Under review 11 (8 remaining), Assigned 8 (6 remaining),
            #         Action in progress 11 (9 remaining), Implemented 6 (5 remaining), Closed 2 (1 remaining)
            # All scores strictly within risk range:
            # Critical >= 80, High 60-79.9, Medium 40-59.9, Low < 40.
            remaining_specs = [
                # 10 Critical (scores 81 - 93)
                ("critical", 89.5, "Under review", None),
                ("critical", 87.2, "Under review", None),
                ("critical", 85.0, "Under review", None),
                ("critical", 84.1, "Under review", None),
                ("critical", 91.0, "Assigned", user_map.get("Ravi Kumar")),
                ("critical", 83.5, "Assigned", user_map.get("Imran Sheikh")),
                ("critical", 88.0, "Action in progress", user_map.get("Sana Fatima")),
                ("critical", 86.4, "Action in progress", user_map.get("Meera Iyer")),
                ("critical", 82.0, "Action in progress", user_map.get("Ravi Kumar")),
                ("critical", 81.5, "Identified", None),

                # 11 High (scores 62 - 78)
                ("high", 77.0, "Identified", None),
                ("high", 75.5, "Identified", None),
                ("high", 72.0, "Identified", None),
                ("high", 74.0, "Assigned", user_map.get("Imran Sheikh")),
                ("high", 69.5, "Assigned", user_map.get("Sana Fatima")),
                ("high", 67.0, "Assigned", user_map.get("Meera Iyer")),
                ("high", 76.2, "Action in progress", user_map.get("Sana Fatima")),
                ("high", 71.8, "Action in progress", user_map.get("Ravi Kumar")),
                ("high", 65.4, "Action in progress", user_map.get("Imran Sheikh")),
                ("high", 73.0, "Under review", None),
                ("high", 68.2, "Under review", None),

                # 10 Medium (scores 41 - 58)
                ("medium", 57.0, "Identified", None),
                ("medium", 53.5, "Identified", None),
                ("medium", 49.0, "Identified", None),
                ("medium", 56.2, "Under review", None),
                ("medium", 48.0, "Under review", None),
                ("medium", 52.0, "Assigned", user_map.get("Meera Iyer")),
                ("medium", 55.4, "Action in progress", user_map.get("Sana Fatima")),
                ("medium", 45.0, "Action in progress", user_map.get("Ravi Kumar")),
                ("medium", 51.0, "Implemented", user_map.get("Meera Iyer")),
                ("medium", 43.5, "Implemented", user_map.get("Sana Fatima")),

                # 6 Low (scores 21 - 38)
                ("low", 38.0, "Identified", None),
                ("low", 35.5, "Action in progress", user_map.get("Imran Sheikh")),
                ("low", 32.0, "Implemented", user_map.get("Meera Iyer")),
                ("low", 28.5, "Implemented", user_map.get("Sana Fatima")),
                ("low", 24.0, "Implemented", user_map.get("Meera Iyer")),
                ("low", 31.0, "Closed", user_map.get("Asha Reddy")),
            ]

            used_codes = {item["code"] for item in top_ten}
            code_counter = 301

            for idx, (risk_lvl, score, st, assignee) in enumerate(remaining_specs, start=11):
                while f"H-{code_counter:04d}" in used_codes:
                    code_counter += 1
                code = f"H-{code_counter:04d}"
                used_codes.add(code)
                code_counter += 1

                lat_jitter = CENTER_LAT + random.uniform(-0.07, 0.07)
                lon_jitter = CENTER_LON + random.uniform(-0.07, 0.07)
                deaths = random.randint(4, 7) if risk_lvl == "critical" else (random.randint(1, 3) if risk_lvl == "high" else (1 if risk_lvl == "medium" else 0))
                accidents = random.randint(30, 38) if risk_lvl == "critical" else (random.randint(18, 28) if risk_lvl == "high" else random.randint(10, 20))
                injuries = random.randint(accidents, int(accidents * 1.5))

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
                    risk_score=score,
                    risk_level=risk_lvl,
                    status=st,
                    assignee_id=assignee.id if assignee else None,
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
            print("Successfully populated exactly 47 Hotspots!")

        print("4. Seeding Exactly 4,812 Synthetic Accidents (389 Fatalities, 5,274 Injured)...")
        current_accidents = db.query(AccidentRecord).count()
        if current_accidents < 4812:
            db.query(AccidentRecord).delete()
            db.commit()

            hotspot_centers = db.query(Hotspot.lat, Hotspot.lon).all()
            if not hotspot_centers:
                hotspot_centers = [(CENTER_LAT, CENTER_LON)]

            start_date = datetime(2025, 12, 1, tzinfo=timezone.utc)
            total_target = 4812
            target_fatalities = 389
            target_injuries = 5274

            # Generate distributions matching target totals exactly
            # Fatalities: 389 records with 1 fatality
            fatal_indices = set(random.sample(range(total_target), target_fatalities))

            # Remaining 4423 records have 0 fatalities
            # Injuries allocation across records:
            # We need 5,274 injuries across 4,812 records.
            # Average is ~1.096 per record.
            injuries_array = [0] * total_target

            # Give 1 injury to 3,500 records
            # Give 2 injuries to 700 records (1400)
            # Give 3 injuries to 124 records (372)
            # Give 1 extra injury to 2 records (2)
            # Sum = 3500 + 1400 + 372 + 2 = 5274!
            inj_pool = (
                [1] * 3500 +
                [2] * 700 +
                [3] * 124 +
                [0] * (total_target - 3500 - 700 - 124)
            )
            # Ensure sum is exact
            curr_inj_sum = sum(inj_pool)
            diff = target_injuries - curr_inj_sum
            if diff > 0:
                for d in range(diff):
                    inj_pool[d] += 1
            random.seed(42)  # Deterministic seed for reproducible data
            random.shuffle(inj_pool)

            weather_choices = ["Clear", "Rain", "Fog", "Cloudy"]
            road_types = ["national_highway", "state_highway", "city_road", "junction"]

            batch_records = []
            for i in range(total_target):
                acc_code = f"ACC-2026-{i + 1:05d}"
                fatalities = 1 if i in fatal_indices else 0
                injuries = inj_pool[i]

                # Determine severity based on casualties
                if fatalities > 0:
                    sev = "fatal"
                elif injuries >= 2:
                    sev = "grievous_injury"
                elif injuries == 1:
                    sev = "minor_injury"
                else:
                    sev = "non_injury"

                # Cluster near hotspots or along major corridors
                if random.random() < 0.70:
                    center = random.choice(hotspot_centers)
                    lat = center[0] + random.gauss(0, 0.0018)
                    lon = center[1] + random.gauss(0, 0.0018)
                else:
                    lat = CENTER_LAT + random.uniform(-0.08, 0.08)
                    lon = CENTER_LON + random.uniform(-0.08, 0.08)

                days_offset = random.randint(0, 350)
                # Realistic hour distribution with evening rush peak (6-9pm)
                if random.random() < 0.40:
                    hour = random.randint(18, 21)
                else:
                    hour = random.randint(0, 23)

                occurred = start_date + timedelta(days=days_offset, hours=hour, minutes=random.randint(0, 59))

                rec = AccidentRecord(
                    id=str(uuid.uuid4()),
                    accident_code=acc_code,
                    occurred_at=occurred,
                    latitude=round(lat, 6),
                    longitude=round(lon, 6),
                    location_text="NH-65 Corridor Sector, Hyderabad",
                    geocode_confidence=round(random.uniform(0.88, 1.0), 2),
                    severity=sev,
                    fatalities=fatalities,
                    injuries=injuries,
                    vehicle_types=["two_wheeler", "car"] if random.random() < 0.5 else ["two_wheeler"],
                    weather=random.choice(weather_choices),
                    road_type=random.choice(road_types),
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

            print("Successfully populated exactly 4,812 accident records!")

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
            if not db.query(NotificationSetting).filter(NotificationSetting.user_id == u.id).first():
                db.add(NotificationSetting(user_id=u.id))
        db.commit()

        print("6. Seeding System Settings, Analysis Runs, and Reports...")
        settings_data = [
            ("risk_score_weights", {"fatalities": 5.0, "grievous_injuries": 3.0, "minor_injuries": 1.0, "frequency": 1.0}, "Weights for risk score calculation"),
            ("clustering_parameters", {"radius_meters": 250, "min_accidents": 5, "eps_degrees": 0.00225}, "DBSCAN spatial clustering hyperparameters"),
            ("system_metadata", {"version": "1.0.0", "city": "Hyderabad", "state": "Telangana", "hotspot_count_target": 47}, "System metadata and display constants")
        ]
        for key, val, desc in settings_data:
            if not db.query(SystemSetting).filter(SystemSetting.key == key).first():
                db.add(SystemSetting(key=key, value=val, description=desc))

        if not db.query(AnalysisRun).filter(AnalysisRun.run_number == "AR-2026-001").first():
            db.add(AnalysisRun(
                run_number="AR-2026-001",
                started_by=user_map["Dr. Kiran Rao"].id,
                parameters={"radius_m": 250, "min_accidents": 5, "algorithm": "DBSCAN"},
                status="completed",
                record_count="4812",
                duration_ms="4200"
            ))

        if not db.query(Report).filter(Report.title == "Monthly Hotspot Summary - Nov 2026").first():
            db.add(Report(
                title="Monthly Hotspot Summary - Nov 2026",
                type="summary",
                params={"month": "2026-11", "zone": "All"},
                format="pdf",
                object_key="reports/summary_2026_11.pdf",
                created_by=user_map["Asha Reddy"].id
            ))
            db.add(Report(
                title="Zone 5 High-Risk Junctions Export",
                type="trends",
                params={"zone": "Zone 5 (NH-65)", "min_risk": "high"},
                format="csv",
                object_key="reports/zone5_high_risk.csv",
                created_by=user_map["Dr. Kiran Rao"].id
            ))
        db.commit()

        print("7. Seeding AI Chat Conversations & Messages...")
        asha = user_map.get("Asha Reddy")
        if asha and not db.query(ChatConversation).filter(ChatConversation.user_id == asha.id).first():
            conv = ChatConversation(
                id=str(uuid.uuid4()),
                user_id=asha.id,
                title="Zone 5 Fatal Junction Inquiry"
            )
            db.add(conv)
            db.flush()

            db.add_all([
                ChatMessage(
                    conversation_id=conv.id,
                    user_id=asha.id,
                    role="user",
                    content="Which junction in Zone 5 has the highest fatality count and what are the primary factors?"
                ),
                ChatMessage(
                    conversation_id=conv.id,
                    user_id=None,
                    role="assistant",
                    content="NH-65 × Station Road Junction (Hotspot H-0142) has the highest fatality count in Zone 5 with 9 deaths, 63 injuries, and a risk score of 92 (Critical). Peak crash hours are 6–9 pm on Fridays and Saturdays.\n\nKey contributing factors:\n1. Two-wheelers turning (58%)\n2. Poor street lighting (46%)\n3. Overspeeding on merge (34%)\n\nRecommended engineering countermeasures:\n- Install high-mast LED illumination\n- Raised table pedestrian zebra crossing\n- Synchronized traffic signal with turn bay\n\nAI-generated · expert review needed",
                    cited_hotspot_ids=["H-0142"],
                    caveats="AI-generated · expert review needed"
                )
            ])
            db.commit()

        print("8. Seeding Sample Audit Logs (FR-13)...")
        if db.query(AuditLog).count() == 0:
            db.add_all([
                AuditLog(
                    actor_id=user_map["Dr. Kiran Rao"].id,
                    actor_name="Dr. Kiran Rao",
                    actor_role="admin",
                    action="approve_user",
                    entity_type="user",
                    entity_id=user_map["Asha Reddy"].id,
                    before_state={"status": "pending"},
                    after_state={"status": "active"},
                    reason="Verified credentials with Road Safety Authority"
                ),
                AuditLog(
                    actor_id=user_map["Asha Reddy"].id,
                    actor_name="Asha Reddy",
                    actor_role="safety_analyst",
                    action="import",
                    entity_type="import_batch",
                    entity_id=batch.id if batch else "batch-01",
                    before_state=None,
                    after_state={"file": "Telangana_Crash_Data_2026.csv", "accepted_rows": 3214},
                    reason="Annual accident data batch upload"
                ),
                AuditLog(
                    actor_id=user_map["Dr. Kiran Rao"].id,
                    actor_name="Dr. Kiran Rao",
                    actor_role="admin",
                    action="assign",
                    entity_type="hotspot",
                    entity_id="H-0087",
                    before_state={"status": "Identified", "assignee": None},
                    after_state={"status": "Assigned", "assignee": "Ravi Kumar"},
                    reason="High priority expressway exit intervention required"
                )
            ])
            db.commit()

        print("9. Creating Test CSV with seeded issues in docs/...")
        os.makedirs("docs", exist_ok=True)
        issue_csv_path = os.path.join("docs", "accident_test_dataset_with_issues.csv")
        with open(issue_csv_path, "w", encoding="utf-8") as f:
            f.write("record_id,occurred_at,latitude,longitude,location_name,severity,fatalities,injuries,vehicle_number,driver_name,driver_phone,weather,road_type\n")
            f.write("ACC-TEST-001,2026-03-10 18:30:00,17.4399,78.4983,Station Rd Junction,Fatal,1,2,TS09EA1234,Ramesh Chandra,9876543210,Clear,National Highway\n")
            f.write("ACC-TEST-001,2026-03-10 18:30:00,17.4399,78.4983,Station Rd Junction,Fatal,1,2,TS09EA1234,Ramesh Chandra,9876543210,Clear,National Highway\n")
            f.write("ACC-TEST-002,2026-03-11 20:15:00,95.1234,78.4890,Market Cross,Grievous injury,0,3,AP28Z9999,Sunil Verma,9848022338,Rain,City Road\n")
            f.write("ACC-TEST-003,2026-03-12 14:00:00,17.4125,78.5320,ORR Exit 12,Grievious,0,1,DL1CAB1234,John Doe,9988776655,Clear,Expressway\n")
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
    import argparse
    parser = argparse.ArgumentParser(description="Seed demo data")
    parser.add_argument("--reset", action="store_true", help="Reset all tables before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
