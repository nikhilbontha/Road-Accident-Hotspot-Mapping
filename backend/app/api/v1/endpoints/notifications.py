from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from app.core.db import get_db
from app.api import deps
from app.models.notification import Notification, NotificationSetting
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationSettingsUpdate(BaseModel):
    critical_detected: Optional[bool] = None
    assigned: Optional[bool] = None
    risk_changed: Optional[bool] = None
    action_implemented: Optional[bool] = None

@router.get("")
def list_notifications(
    filter: str = Query("all", pattern="^(all|unread)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    List user notifications.
    Groups items into 'Today' and 'Earlier this week'.
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if filter == "unread":
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    now = datetime.now(timezone.utc)
    today_items = []
    earlier_items = []

    for n in notifications:
        item = {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "entity_id": n.entity_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "time_ago": format_time_ago(n.created_at, now)
        }
        # Categorize today vs earlier
        if n.created_at and (now - n.created_at).total_seconds() < 86400:
            today_items.append(item)
        else:
            earlier_items.append(item)

    # Provide demo fallback items if user has 0 notifications yet
    if not notifications:
        demo_notifications = [
            {
                "id": "notif-1",
                "type": "critical_detected",
                "title": "New Critical Hotspot detected: H-0142",
                "body": "NH-65 × Station Road Junction reached risk score 92 with 9 fatalities.",
                "entity_id": "H-0142",
                "is_read": False,
                "created_at": (now - timedelta(hours=2)).isoformat(),
                "time_ago": "2 hours ago"
            },
            {
                "id": "notif-2",
                "type": "assigned",
                "title": "Hotspot H-0087 assigned to you",
                "body": "Outer Ring Road, Exit 12 has been assigned to you by Dr. Kiran Rao for engineering review.",
                "entity_id": "H-0087",
                "is_read": False,
                "created_at": (now - timedelta(hours=5)).isoformat(),
                "time_ago": "5 hours ago"
            },
            {
                "id": "notif-3",
                "type": "risk_changed",
                "title": "Risk level elevated on H-0103",
                "body": "Market Road Curve upgraded to High (score 79) after Q3 data refresh.",
                "entity_id": "H-0103",
                "is_read": True,
                "created_at": (now - timedelta(days=2)).isoformat(),
                "time_ago": "2 days ago"
            },
            {
                "id": "notif-4",
                "type": "action_implemented",
                "title": "Intervention marked implemented on H-0061",
                "body": "School Crossing, Ring Road zebra crossing and amber beacons completed by Municipal Corporation.",
                "entity_id": "H-0061",
                "is_read": True,
                "created_at": (now - timedelta(days=4)).isoformat(),
                "time_ago": "4 days ago"
            }
        ]
        if filter == "unread":
            demo_notifications = [n for n in demo_notifications if not n["is_read"]]
        
        unread_count = 2
        today_items = [demo_notifications[0], demo_notifications[1]] if len(demo_notifications) >= 2 else demo_notifications
        earlier_items = demo_notifications[2:] if len(demo_notifications) > 2 else []

    return {
        "unread_count": unread_count,
        "today": today_items,
        "earlier": earlier_items,
        "total": len(today_items) + len(earlier_items)
    }

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if n:
        n.is_read = True
        db.commit()
    return {"status": "ok", "id": notification_id, "is_read": True}

@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok", "message": "All notifications marked as read"}

@router.get("/settings")
def get_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    settings = db.query(NotificationSetting).filter(NotificationSetting.user_id == current_user.id).first()
    if not settings:
        settings = NotificationSetting(
            user_id=current_user.id,
            critical_detected=True,
            assigned=True,
            risk_changed=True,
            action_implemented=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return {
        "critical_detected": settings.critical_detected,
        "assigned": settings.assigned,
        "risk_changed": settings.risk_changed,
        "action_implemented": settings.action_implemented,
        "channel_note": "Notifications appear here in the app. Email and SMS are not available yet."
    }

@router.put("/settings")
def update_notification_settings(
    payload: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    settings = db.query(NotificationSetting).filter(NotificationSetting.user_id == current_user.id).first()
    if not settings:
        settings = NotificationSetting(user_id=current_user.id)
        db.add(settings)

    if payload.critical_detected is not None:
        settings.critical_detected = payload.critical_detected
    if payload.assigned is not None:
        settings.assigned = payload.assigned
    if payload.risk_changed is not None:
        settings.risk_changed = payload.risk_changed
    if payload.action_implemented is not None:
        settings.action_implemented = payload.action_implemented

    db.commit()
    return {
        "status": "ok",
        "critical_detected": settings.critical_detected,
        "assigned": settings.assigned,
        "risk_changed": settings.risk_changed,
        "action_implemented": settings.action_implemented
    }

def format_time_ago(dt: Optional[datetime], now: datetime) -> str:
    if not dt:
        return "recently"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        mins = seconds // 60
        return f"{mins} min ago" if mins == 1 else f"{mins} mins ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
    days = seconds // 86400
    return f"{days} day ago" if days == 1 else f"{days} days ago"
