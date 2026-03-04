from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.finance_schemas import (
    LoanCreate, LoanUpdate,
    CreditCardCreate, CreditCardUpdate
)
from app.security.auth_dependencies import get_current_user
from app.services.loan_service import loan_service

router = APIRouter(tags=["Finance - Loans & Credit Cards"])

# ═══════════════════════════════════════════
#  LOANS
# ═══════════════════════════════════════════

@router.get("/loans")
def list_loans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loans = loan_service.get_loans(current_user.user_id, db)
    return {"success": True, "data": [
        {"loan_id": l.loan_id, "loan_name": l.loan_name, "loan_type": l.loan_type,
         "outstanding": float(l.outstanding or 0), "emi": float(l.emi or 0),
         "interest_rate": float(l.interest_rate) if l.interest_rate else None,
         "tenure_months": l.tenure_months, "mode": l.mode}
        for l in loans
    ]}

@router.post("/loans", status_code=201)
def create_loan(body: LoanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = loan_service.create_loan(current_user.user_id, body, db)
    return {"success": True, "data": {"loan_id": loan.loan_id}, "message": "Loan added"}

@router.put("/loans/{loan_id}")
def update_loan(loan_id: int, body: LoanUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    loan = loan_service.update_loan(current_user.user_id, loan_id, body, db)
    if not loan:
        raise HTTPException(404, "Loan not found")
    return {"success": True, "message": "Loan updated"}

@router.delete("/loans/{loan_id}")
def delete_loan(loan_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = loan_service.delete_loan(current_user.user_id, loan_id, db)
    if not deleted:
        raise HTTPException(404, "Loan not found")
    return {"success": True, "message": "Loan deleted"}

# ═══════════════════════════════════════════
#  CREDIT CARDS
# ═══════════════════════════════════════════

@router.get("/credit-cards")
def list_credit_cards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cards = loan_service.get_credit_cards(current_user.user_id, db)
    return {"success": True, "data": [
        {"card_id": c.card_id, "card_name": c.card_name, "credit_limit": float(c.credit_limit or 0),
         "credit_used": float(c.credit_used or 0), "emi": float(c.emi or 0)}
        for c in cards
    ]}

@router.post("/credit-cards", status_code=201)
def create_credit_card(body: CreditCardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cc = loan_service.create_credit_card(current_user.user_id, body, db)
    return {"success": True, "data": {"card_id": cc.card_id}, "message": "Credit card added"}

@router.put("/credit-cards/{card_id}")
def update_credit_card(card_id: int, body: CreditCardUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cc = loan_service.update_credit_card(current_user.user_id, card_id, body, db)
    if not cc:
        raise HTTPException(404, "Credit card not found")
    return {"success": True, "message": "Credit card updated"}

@router.delete("/credit-cards/{card_id}")
def delete_credit_card(card_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = loan_service.delete_credit_card(current_user.user_id, card_id, db)
    if not deleted:
        raise HTTPException(404, "Credit card not found")
    return {"success": True, "message": "Credit card deleted"}
