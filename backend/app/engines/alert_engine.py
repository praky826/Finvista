"""
Alert Engine — Rule-based alert evaluation.
Split into personal and business alert evaluators.
Each function creates/updates/resolves ONLY its own alert types.
"""
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal
from typing import List, Set
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.goal import Goal
from app.engines import financial_calculations


# ── Alert type categories ──
PERSONAL_ALERT_TYPES = {
    "HIGH_DTI", "HIGH_CREDIT_UTILIZATION", "LOW_EMERGENCY_FUND",
    "GOAL_BEHIND_SCHEDULE", "EMI_DUE_SOON", "CC_DUE_SOON", "FD_MATURING_SOON",
}

BUSINESS_ALERT_TYPES = {
    "NEGATIVE_CASH_FLOW", "LOW_WORKING_CAPITAL", "HIGH_DEBT_RATIO",
    "HIGH_EMI_BURDEN", "LOW_PROFIT_MARGIN",
}


def evaluate_personal_alerts(
    user_id: int,
    metrics,  # PersonalMetrics object
    db: Session,
    user=None,
    tax_info=None,
    loans=None,
    credit_cards=None,
    investments=None,
):
    """Evaluate ONLY personal finance alerts."""
    alerts_to_create: List[dict] = []

    # 1. HIGH DTI (>40%)
    if metrics.dti is not None and metrics.dti > 40:
        alerts_to_create.append({
            "alert_type": "HIGH_DTI",
            "severity": "critical",
            "message": f"Your debt-to-income ratio is {float(metrics.dti):.1f}%, indicating high financial stress. Consider reducing EMI load.",
            "metric_value": metrics.dti,
            "threshold": Decimal(40),
        })

    # 2. HIGH CREDIT UTILIZATION (>30%)
    if metrics.credit_utilization is not None and metrics.credit_utilization > 30:
        severity = "critical" if metrics.credit_utilization > 50 else "warning"
        alerts_to_create.append({
            "alert_type": "HIGH_CREDIT_UTILIZATION",
            "severity": severity,
            "message": f"Credit utilization is {float(metrics.credit_utilization):.1f}%. Keep below 30% for better credit score.",
            "metric_value": metrics.credit_utilization,
            "threshold": Decimal(30),
        })

    # 3. LOW EMERGENCY FUND (<3 months)
    if metrics.emergency_fund is not None and metrics.emergency_fund < 3:
        severity = "critical" if metrics.emergency_fund < 1 else "warning"
        alerts_to_create.append({
            "alert_type": "LOW_EMERGENCY_FUND",
            "severity": severity,
            "message": f"Emergency fund covers only {float(metrics.emergency_fund):.1f} months. Target: 6 months.",
            "metric_value": metrics.emergency_fund,
            "threshold": Decimal(3),
        })

    # 4. GOAL BEHIND SCHEDULE
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    for goal in goals:
        if goal.deadline:
            today = date.today()
            delta = (goal.deadline - today).days
            months_remaining = max(delta // 30, 0)
            if months_remaining > 0:
                remaining = float(goal.target) - float(goal.current_savings)
                if remaining > 0:
                    required_monthly = remaining / months_remaining
                    available = 0
                    if user and user.monthly_income and user.monthly_expenses:
                        available = float(user.monthly_income) - float(user.monthly_expenses)
                    if available > 0 and required_monthly > 0:
                        ratio = available / required_monthly
                        if ratio < 1:
                            alerts_to_create.append({
                                "alert_type": "GOAL_BEHIND_SCHEDULE",
                                "severity": "warning",
                                "message": f"Goal '{goal.goal_name}' is behind schedule. Required: ₹{required_monthly:,.0f}/month.",
                                "metric_value": Decimal(str(round(ratio, 2))),
                                "threshold": Decimal(1),
                            })

    # ── DATE-BASED ALERTS ──
    today = date.today()

    # 5. EMI due within 7 days
    if loans:
        for loan in loans:
            if loan.next_emi_due_date and (loan.next_emi_due_date - today).days <= 7 and (loan.next_emi_due_date - today).days >= 0:
                alerts_to_create.append({
                    "alert_type": "EMI_DUE_SOON",
                    "severity": "info",
                    "message": f"EMI of ₹{float(loan.emi):,.0f} for '{loan.loan_name}' due on {loan.next_emi_due_date}.",
                    "metric_value": loan.emi,
                    "threshold": Decimal(7),
                })
                break  # One reminder is enough

    # 6. Credit card due within 5 days
    if credit_cards:
        for cc in credit_cards:
            if cc.next_due_date and (cc.next_due_date - today).days <= 5 and (cc.next_due_date - today).days >= 0:
                alerts_to_create.append({
                    "alert_type": "CC_DUE_SOON",
                    "severity": "info",
                    "message": f"Credit card '{cc.card_name}' payment due on {cc.next_due_date}.",
                    "metric_value": cc.credit_used,
                    "threshold": Decimal(5),
                })
                break

    # 7. FD maturing within 30 days
    if investments:
        for inv in investments:
            if inv.type == "fd" and inv.maturity_date and (inv.maturity_date - today).days <= 30 and (inv.maturity_date - today).days >= 0:
                alerts_to_create.append({
                    "alert_type": "FD_MATURING_SOON",
                    "severity": "info",
                    "message": f"FD worth ₹{float(inv.value):,.0f} is maturing on {inv.maturity_date}.",
                    "metric_value": inv.value,
                    "threshold": Decimal(30),
                })

    # ── SYNC PERSONAL ALERTS ONLY ──
    _sync_alerts(user_id, alerts_to_create, db, PERSONAL_ALERT_TYPES)


def evaluate_business_alerts(
    user_id: int,
    metrics,  # BusinessMetrics object
    db: Session,
    tax_info=None,
    loans=None,
):
    """Evaluate ONLY business finance alerts."""
    alerts_to_create: List[dict] = []

    # 1. NEGATIVE CASH FLOW
    if metrics.cash_flow is not None and metrics.cash_flow < 0:
        alerts_to_create.append({
            "alert_type": "NEGATIVE_CASH_FLOW",
            "severity": "critical",
            "message": f"Cash flow is negative (₹{float(metrics.cash_flow):,.0f}). Business spending exceeds earnings.",
            "metric_value": metrics.cash_flow,
            "threshold": Decimal(0),
        })

    # 2. LOW WORKING CAPITAL
    if metrics.working_capital is not None and tax_info and tax_info.business_expenses:
        monthly_exp = float(tax_info.business_expenses)
        if float(metrics.working_capital) < monthly_exp:
            alerts_to_create.append({
                "alert_type": "LOW_WORKING_CAPITAL",
                "severity": "warning",
                "message": f"Working capital is ₹{float(metrics.working_capital):,.0f}. Maintain at least 1 month of expenses.",
                "metric_value": metrics.working_capital,
                "threshold": Decimal(str(monthly_exp)),
            })

    # 3. HIGH DEBT RATIO (>60%)
    if metrics.debt_ratio is not None and metrics.debt_ratio > 60:
        alerts_to_create.append({
            "alert_type": "HIGH_DEBT_RATIO",
            "severity": "critical",
            "message": f"Debt ratio is {float(metrics.debt_ratio):.1f}%. You're over-leveraged. Target: <60%.",
            "metric_value": metrics.debt_ratio,
            "threshold": Decimal(60),
        })

    # 4. HIGH EMI BURDEN (>30% of revenue)
    if metrics.emi_burden_ratio is not None and metrics.emi_burden_ratio > 30:
        alerts_to_create.append({
            "alert_type": "HIGH_EMI_BURDEN",
            "severity": "warning",
            "message": f"EMI burden is {float(metrics.emi_burden_ratio):.1f}% of revenue. Keep below 30%.",
            "metric_value": metrics.emi_burden_ratio,
            "threshold": Decimal(30),
        })

    # 5. LOW PROFIT MARGIN (<5%)
    if metrics.net_profit_margin is not None and metrics.net_profit_margin < 5:
        alerts_to_create.append({
            "alert_type": "LOW_PROFIT_MARGIN",
            "severity": "warning",
            "message": f"Net profit margin is {float(metrics.net_profit_margin):.1f}%. Improve pricing or cut costs.",
            "metric_value": metrics.net_profit_margin,
            "threshold": Decimal(5),
        })

    # ── SYNC BUSINESS ALERTS ONLY ──
    _sync_alerts(user_id, alerts_to_create, db, BUSINESS_ALERT_TYPES)


def _sync_alerts(user_id: int, alerts_to_create: List[dict], db: Session, allowed_types: Set[str]):
    """
    Create/update/resolve alerts in the database.
    ONLY touches alert types within allowed_types — never resolves alerts from the other domain.
    """
    active_types = {a["alert_type"] for a in alerts_to_create}

    for alert_data in alerts_to_create:
        existing = (
            db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.alert_type == alert_data["alert_type"],
                Alert.status == "active",
            )
            .first()
        )

        if existing:
            existing.message = alert_data["message"]
            existing.metric_value = alert_data["metric_value"]
            existing.severity = alert_data["severity"]
            existing.updated_at = datetime.now(timezone.utc)
        else:
            new_alert = Alert(
                user_id=user_id,
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                message=alert_data["message"],
                metric_value=alert_data["metric_value"],
                threshold=alert_data["threshold"],
                status="active",
            )
            db.add(new_alert)

    # Resolve alerts that no longer apply — ONLY within our domain
    existing_alerts = (
        db.query(Alert).filter(Alert.user_id == user_id, Alert.status == "active").all()
    )
    for alert in existing_alerts:
        if alert.alert_type in allowed_types and alert.alert_type not in active_types:
            alert.status = "resolved"
            alert.resolved_at = datetime.now(timezone.utc)

    db.commit()
