import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.accident import AccidentRecord
from app.models.hotspot import Hotspot, HotspotFactor, Recommendation
from app.models.system import AnalysisRun, SystemSetting
from app.models.notification import Notification
from app.models.user import User, UserRoleEnum
from app.api.deps import record_audit
from analytics.hotspots import hotspot_detector
from analytics.scoring import calculate_risk_scores
from analytics.factors import analyze_hotspot_factors
from analytics.recommendations import generate_recommendations


class HotspotAnalysisService:

    def run_analysis(
        self,
        db: Session,
        actor_id: str,
        radius_m: float = 250.0,
        min_accidents: int = 5,
        period_months: int = 12,
    ) -> Dict[str, Any]:
        """
        Execute full spatial analytics pipeline:
        DBSCAN -> Multi-criteria Risk Scoring -> Contributing Factors -> Grounded Recommendations (FR-04, FR-05, FR-07)
        """
        start_time = time.time()
        run_number = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # 1. Fetch accident records from DB
        db_records = db.query(AccidentRecord).all()
        records_data = [
            {
                "id": r.id,
                "accident_code": r.accident_code,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "location_text": r.location_text,
                "road_name": r.road_name,
                "severity": r.severity,
                "fatalities": r.fatalities,
                "injuries": r.injuries,
                "vehicle_types": r.vehicle_types,
                "weather": r.weather,
                "light_condition": r.light_condition,
                "probable_cause": r.probable_cause,
                "occurred_at": r.occurred_at,
            }
            for r in db_records
        ]

        # 2. Spatial Clustering (DBSCAN)
        clusters, err_msg = hotspot_detector.detect_clusters(
            records=records_data,
            radius_m=radius_m,
            min_accidents=min_accidents,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # 3. Handle Insufficient Data Rule
        if err_msg or not clusters:
            run_obj = AnalysisRun(
                run_number=run_number,
                started_by=actor_id,
                parameters={
                    "radius_m": radius_m,
                    "min_accidents": min_accidents,
                    "period_months": period_months,
                },
                status="completed_no_clusters",
                record_count=str(len(records_data)),
                duration_ms=str(duration_ms),
            )
            db.add(run_obj)
            db.commit()
            return {
                "message": err_msg or "No reliable hotspot can be determined from this data",
                "run_number": run_number,
                "hotspots_found": 0,
                "record_count": len(records_data),
                "duration_ms": duration_ms,
            }

        # 4. Risk Scoring & Classification
        scored_clusters = calculate_risk_scores(clusters)

        # 5. Persist Hotspots, Factors, and Recommendations
        created_hotspots = []
        critical_hotspots = []

        for idx, cluster in enumerate(scored_clusters, start=1):
            code = f"H-{str(idx).padStart(4, '0')}" if hasattr(str(idx), 'padStart') else f"H-{idx:04d}"
            
            # Check if hotspot already exists by code
            existing = db.query(Hotspot).filter(Hotspot.code == code).first()
            if not existing:
                hotspot = Hotspot(
                    code=code,
                    name=cluster["name"],
                    road_name=cluster["name"],
                    lat=cluster["centroid_lat"],
                    lon=cluster["centroid_lon"],
                    accidents_count=cluster["accidents_count"],
                    fatalities=cluster["fatalities"],
                    injured=cluster["injuries"],
                    risk_score=cluster["risk_score"],
                    score_breakdown=cluster["score_breakdown"],
                    risk_level=cluster["risk_level"],
                    status="Identified",
                    analysis_run_id=run_number,
                )
                db.add(hotspot)
                db.commit()
                db.refresh(hotspot)
            else:
                hotspot = existing
                hotspot.accidents_count = cluster["accidents_count"]
                hotspot.fatalities = cluster["fatalities"]
                hotspot.injured = cluster["injuries"]
                hotspot.risk_score = cluster["risk_score"]
                hotspot.score_breakdown = cluster["score_breakdown"]
                hotspot.risk_level = cluster["risk_level"]
                db.commit()

            # Factors analysis
            factor_analysis = analyze_hotspot_factors(cluster["accidents"])
            hotspot.peak_time_text = factor_analysis["peak_time_text"]

            # Clear old factors and add updated
            db.query(HotspotFactor).filter(HotspotFactor.hotspot_id == hotspot.id).delete()
            for f in factor_analysis["factors"]:
                db.add(HotspotFactor(
                    hotspot_id=hotspot.id,
                    factor_key=f["factor_key"],
                    label=f["label"],
                    count=f["count"],
                    percent=f["percent"],
                    time_blocks=factor_analysis["time_blocks"],
                ))

            # Recommendations
            db.query(Recommendation).filter(Recommendation.hotspot_id == hotspot.id).delete()
            recs = generate_recommendations(
                factors=factor_analysis["factors"],
                total_accidents=cluster["accidents_count"],
                time_blocks=factor_analysis["time_blocks"],
            )
            for r in recs:
                db.add(Recommendation(
                    hotspot_id=hotspot.id,
                    title=r["title"],
                    linked_factor=r["linked_factor"],
                    evidence_text=r["evidence_text"],
                    confidence=r["confidence"],
                    is_ai_generated=True,
                ))

            db.commit()
            created_hotspots.append(hotspot)

            if hotspot.risk_level == "critical":
                critical_hotspots.append(hotspot)

        # 6. Trigger Notifications for Critical Hotspots (BR-06)
        if critical_hotspots:
            # Send notification to safety analysts and police officers
            eligible_users = db.query(User).filter(
                User.role.in_([UserRoleEnum.ADMIN, UserRoleEnum.SAFETY_ANALYST, UserRoleEnum.POLICE_OFFICER]),
                User.status == "active",
            ).all()

            for h in critical_hotspots[:3]:
                for u in eligible_users:
                    db.add(Notification(
                        user_id=u.id,
                        type="critical_detected",
                        title=f"Critical Hotspot Detected: {h.code}",
                        body=f"{h.name} reached Critical risk score of {int(h.risk_score)} ({h.accidents_count} accidents, {h.fatalities} deaths).",
                        entity_id=h.id,
                    ))
            db.commit()

        # Log analysis run
        run_obj = AnalysisRun(
            run_number=run_number,
            started_by=actor_id,
            parameters={
                "radius_m": radius_m,
                "min_accidents": min_accidents,
                "period_months": period_months,
            },
            status="completed",
            record_count=str(len(records_data)),
            duration_ms=str(duration_ms),
        )
        db.add(run_obj)
        db.commit()

        record_audit(
            db=db,
            action="run_hotspot_analysis",
            entity_type="analysis_run",
            entity_id=run_obj.id,
            reason=f"Detected {len(created_hotspots)} hotspots in {duration_ms} ms",
        )

        return {
            "message": f"Successfully identified {len(created_hotspots)} hotspots ({len(critical_hotspots)} critical)",
            "run_number": run_number,
            "hotspots_found": len(created_hotspots),
            "critical_count": len(critical_hotspots),
            "record_count": len(records_data),
            "duration_ms": duration_ms,
        }


hotspot_service = HotspotAnalysisService()
