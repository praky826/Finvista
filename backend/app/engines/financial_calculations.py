"""
Financial Calculations Engine — 30+ Pure Functions
NO database access. NO I/O. Receives data → Returns computed values.

All money values use Decimal for precision.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


# ═══════════════════════════════════════════════════════════
#  PERSONAL FINANCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def calculate_net_worth(total_assets: Decimal, total_liabilities: Decimal) -> Decimal:
    """Net Worth = Total Assets - Total Liabilities"""
    return total_assets - total_liabilities


def calculate_liquid_asset_percentage(liquid_assets: Decimal, total_assets: Decimal) -> Decimal:
    """Liquid Assets % = (Liquid Assets / Total Assets) × 100"""
    if total_assets == 0:
        return Decimal(0)
    return ((liquid_assets / total_assets) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_savings_ratio(monthly_income: Decimal, monthly_expenses: Decimal) -> Decimal:
    """
    Savings Ratio = ((Income - Expenses) / Income) × 100
    >30% Excellent | 20-30% Good | 10-20% Average | <10% Poor
    """
    if monthly_income == 0:
        return Decimal(0)
    return (((monthly_income - monthly_expenses) / monthly_income) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_emergency_fund(liquid_savings: Decimal, monthly_expenses: Decimal) -> Decimal:
    """
    Emergency Fund Coverage (months) = Liquid Savings / Monthly Expenses
    <3 months CRITICAL | 3-6 At Risk | 6+ Healthy
    """
    if monthly_expenses == 0:
        return Decimal(0)
    return (liquid_savings / monthly_expenses).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_dti(total_monthly_emi: Decimal, monthly_income: Decimal) -> Decimal:
    """
    Debt-to-Income Ratio = (Total Monthly EMI / Monthly Income) × 100
    <30% Healthy | 30-40% Caution | >40% CRITICAL
    """
    if monthly_income == 0:
        return Decimal(0)
    ratio = ((total_monthly_emi / monthly_income) * 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return min(ratio, Decimal("9999.99"))


def calculate_emi_burden_ratio(total_monthly_emi: Decimal, monthly_income: Decimal) -> Decimal:
    """EMI Burden = Total EMI / Monthly Income × 100 (same as DTI, named for clarity)"""
    return calculate_dti(total_monthly_emi, monthly_income)


def calculate_loan_to_asset(total_loan_outstanding: Decimal, total_assets: Decimal) -> Decimal:
    """
    Loan-to-Asset Ratio = Total Loan Outstanding / Total Assets
    <0.3 Good | 0.3-0.6 Moderate | >0.6 High risk
    """
    if total_assets == 0:
        return Decimal(0)
    ratio = (total_loan_outstanding / total_assets).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return min(ratio, Decimal("9999.99"))


def calculate_credit_utilization(credit_used: Decimal, credit_limit: Decimal) -> Decimal:
    """
    Credit Utilization = (Credit Used / Credit Limit) × 100
    <30% Good | 30-50% Caution | >50% High risk
    """
    if credit_limit == 0:
        return Decimal(0)
    ratio = ((credit_used / credit_limit) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return min(ratio, Decimal("9999.99"))


def calculate_credit_score_simulation(
    credit_utilization: Decimal,
    dti: Decimal,
    payment_history_score: Decimal = Decimal(100),
) -> int:
    """
    Simulated Credit Score — Base 750.
    Deduct for high utilization (>30%) and high DTI (>40%).
    Bonus for low EMI burden. Range: 600-900.
    """
    score = 750

    if credit_utilization > 30:
        score -= min(50, int(credit_utilization / 2))
    if dti > 40:
        score -= min(100, int((dti - 40) * 2))

    score += int((payment_history_score - 100) / 2)  # -50 to +50 range

    return max(600, min(900, score))


# ── Investment & FD Metrics ──

def calculate_fd_maturity(
    principal: Decimal, annual_interest_rate: Decimal, tenure_years: Decimal
) -> Decimal:
    """FD Maturity = Principal × (1 + Rate/100)^Years (annual compounding)"""
    rate = annual_interest_rate / 100
    return (principal * ((1 + rate) ** tenure_years)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_diversification_ratio(asset_value: Decimal, total_investment: Decimal) -> Decimal:
    """Diversification % for one asset type = (Asset Value / Total Investment) × 100"""
    if total_investment == 0:
        return Decimal(0)
    return ((asset_value / total_investment) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_expected_annual_return(
    investment_value: Decimal, expected_return_rate: Decimal
) -> Decimal:
    """Expected Annual Return = Investment Value × (Expected Rate / 100)"""
    return (investment_value * (expected_return_rate / 100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_cash_flow_personal(
    monthly_income: Decimal, monthly_expenses: Decimal, total_emi: Decimal
) -> Decimal:
    """Personal Cash Flow = Income - Expenses - EMI"""
    return monthly_income - monthly_expenses - total_emi


# ── Goal Tracking ──

def calculate_goal_feasibility(
    target_amount: Decimal,
    current_savings: Decimal,
    available_monthly_savings: Decimal,
    months_remaining: int,
) -> dict:
    """
    Goal Feasibility (Personal):
    Required Monthly = (Target - Current) / Months Remaining
    Feasibility Ratio = Available Monthly / Required Monthly
    ≥1.0 On Track | 0.5-1.0 Behind | <0.5 Far Behind
    """
    if months_remaining <= 0:
        return {"status": "overdue", "feasibility_ratio": Decimal(0), "required_monthly": Decimal(0)}

    remaining = target_amount - current_savings
    required_monthly = remaining / months_remaining if remaining > 0 else Decimal(0)

    if required_monthly == 0:
        ratio = Decimal(1)
    else:
        ratio = available_monthly_savings / required_monthly

    if ratio >= 1:
        status = "on_track"
    elif ratio >= Decimal("0.5"):
        status = "behind"
    else:
        status = "far_behind"

    return {
        "target_amount": float(target_amount),
        "current_savings": float(current_savings),
        "required_monthly": float(required_monthly.quantize(Decimal("0.01"))),
        "available_monthly": float(available_monthly_savings),
        "feasibility_ratio": float(ratio.quantize(Decimal("0.01"))),
        "status": status,
        "months_remaining": months_remaining,
        "total_needed": float(remaining),
    }


# ═══════════════════════════════════════════════════════════
#  TAX FUNCTIONS (India)
# ═══════════════════════════════════════════════════════════

def calculate_tax_old_regime(
    annual_income: Decimal,
    deductions_80c: Decimal = Decimal(0),
    deductions_80d: Decimal = Decimal(0),
    deductions_80tta: Decimal = Decimal(0),
    other_deductions: Decimal = Decimal(0),
) -> dict:
    """
    OLD REGIME (FY 2023-24):
    Slabs: ₹0-2.5L(0%), 2.5-5L(5%), 5-10L(10%), 10-15L(20%), 15L+(30%)
    + Standard Deduction ₹50,000
    + 4% Health & Education Cess
    """
    gross = annual_income
    std_ded = Decimal(50000)

    # Cap deductions per Indian tax rules
    d80c = min(deductions_80c, Decimal(150000))
    d80d = min(deductions_80d, Decimal(25000))
    d80tta = min(deductions_80tta, Decimal(10000))

    total_ded = d80c + d80d + d80tta + other_deductions
    taxable = max(gross - std_ded - total_ded, Decimal(0))

    # Slab computation
    if taxable <= 250000:
        tax = Decimal(0)
    elif taxable <= 500000:
        tax = (taxable - 250000) * Decimal("0.05")
    elif taxable <= 1000000:
        tax = Decimal(250000) * Decimal("0.05") + (taxable - 500000) * Decimal("0.10")
    elif taxable <= 1500000:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(500000) * Decimal("0.10")
            + (taxable - 1000000) * Decimal("0.20")
        )
    else:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(500000) * Decimal("0.10")
            + Decimal(500000) * Decimal("0.20")
            + (taxable - 1500000) * Decimal("0.30")
        )

    cess = tax * Decimal("0.04")
    total_tax = (tax + cess).quantize(Decimal("0.01"))
    eff_rate = (total_tax / gross * 100).quantize(Decimal("0.01")) if gross > 0 else Decimal(0)

    return {
        "gross_income": float(gross),
        "standard_deduction": float(std_ded),
        "total_deductions": float(total_ded),
        "taxable_income": float(taxable),
        "tax_before_cess": float(tax.quantize(Decimal("0.01"))),
        "cess": float(cess.quantize(Decimal("0.01"))),
        "total_tax": float(total_tax),
        "effective_tax_rate": float(eff_rate),
        "net_income": float(gross - total_tax),
    }


def calculate_tax_new_regime(
    annual_income: Decimal, standard_deduction: Decimal = Decimal(50000)
) -> dict:
    """
    NEW REGIME (FY 2023-24):
    Slabs: ₹0-2.5L(0%), 2.5-5L(5%), 5-7.5L(10%), 7.5-10L(15%),
           10-12.5L(20%), 12.5-15L(25%), 15L+(30%)
    Section 87A rebate: tax = ₹0 if income ≤ ₹5L
    """
    gross = annual_income
    taxable = max(gross - standard_deduction, Decimal(0))

    if taxable <= 250000:
        tax = Decimal(0)
    elif taxable <= 500000:
        tax = (taxable - 250000) * Decimal("0.05")
    elif taxable <= 750000:
        tax = Decimal(250000) * Decimal("0.05") + (taxable - 500000) * Decimal("0.10")
    elif taxable <= 1000000:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(250000) * Decimal("0.10")
            + (taxable - 750000) * Decimal("0.15")
        )
    elif taxable <= 1250000:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(250000) * Decimal("0.10")
            + Decimal(250000) * Decimal("0.15")
            + (taxable - 1000000) * Decimal("0.20")
        )
    elif taxable <= 1500000:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(250000) * Decimal("0.10")
            + Decimal(250000) * Decimal("0.15")
            + Decimal(250000) * Decimal("0.20")
            + (taxable - 1250000) * Decimal("0.25")
        )
    else:
        tax = (
            Decimal(250000) * Decimal("0.05")
            + Decimal(250000) * Decimal("0.10")
            + Decimal(250000) * Decimal("0.15")
            + Decimal(250000) * Decimal("0.20")
            + Decimal(250000) * Decimal("0.25")
            + (taxable - 1500000) * Decimal("0.30")
        )

    cess = tax * Decimal("0.04")
    total_before_rebate = tax + cess

    # Section 87A rebate
    if gross <= 500000:
        total_tax = Decimal(0)
        rebate = total_before_rebate
    else:
        total_tax = total_before_rebate
        rebate = Decimal(0)

    total_tax = total_tax.quantize(Decimal("0.01"))
    eff_rate = (total_tax / gross * 100).quantize(Decimal("0.01")) if gross > 0 else Decimal(0)

    return {
        "gross_income": float(gross),
        "standard_deduction": float(standard_deduction),
        "taxable_income": float(taxable),
        "tax_before_cess": float(tax.quantize(Decimal("0.01"))),
        "cess": float(cess.quantize(Decimal("0.01"))),
        "total_tax_before_rebate": float(total_before_rebate.quantize(Decimal("0.01"))),
        "section_87a_rebate": float(rebate.quantize(Decimal("0.01"))),
        "total_tax": float(total_tax),
        "effective_tax_rate": float(eff_rate),
        "net_income": float(gross - total_tax),
    }


# ═══════════════════════════════════════════════════════════
#  BUSINESS FINANCE FUNCTIONS
# ═══════════════════════════════════════════════════════════

def calculate_net_profit(
    revenue: Decimal,
    operating_expenses: Decimal,
    cogs: Decimal = Decimal(0),
    interest_paid: Decimal = Decimal(0),
    tax_paid: Decimal = Decimal(0),
) -> Decimal:
    """Net Profit = Revenue - COGS - Operating Expenses - Interest - Taxes"""
    return revenue - cogs - operating_expenses - interest_paid - tax_paid


def calculate_working_capital(
    current_assets: Decimal, current_liabilities: Decimal
) -> Decimal:
    """Working Capital = Current Assets - Current Liabilities"""
    return current_assets - current_liabilities


def calculate_liquidity_ratio(
    current_assets: Decimal, current_liabilities: Decimal
) -> Decimal:
    """
    Liquidity Ratio = Current Assets / Current Liabilities
    >1.5 Excellent | 1.0-1.5 Healthy | <1.0 CRITICAL
    """
    if current_liabilities == 0:
        return Decimal(0)
    ratio = (current_assets / current_liabilities).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return min(ratio, Decimal("9999.99"))


def calculate_debt_ratio(total_debt: Decimal, total_assets: Decimal) -> Decimal:
    """
    Debt Ratio = (Total Debt / Total Assets) × 100
    <40% Conservative | 40-60% Moderate | >60% CRITICAL
    """
    if total_assets == 0:
        return Decimal(0)
    ratio = ((total_debt / total_assets) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return min(ratio, Decimal("9999.99"))


def calculate_profit_margins(
    revenue: Decimal, cogs: Decimal, net_profit: Decimal
) -> dict:
    """
    Gross Margin = (Revenue - COGS) / Revenue × 100
    Net Margin = Net Profit / Revenue × 100
    """
    if revenue == 0:
        return {"gross_margin": 0.0, "net_margin": 0.0, "gross_profit": 0.0}

    gross_profit = revenue - cogs
    return {
        "gross_margin": float(((gross_profit / revenue) * 100).quantize(Decimal("0.01"))),
        "net_margin": float(((net_profit / revenue) * 100).quantize(Decimal("0.01"))),
        "gross_profit": float(gross_profit),
    }


def calculate_cash_flow_business(
    revenue: Decimal, operating_expenses: Decimal, total_emi: Decimal
) -> Decimal:
    """Business Cash Flow = Revenue - Expenses - EMI"""
    return revenue - operating_expenses - total_emi


def calculate_business_goal_feasibility(
    target_amount: Decimal,
    current_savings: Decimal,
    monthly_net_profit: Decimal,
    months_remaining: int,
) -> dict:
    """
    Business Goal Feasibility (uses net profit instead of savings):
    Feasibility Ratio = Monthly Net Profit / Required Monthly Allocation
    ≥1.0 Feasible | 0.5-1.0 Tight | <0.5 Unrealistic
    """
    if months_remaining <= 0:
        return {"status": "overdue", "feasibility_ratio": Decimal(0), "required_monthly": Decimal(0)}

    remaining = target_amount - current_savings
    required_monthly = remaining / months_remaining if remaining > 0 else Decimal(0)

    if required_monthly == 0:
        ratio = Decimal(1)
    else:
        ratio = monthly_net_profit / required_monthly

    if ratio >= 1:
        status = "feasible"
    elif ratio >= Decimal("0.5"):
        status = "tight"
    else:
        status = "unrealistic"

    return {
        "target_amount": float(target_amount),
        "current_savings": float(current_savings),
        "required_monthly": float(required_monthly.quantize(Decimal("0.01"))),
        "monthly_net_profit": float(monthly_net_profit),
        "feasibility_ratio": float(ratio.quantize(Decimal("0.01"))),
        "status": status,
        "months_remaining": months_remaining,
        "total_needed": float(remaining),
    }


def calculate_business_tax(
    revenue: Decimal,
    business_expenses: Decimal,
    cogs: Decimal = Decimal(0),
    business_deductions: Decimal = Decimal(0),
    corporate_tax_rate: Decimal = Decimal(30),
) -> dict:
    """
    Business Tax:
    Taxable Profit = Revenue - COGS - Expenses - Deductions
    Tax = Taxable Profit × Corporate Tax Rate
    Quarterly Advance Tax = Annual Tax / 4
    """
    taxable = max(revenue - cogs - business_expenses - business_deductions, Decimal(0))
    annual_tax = (taxable * (corporate_tax_rate / 100)).quantize(Decimal("0.01"))
    quarterly = (annual_tax / 4).quantize(Decimal("0.01"))
    eff_rate = (annual_tax / revenue * 100).quantize(Decimal("0.01")) if revenue > 0 else Decimal(0)

    return {
        "revenue": float(revenue),
        "expenses": float(business_expenses),
        "cogs": float(cogs),
        "deductions": float(business_deductions),
        "taxable_profit": float(taxable),
        "corporate_tax_rate": float(corporate_tax_rate),
        "annual_tax": float(annual_tax),
        "quarterly_advance_tax": float(quarterly),
        "effective_tax_rate": float(eff_rate),
        "net_profit_after_tax": float(taxable - annual_tax),
    }


def calculate_loan_eligibility(
    monthly_income: Decimal,
    existing_emi: Decimal,
    max_dti_percent: Decimal = Decimal(40),
) -> dict:
    """
    V3: Loan Eligibility Estimation
    Max affordable EMI = (Income × max_DTI%) - Existing EMI
    """
    max_total_emi = monthly_income * (max_dti_percent / 100)
    max_new_emi = max(max_total_emi - existing_emi, Decimal(0))

    return {
        "monthly_income": float(monthly_income),
        "existing_emi": float(existing_emi),
        "max_dti_percent": float(max_dti_percent),
        "max_total_emi": float(max_total_emi.quantize(Decimal("0.01"))),
        "max_new_emi": float(max_new_emi.quantize(Decimal("0.01"))),
        "eligible": max_new_emi > 0,
    }
