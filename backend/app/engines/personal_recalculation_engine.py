"""
Personal Recalculation Engine — Handles ONLY personal finance metrics.
Fetches personal data → Aggregates → Calculates → Upserts PersonalMetrics → Triggers personal alerts.
Called by services whenever personal financial data changes.
"""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.bank_account import BankAccount
from app.models.loan import Loan
from app.models.credit_card import CreditCard
from app.models.investment import Investment
from app.models.tax import Tax
from app.models.personal_metrics import PersonalMetrics
from app.models.cash import Cash
from app.engines import financial_calculations
from app.engines import health_score_engine
from app.engines.alert_engine import evaluate_personal_alerts


def recalculate_personal_metrics(user_id: int, db: Session) -> dict:
    """
    PERSONAL ORCHESTRATOR — Recalculates all personal derived metrics.

    Steps:
    1. Fetch raw data
    2. Aggregate personal totals
    3. Call pure calculation functions
    4. Compute health score
    5. Upsert personal_metrics row
    6. Trigger personal alert engine
    """
    # ── STEP 1: FETCH RAW DATA ──
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}

    bank_accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    credit_cards = db.query(CreditCard).filter(CreditCard.user_id == user_id).all()
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    tax_info = db.query(Tax).filter(Tax.user_id == user_id).first()
    cash_records = db.query(Cash).filter(Cash.user_id == user_id).all()

    # ── STEP 2: AGGREGATE PERSONAL TOTALS ──
    personal_bank = sum(
        (acc.balance or Decimal(0)) for acc in bank_accounts if acc.mode == "personal"
    )
    total_bank = sum((acc.balance or Decimal(0)) for acc in bank_accounts)

    # Personal cash
    personal_cash = sum(
        (c.amount or Decimal(0)) for c in cash_records if c.mode == "personal"
    )

    # Investment totals
    total_investments = sum((inv.value or Decimal(0)) for inv in investments)

    # Total assets (personal)
    total_assets = total_bank + personal_cash + total_investments

    # Loan totals
    total_loan_outstanding = sum((l.outstanding or Decimal(0)) for l in loans)
    total_emi = sum((l.emi or Decimal(0)) for l in loans)
    total_emi += sum((cc.emi or Decimal(0)) for cc in credit_cards)

    # Credit totals
    total_credit_used = sum((cc.credit_used or Decimal(0)) for cc in credit_cards)
    total_credit_limit = sum((cc.credit_limit or Decimal(0)) for cc in credit_cards)

    total_liabilities = total_loan_outstanding + total_credit_used

    # Monthly income/expenses
    monthly_income = user.monthly_income or Decimal(0)
    monthly_expenses = user.monthly_expenses or Decimal(0)
    other_income = user.other_monthly_income or Decimal(0)
    effective_income = monthly_income + other_income

    # ── STEP 3: PERSONAL CALCULATIONS ──
    net_worth = financial_calculations.calculate_net_worth(total_assets, total_liabilities)
    savings_ratio = financial_calculations.calculate_savings_ratio(effective_income, monthly_expenses)
    dti = financial_calculations.calculate_dti(total_emi, effective_income)
    emergency_fund = financial_calculations.calculate_emergency_fund(total_bank + personal_cash, monthly_expenses)
    credit_utilization = financial_calculations.calculate_credit_utilization(total_credit_used, total_credit_limit)
    liquid_pct = financial_calculations.calculate_liquid_asset_percentage(total_bank + personal_cash, total_assets)
    loan_to_asset = financial_calculations.calculate_loan_to_asset(total_loan_outstanding, total_assets)
    credit_score = financial_calculations.calculate_credit_score_simulation(credit_utilization, dti)
    cash_flow = financial_calculations.calculate_cash_flow_personal(effective_income, monthly_expenses, total_emi)

    # Tax calculation
    tax_estimate = Decimal(0)
    effective_tax_rate = Decimal(0)
    if tax_info:
        annual = tax_info.annual_income or (monthly_income * 12)
        if tax_info.regime == "old":
            tax_calc = financial_calculations.calculate_tax_old_regime(
                annual_income=annual,
                deductions_80c=tax_info.deductions_80c or Decimal(0),
                deductions_80d=tax_info.deductions_80d or Decimal(0),
                deductions_80tta=tax_info.deductions_80tta or Decimal(0),
                other_deductions=tax_info.other_deductions or Decimal(0),
            )
        else:
            tax_calc = financial_calculations.calculate_tax_new_regime(annual_income=annual)
        tax_estimate = Decimal(str(tax_calc["total_tax"]))
        effective_tax_rate = Decimal(str(tax_calc["effective_tax_rate"]))

    # Diversification
    diversification = {}
    if total_investments > 0:
        for inv in investments:
            d = financial_calculations.calculate_diversification_ratio(inv.value or Decimal(0), total_investments)
            diversification[inv.type] = d
    div_avg = (
        sum(diversification.values()) / len(diversification) if diversification else Decimal(50)
    )

    # ── STEP 4: HEALTH SCORE ──
    health_score = health_score_engine.calculate_health_score(
        savings_ratio=savings_ratio,
        dti=dti,
        emergency_fund=emergency_fund,
        credit_utilization=credit_utilization,
        diversification_avg=div_avg,
    )

    # ── STEP 5: UPSERT personal_metrics ──
    personal = db.query(PersonalMetrics).filter(PersonalMetrics.user_id == user_id).first()
    if not personal:
        personal = PersonalMetrics(user_id=user_id)
        db.add(personal)

    personal.net_worth = net_worth
    personal.savings_ratio = savings_ratio
    personal.dti = dti
    personal.emergency_fund = emergency_fund
    personal.credit_utilization = credit_utilization
    personal.liquid_asset_percentage = liquid_pct
    personal.loan_to_asset = loan_to_asset
    personal.tax_estimate = tax_estimate
    personal.effective_tax_rate = effective_tax_rate
    personal.credit_score_simulation = credit_score
    personal.health_score = health_score
    personal.cash_flow_monthly = cash_flow
    personal.cash_in_hand = personal_cash

    personal.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(personal)

    # ── STEP 6: TRIGGER PERSONAL ALERTS ──
    evaluate_personal_alerts(
        user_id=user_id,
        metrics=personal,
        db=db,
        user=user,
        tax_info=tax_info,
        loans=loans,
        credit_cards=credit_cards,
        investments=investments,
    )

    return {
        "success": True,
        "message": "Personal metrics recalculated",
        "health_score": float(health_score),
    }
