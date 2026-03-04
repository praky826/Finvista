"""
Account, Loan, Credit Card, Investment, Goal, Tax, Alert Schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ── Bank Account Schemas ──

class BankAccountCreate(BaseModel):
    bank_name: str = Field(..., max_length=100)
    account_type: str = Field(default="savings")  # savings | current | salary
    balance: float = Field(..., ge=0)
    mode: str = Field(default="personal")  # personal | business

class BankAccountUpdate(BaseModel):
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    balance: Optional[float] = Field(None, ge=0)

class BankAccountResponse(BaseModel):
    account_id: int
    bank_name: str
    account_type: str
    balance: float
    mode: str
    class Config:
        from_attributes = True


# ── Cash Schemas ──

class CashCreate(BaseModel):
    amount: float = Field(..., ge=0)
    mode: str = Field(default="personal")
    description: Optional[str] = None

class CashUpdate(BaseModel):
    amount: float = Field(..., ge=0)

class CashResponse(BaseModel):
    cash_id: int
    amount: float
    mode: str
    description: Optional[str] = None
    class Config:
        from_attributes = True


# ── Loan Schemas ──

class LoanCreate(BaseModel):
    loan_name: str = Field(..., max_length=100)
    loan_type: str = Field(default="personal")  # home | personal | business | education | other
    outstanding: float = Field(..., gt=0)
    emi: float = Field(..., ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=30)
    tenure_months: Optional[int] = Field(None, ge=0)
    mode: str = Field(default="personal")
    emi_day_of_month: Optional[int] = Field(None, ge=1, le=31)

class LoanUpdate(BaseModel):
    loan_name: Optional[str] = None
    outstanding: Optional[float] = Field(None, gt=0)
    emi: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = None
    emi_day_of_month: Optional[int] = None

class LoanResponse(BaseModel):
    loan_id: int
    loan_name: str
    loan_type: str
    outstanding: float
    emi: float
    interest_rate: Optional[float] = None
    tenure_months: Optional[int] = None
    mode: str
    next_emi_due_date: Optional[date] = None
    class Config:
        from_attributes = True


# ── Credit Card Schemas ──

class CreditCardCreate(BaseModel):
    card_name: str = Field(..., max_length=100)
    credit_limit: float = Field(..., gt=0)
    credit_used: float = Field(..., ge=0)
    emi: float = Field(default=0, ge=0)
    due_day_of_month: Optional[int] = Field(None, ge=1, le=31)

class CreditCardUpdate(BaseModel):
    card_name: Optional[str] = None
    credit_limit: Optional[float] = Field(None, gt=0)
    credit_used: Optional[float] = Field(None, ge=0)
    emi: Optional[float] = None

class CreditCardResponse(BaseModel):
    card_id: int
    card_name: str
    credit_limit: float
    credit_used: float
    emi: float
    next_due_date: Optional[date] = None
    class Config:
        from_attributes = True


# ── Investment Schemas ──

class InvestmentCreate(BaseModel):
    type: str  # fd | stock | mf | gold | property
    value: float = Field(..., gt=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=50)
    tenure_months: Optional[int] = None
    maturity_date: Optional[date] = None
    purchase_date: Optional[date] = None

class InvestmentUpdate(BaseModel):
    value: Optional[float] = Field(None, gt=0)
    interest_rate: Optional[float] = None
    maturity_date: Optional[date] = None

class InvestmentResponse(BaseModel):
    investment_id: int
    type: str
    value: float
    interest_rate: Optional[float] = None
    tenure_months: Optional[int] = None
    maturity_date: Optional[date] = None
    class Config:
        from_attributes = True


# ── Goal Schemas ──

class GoalCreate(BaseModel):
    goal_name: str = Field(..., max_length=150)
    target: float = Field(..., gt=0)
    deadline: date
    current_savings: float = Field(default=0, ge=0)
    mode: str = Field(default="personal")
    priority: str = Field(default="medium")  # low | medium | high

class GoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    target: Optional[float] = Field(None, gt=0)
    deadline: Optional[date] = None
    current_savings: Optional[float] = Field(None, ge=0)

class GoalResponse(BaseModel):
    goal_id: int
    goal_name: str
    target: float
    deadline: date
    current_savings: float
    mode: str
    priority: str
    class Config:
        from_attributes = True


# ── Tax Schemas ──

class TaxUpdate(BaseModel):
    annual_income: Optional[float] = None
    monthly_income: Optional[float] = None
    deductions_80c: Optional[float] = Field(None, ge=0, le=150000)
    deductions_80d: Optional[float] = Field(None, ge=0, le=25000)
    deductions_80tta: Optional[float] = Field(None, ge=0, le=10000)
    other_deductions: Optional[float] = Field(None, ge=0)
    regime: Optional[str] = None  # old | new
    business_revenue: Optional[float] = None
    business_expenses: Optional[float] = None
    cogs: Optional[float] = None
    business_deductions: Optional[float] = None
    corporate_tax_percent: Optional[float] = Field(None, ge=0, le=50)

class TaxResponse(BaseModel):
    tax_id: int
    regime: Optional[str] = None
    annual_income: Optional[float] = None
    deductions_80c: Optional[float] = 0
    deductions_80d: Optional[float] = 0
    deductions_80tta: Optional[float] = 0
    other_deductions: Optional[float] = 0
    business_revenue: Optional[float] = None
    business_expenses: Optional[float] = None
    cogs: Optional[float] = None
    corporate_tax_percent: Optional[float] = 30
    class Config:
        from_attributes = True

class TaxComparison(BaseModel):
    old_regime: dict
    new_regime: dict
    recommended: str
    savings: float


# ── Alert Schemas ──

class AlertResponse(BaseModel):
    alert_id: int
    alert_type: str
    severity: str
    message: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    status: str
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ── Dashboard Schema ──

class DashboardResponse(BaseModel):
    user_id: int
    account_type: str
    summary: dict
    alerts: List[AlertResponse] = []
    goals: List[dict] = []


# ── Business Schemas ──

class InventoryCreate(BaseModel):
    item_name: str = Field(..., max_length=150)
    quantity: float = Field(..., ge=0)
    unit_cost: float = Field(..., ge=0)

class InventoryResponse(BaseModel):
    inventory_id: int
    item_name: str
    quantity: float
    unit_cost: float
    current_value: float
    class Config:
        from_attributes = True

class ReceivableCreate(BaseModel):
    customer_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_amount: float = Field(..., gt=0)
    due_date: Optional[date] = None

class ReceivableResponse(BaseModel):
    receivable_id: int
    customer_name: Optional[str] = None
    invoice_amount: float
    due_date: Optional[date] = None
    status: str
    class Config:
        from_attributes = True

class PayableCreate(BaseModel):
    vendor_name: Optional[str] = None
    bill_number: Optional[str] = None
    bill_amount: float = Field(..., gt=0)
    due_date: Optional[date] = None

class PayableResponse(BaseModel):
    payable_id: int
    vendor_name: Optional[str] = None
    bill_amount: float
    due_date: Optional[date] = None
    status: str
    class Config:
        from_attributes = True


# ── Generic Response ──

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None
