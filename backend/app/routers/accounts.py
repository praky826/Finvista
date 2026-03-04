from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.finance_schemas import (
    BankAccountCreate, BankAccountUpdate,
    CashCreate
)
from app.security.auth_dependencies import get_current_user
from app.services.account_service import account_service

router = APIRouter(tags=["Finance - Accounts & Cash"])

# ═══════════════════════════════════════════
#  BANK ACCOUNTS
# ═══════════════════════════════════════════

@router.get("/accounts")
def list_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = account_service.get_accounts(current_user.user_id, db)
    return {
        "success": True,
        "data": {
            "accounts": [
                {"account_id": a.account_id, "bank_name": a.bank_name, "account_type": a.account_type,
                 "balance": float(a.balance or 0), "mode": a.mode}
                for a in accounts
            ],
            "total_balance": sum(float(a.balance or 0) for a in accounts),
        },
    }

@router.post("/accounts", status_code=201)
def create_account(body: BankAccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = account_service.create_account(current_user.user_id, body, db)
    return {"success": True, "data": {"account_id": acc.account_id}, "message": "Account created"}

@router.put("/accounts/{account_id}")
def update_account(account_id: int, body: BankAccountUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated = account_service.update_account(current_user.user_id, account_id, body, db)
    if not updated:
        raise HTTPException(404, "Account not found")
    return {"success": True, "message": "Account updated"}

@router.delete("/accounts/{account_id}")
def delete_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = account_service.delete_account(current_user.user_id, account_id, db)
    if not deleted:
        raise HTTPException(404, "Account not found")
    return {"success": True, "message": "Account deleted"}

# ═══════════════════════════════════════════
#  CASH
# ═══════════════════════════════════════════

@router.get("/cash")
def list_cash(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = account_service.get_cash_records(current_user.user_id, db)
    return {"success": True, "data": [{"cash_id": c.cash_id, "amount": float(c.amount or 0), "mode": c.mode} for c in records]}

@router.post("/cash", status_code=201)
def upsert_cash(body: CashCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account_service.upsert_cash(current_user.user_id, body, db)
    return {"success": True, "message": "Cash updated"}
