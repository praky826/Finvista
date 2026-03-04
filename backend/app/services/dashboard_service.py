"""
Dashboard Service — Decoupled personal and business dashboard data.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.personal_metrics import PersonalMetrics
from app.models.business_metrics import BusinessMetrics
from app.models.alert import Alert
from app.models.goal import Goal
from app.models.bank_account import BankAccount
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics
from decimal import Decimal
from datetime import date


def get_personal_dashboard(user_id: int, db: Session) -> dict:
    """Get personal dashboard data for a user."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}

    personal = db.query(PersonalMetrics).filter(PersonalMetrics.user_id == user_id).first()
    if not personal:
        recalculate_personal_metrics(user_id, db)
        personal = db.query(PersonalMetrics).filter(PersonalMetrics.user_id == user_id).first()

    alerts = (
        db.query(Alert)
        .filter(Alert.user_id == user_id, Alert.status == "active")
        .order_by(Alert.severity.desc(), Alert.created_at.desc())
        .all()
    )

    # Filter to personal alert types only
    from app.engines.alert_engine import PERSONAL_ALERT_TYPES
    personal_alerts = [a for a in alerts if a.alert_type in PERSONAL_ALERT_TYPES]

    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()

    summary = {
        "net_worth": float(personal.net_worth or 0) if personal else 0,
        "health_score": float(personal.health_score or 0) if personal else 0,
        "dti": float(personal.dti or 0) if personal else 0,
        "emergency_fund": float(personal.emergency_fund or 0) if personal else 0,
        "credit_utilization": float(personal.credit_utilization or 0) if personal else 0,
        "tax_estimate": float(personal.tax_estimate or 0) if personal else 0,
        "savings_ratio": float(personal.savings_ratio or 0) if personal else 0,
        "credit_score_simulation": personal.credit_score_simulation or 0 if personal else 0,
        "cash_flow_monthly": float(personal.cash_flow_monthly or 0) if personal else 0,
        "liquid_asset_percentage": float(personal.liquid_asset_percentage or 0) if personal else 0,
        "loan_to_asset": float(personal.loan_to_asset or 0) if personal else 0,
        "effective_tax_rate": float(personal.effective_tax_rate or 0) if personal else 0,
    }

    # Goal summaries
    goal_data = _build_goal_data(goals)

    return {
        "user_id": user_id,
        "account_type": user.account_type,
        "full_name": user.full_name,
        "monthly_income": float(user.monthly_income or 0),
        "monthly_expenses": float(user.monthly_expenses or 0),
        "summary": summary,
        "alerts": _format_alerts(personal_alerts),
        "goals": goal_data,
        "total_bank_balance": sum(float(a.balance or 0) for a in accounts),
    }


def get_business_dashboard(user_id: int, db: Session) -> dict:
    """Get business dashboard data for a user."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}

    business = db.query(BusinessMetrics).filter(BusinessMetrics.user_id == user_id).first()
    if not business:
        recalculate_business_metrics(user_id, db)
        business = db.query(BusinessMetrics).filter(BusinessMetrics.user_id == user_id).first()

    alerts = (
        db.query(Alert)
        .filter(Alert.user_id == user_id, Alert.status == "active")
        .order_by(Alert.severity.desc(), Alert.created_at.desc())
        .all()
    )

    # Filter to business alert types only
    from app.engines.alert_engine import BUSINESS_ALERT_TYPES
    business_alerts = [a for a in alerts if a.alert_type in BUSINESS_ALERT_TYPES]

    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id, BankAccount.mode == "business").all()

    summary = {
        "business_net_worth": float(business.business_net_worth or 0) if business else 0,
        "net_profit": float(business.net_profit or 0) if business else 0,
        "working_capital": float(business.working_capital or 0) if business else 0,
        "cash_flow": float(business.cash_flow or 0) if business else 0,
        "debt_ratio": float(business.debt_ratio or 0) if business else 0,
        "liquidity_ratio": float(business.liquidity_ratio or 0) if business else 0,
        "gross_profit_margin": float(business.gross_profit_margin or 0) if business else 0,
        "net_profit_margin": float(business.net_profit_margin or 0) if business else 0,
        "emi_burden_ratio": float(business.emi_burden_ratio or 0) if business else 0,
        "total_inventory_value": float(business.total_inventory_value or 0) if business else 0,
        "total_receivables": float(business.total_receivables or 0) if business else 0,
        "total_payables": float(business.total_payables or 0) if business else 0,
    }

    # Goal summaries (business goals only)
    business_goals = [g for g in goals if g.mode == "business"]
    goal_data = _build_goal_data(business_goals)

    return {
        "user_id": user_id,
        "account_type": user.account_type,
        "full_name": user.full_name,
        "summary": summary,
        "alerts": _format_alerts(business_alerts),
        "goals": goal_data,
        "total_bank_balance": sum(float(a.balance or 0) for a in accounts),
    }


def get_dashboard(user_id: int, db: Session) -> dict:
    """
    BACKWARD-COMPATIBLE — Returns combined dashboard.
    Used by the old /dashboard endpoint during frontend transition.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}

    result = {}

    if user.account_type in ("personal", "both"):
        personal_data = get_personal_dashboard(user_id, db)
        result.update(personal_data)

    if user.account_type in ("business", "both"):
        business_data = get_business_dashboard(user_id, db)
        if "summary" in result:
            result["summary"].update(business_data.get("summary", {}))
        else:
            result.update(business_data)
        # Merge business alerts
        result.setdefault("alerts", [])
        result["alerts"].extend(business_data.get("alerts", []))
        # Merge business goals
        result.setdefault("goals", [])
        result["goals"].extend(business_data.get("goals", []))

    return result


# ── Helper functions ──

def _build_goal_data(goals) -> list:
    """Build goal summary list."""
    goal_data = []
    for g in goals:
        today = date.today()
        months_rem = max(((g.deadline - today).days // 30), 0) if g.deadline else 0
        progress = float(g.current_savings / g.target * 100) if g.target > 0 else 0
        goal_data.append({
            "goal_id": g.goal_id,
            "goal_name": g.goal_name,
            "target": float(g.target),
            "current_savings": float(g.current_savings),
            "progress_percent": round(progress, 1),
            "months_remaining": months_rem,
            "mode": g.mode,
            "priority": g.priority,
        })
    return goal_data


def _format_alerts(alerts) -> list:
    """Format alert objects into dicts."""
    return [
        {
            "alert_id": a.alert_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "metric_value": float(a.metric_value) if a.metric_value else None,
            "threshold": float(a.threshold) if a.threshold else None,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]
