from sqlalchemy.orm import Session
from app.core.db import engine, Base, SessionLocal
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.hotspot import Hotspot
from app.core.security import get_password_hash

def init_db_and_seed():
    """Ensure database tables and initial demo users / critical hotspots exist."""
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            # Check if demo users exist
            existing_asha = db.query(User).filter(User.email.in_(["asha@demo.in", "asha.reddy@police.gov.in"])).first()
            if not existing_asha:
                pwd_hash = get_password_hash("DemoPass123!")
                gov_pwd_hash = get_password_hash("Password123!")

                users = [
                    # Quick demo accounts
                    User(
                        full_name="Asha Reddy",
                        email="asha@demo.in",
                        organisation="Road Safety Analysis Cell",
                        role=UserRoleEnum.SAFETY_ANALYST,
                        password_hash=pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Dr. Kiran Rao",
                        email="admin@demo.in",
                        organisation="State Transport Department",
                        role=UserRoleEnum.ADMIN,
                        password_hash=pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Ravi Kumar",
                        email="ravi@demo.in",
                        organisation="Hyderabad Traffic Police",
                        role=UserRoleEnum.POLICE_OFFICER,
                        password_hash=pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Sana Fatima",
                        email="sana@demo.in",
                        organisation="Greater Hyderabad Municipal Corp",
                        role=UserRoleEnum.AUTHORITY_OFFICIAL,
                        password_hash=pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    # Official government accounts
                    User(
                        full_name="Asha Reddy",
                        email="asha.reddy@police.gov.in",
                        organisation="Road Safety Analysis Cell",
                        role=UserRoleEnum.SAFETY_ANALYST,
                        password_hash=gov_pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Dr. Kiran Rao",
                        email="admin@police.gov.in",
                        organisation="State Transport Department",
                        role=UserRoleEnum.ADMIN,
                        password_hash=gov_pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Ravi Kumar",
                        email="ravi.kumar@police.gov.in",
                        organisation="Hyderabad Traffic Police",
                        role=UserRoleEnum.POLICE_OFFICER,
                        password_hash=gov_pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                    User(
                        full_name="Sana Fatima",
                        email="sana.fatima@transport.gov.in",
                        organisation="Greater Hyderabad Municipal Corp",
                        role=UserRoleEnum.AUTHORITY_OFFICIAL,
                        password_hash=gov_pwd_hash,
                        status=UserStatusEnum.ACTIVE,
                    ),
                ]
                db.add_all(users)
                db.commit()

            # Check if demo hotspot H-0142 exists
            h_count = db.query(Hotspot).count()
            if h_count == 0:
                demo_h = Hotspot(
                    code="H-0142",
                    name="NH-65 × Station Road Junction",
                    road_name="National Highway 65",
                    latitude=17.4125,
                    longitude=78.5721,
                    risk_score=92.0,
                    risk_level="critical",
                    accidents_count=41,
                    fatalities_count=9,
                    injuries_count=63,
                    status="Under review",
                    severity_index=8.4,
                    peak_hours_json='["18:00-21:00"]',
                    primary_collision_type="Side-impact collision",
                )
                db.add(demo_h)
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"init_db_and_seed notice: {e}")
