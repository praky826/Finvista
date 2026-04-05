"""
Business Recalculation Engine — Handles ONLY business finance metrics.
Fetches business data → Aggregates → Calculates → Upserts BusinessMetrics → Triggers business alerts.
Called by services whenever business financial data changes.
"""
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.bank_account import BankAccount
from app.models.loan import Loan
from app.models.tax import Tax
from app.models.business_metrics import BusinessMetrics
from app.models.cash import Cash
from app.models.business_inventory import BusinessInventory
from app.models.business_receivables import BusinessReceivable
from app.models.business_payables import BusinessPayable
from app.models.asset import Asset
from app.models.investment import Investment
from app.engines import financial_calculations
from app.engines.alert_engine import evaluate_business_alerts


def recalculate_business_metrics(user_id: int, db: Session) -> dict:
    """
    BUSINESS ORCHESTRATOR — Recalculates all business derived metrics.

    Steps:
    1. Fetch raw data
    2. Aggregate business totals
    3. Call pure calculation functions
    4. Upsert business_metrics row
    5. Trigger business alert engine
    """
    # ── STEP 1: FETCH RAW DATA ──
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}

    # Only run for business or both account types
    if user.account_type not in ("business", "both"):
        return {"success": True, "message": "Not a business account, skipped"}

    bank_accounts = db.query(BankAccount).filter(BankAccount.user_id == user_id).all()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    tax_info = db.query(Tax).filter(Tax.user_id == user_id).first()
    cash_records = db.query(Cash).filter(Cash.user_id == user_id).all()

    if not tax_info:
        return {"success": True, "message": "No tax info found, skipped business metrics"}

    revenue = tax_info.business_revenue or Decimal(0)
    expenses = tax_info.business_expenses or Decimal(0)
    cogs = tax_info.cogs or Decimal(0)

    if revenue <= 0:
        return {"success": True, "message": "No business revenue, skipped business metrics"}

    # ── STEP 2: AGGREGATE BUSINESS TOTALS ──
    business_bank = sum(
        (acc.balance or Decimal(0)) for acc in bank_accounts if acc.mode == "business"
    )
    business_cash = sum(
        (c.amount or Decimal(0)) for c in cash_records if c.mode == "business"
    )
    business_loans = [l for l in loans if l.mode == "business"]
    total_emi = sum((l.emi or Decimal(0)) for l in loans)

    # Business inventory / receivables / payables
    inventory_items = db.query(BusinessInventory).filter(BusinessInventory.user_id == user_id).all()
    receivables = db.query(BusinessReceivable).filter(
        BusinessReceivable.user_id == user_id, BusinessReceivable.status == "pending"
    ).all()
    payables = db.query(BusinessPayable).filter(
        BusinessPayable.user_id == user_id, BusinessPayable.status == "pending"
    ).all()

    total_inventory = sum((i.current_value or Decimal(0)) for i in inventory_items)
    total_receivables = sum((r.invoice_amount or Decimal(0)) for r in receivables)
    total_payables = sum((p.bill_amount or Decimal(0)) for p in payables)

    biz_tax_calc = financial_calculations.calculate_business_tax(revenue, expenses, cogs)
    biz_tax_paid = Decimal(str(biz_tax_calc["annual_tax"]))
    biz_net_profit = financial_calculations.calculate_net_profit(revenue, expenses, cogs, tax_paid=biz_tax_paid)

    current_assets = business_bank + business_cash + total_inventory + total_receivables
    current_liabilities = total_payables + sum(
        (l.outstanding or Decimal(0)) for l in business_loans
    )

    # Add Fixed Assets & Investments to Net Worth
    assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    
    total_custom_assets = sum((a.value or Decimal(0)) for a in assets)
    total_investments = sum((i.value or Decimal(0)) for i in investments)
    
    total_assets = current_assets + total_custom_assets + total_investments

    biz_working_capital = financial_calculations.calculate_working_capital(current_assets, current_liabilities)
    biz_liquidity = financial_calculations.calculate_liquidity_ratio(current_assets, max(current_liabilities, Decimal(1)))

    biz_debt_ratio = financial_calculations.calculate_debt_ratio(
        current_liabilities,
        total_assets if total_assets > 0 else Decimal(1),
    )

    margins = financial_calculations.calculate_profit_margins(revenue, cogs, biz_net_profit)
    biz_gross_margin = Decimal(str(margins["gross_margin"]))
    biz_net_margin = Decimal(str(margins["net_margin"]))

    biz_emi_burden = financial_calculations.calculate_emi_burden_ratio(
        sum((l.emi or Decimal(0)) for l in business_loans), revenue
    )
    biz_cash_flow = financial_calculations.calculate_cash_flow_business(revenue, expenses, total_emi)

    biz_net_worth = financial_calculations.calculate_net_worth(
        total_assets,
        (total_payables + sum((l.outstanding or Decimal(0)) for l in business_loans)),
    )

    # ── STEP 4: UPSERT business_metrics ──
    business = db.query(BusinessMetrics).filter(BusinessMetrics.user_id == user_id).first()
    if not business:
        business = BusinessMetrics(user_id=user_id)
        db.add(business)

    business.business_net_worth = biz_net_worth
    business.net_profit = biz_net_profit
    business.working_capital = biz_working_capital
    business.cash_flow = biz_cash_flow
    business.liquidity_ratio = biz_liquidity
    business.debt_ratio = biz_debt_ratio
    business.gross_profit_margin = biz_gross_margin
    business.net_profit_margin = biz_net_margin
    business.emi_burden_ratio = biz_emi_burden
    business.total_inventory_value = total_inventory
    business.total_receivables = total_receivables
    business.total_payables = total_payables
    business.cash_in_hand = business_cash

    business.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(business)

    # ── STEP 5: TRIGGER BUSINESS ALERTS ──
    evaluate_business_alerts(
        user_id=user_id,
        metrics=business,
        db=db,
        tax_info=tax_info,
        loans=business_loans,
    )

    return {
        "success": True,
        "message": "Business metrics recalculated",
    }
