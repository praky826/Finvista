from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.finance_schemas import TaxUpdate
from app.schemas.user_schema import UpdateIncomeRequest
from app.security.auth_dependencies import get_current_user
from app.services.tax_service import tax_service
from app.engines import financial_calculations

router = APIRouter(tags=["Finance - Tax & Income"])

# ═══════════════════════════════════════════
#  INCOME / EXPENSES
# ═══════════════════════════════════════════

@router.put("/income")
def update_income(
    request: UpdateIncomeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update monthly income and expenses."""
    user = tax_service.update_income(current_user.user_id, request, db)
    if not user:
        raise HTTPException(404, "User not found")
    return {"success": True, "message": "Income updated and metrics recalculated"}

# ═══════════════════════════════════════════
#  TAX
# ═══════════════════════════════════════════

@router.get("/tax")
def get_tax(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tax = tax_service.get_tax(current_user.user_id, db)
    if not tax:
        raise HTTPException(404, "Tax record not found")
    return {"success": True, "data": {
        "regime": tax.regime, "annual_income": float(tax.annual_income or 0),
        "deductions_80c": float(tax.deductions_80c or 0), "deductions_80d": float(tax.deductions_80d or 0),
        "deductions_80tta": float(tax.deductions_80tta or 0), "other_deductions": float(tax.other_deductions or 0),
        "business_revenue": float(tax.business_revenue or 0), "business_expenses": float(tax.business_expenses or 0),
        "cogs": float(tax.cogs or 0), "corporate_tax_percent": float(tax.corporate_tax_percent or 30),
    }}

@router.put("/tax")
def update_tax(body: TaxUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tax_service.update_tax(current_user.user_id, body, db)
    return {"success": True, "message": "Tax updated"}

@router.get("/tax/comparison")
def tax_comparison(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Compare Old vs New regime tax for current income."""
    tax = tax_service.get_tax(current_user.user_id, db)
    annual = Decimal(str(tax.annual_income or 0)) if tax else (current_user.monthly_income or Decimal(0)) * 12

    old = financial_calculations.calculate_tax_old_regime(
        annual, Decimal(str(tax.deductions_80c or 0)) if tax else Decimal(0),
        Decimal(str(tax.deductions_80d or 0)) if tax else Decimal(0),
        Decimal(str(tax.deductions_80tta or 0)) if tax else Decimal(0),
        Decimal(str(tax.other_deductions or 0)) if tax else Decimal(0),
    )
    new = financial_calculations.calculate_tax_new_regime(annual)

    savings = old["total_tax"] - new["total_tax"]
    recommended = "new" if new["total_tax"] <= old["total_tax"] else "old"

    return {"success": True, "data": {
        "old_regime": old, "new_regime": new, "recommended": recommended,
        "savings_with_recommended": abs(savings),
    }}
