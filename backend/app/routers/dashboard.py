from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.security.auth_dependencies import get_current_user

router = APIRouter(tags=["Finance - Dashboard & Alerts"])

@router.get("/dashtest")
def dashboard_test():
    return {"msg": "dashtest works"}

# ═══════════════════════════════════════════
#  ALERTS
# ═══════════════════════════════════════════

@router.get("/alerts")
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Alert).filter(Alert.user_id == current_user.user_id)
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    if severity:
        query = query.filter(Alert.severity == severity)
    alerts = query.order_by(Alert.created_at.desc()).all()

    active_count = db.query(Alert).filter(Alert.user_id == current_user.user_id, Alert.status == "active").count()
    critical_count = db.query(Alert).filter(Alert.user_id == current_user.user_id, Alert.status == "active", Alert.severity == "critical").count()

    return {"success": True, "data": {
        "alerts": [
            {"alert_id": a.alert_id, "alert_type": a.alert_type, "severity": a.severity,
             "message": a.message, "metric_value": float(a.metric_value) if a.metric_value else None,
             "threshold": float(a.threshold) if a.threshold else None, "status": a.status,
             "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in alerts
        ],
        "total_active": active_count, "critical_count": critical_count,
    }}


@router.patch("/alerts/{alert_id}/dismiss")
def dismiss_alert(alert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.alert_id == alert_id, Alert.user_id == current_user.user_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = "ignored"
    db.commit()
    return {"success": True, "message": "Alert dismissed"}


# ═══════════════════════════════════════════
#  DASHBOARD — Decoupled Endpoints
# ═══════════════════════════════════════════

@router.get("/dashboard/personal")
def get_personal_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Personal-only dashboard — returns only personal metrics, alerts, and goals."""
    from app.services.dashboard_service import get_personal_dashboard as _get_personal
    data = _get_personal(current_user.user_id, db)
    return {"success": True, "data": data}


@router.get("/dashboard/business")
def get_business_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Business-only dashboard — returns only business metrics, alerts, and goals."""
    if current_user.account_type not in ("business", "both"):
        raise HTTPException(403, "Business dashboard not available for personal accounts")
    from app.services.dashboard_service import get_business_dashboard as _get_business
    data = _get_business(current_user.user_id, db)
    return {"success": True, "data": data}


@router.get("/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Backward-compatible combined dashboard."""
    from app.services.dashboard_service import get_dashboard as _get_dashboard
    data = _get_dashboard(current_user.user_id, db)
    return {"success": True, "data": data}

