from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.finance_schemas import (
    InventoryCreate, ReceivableCreate, PayableCreate
)
from app.security.auth_dependencies import get_current_user
from app.services.business_service import business_service

router = APIRouter(tags=["Finance - Business Modules"])

# ═══════════════════════════════════════════
#  BUSINESS: Inventory, Receivables, Payables
# ═══════════════════════════════════════════

@router.get("/business/inventory")
def list_inventory(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = business_service.get_inventory(current_user.user_id, db)
    return {"success": True, "data": [
        {"inventory_id": i.inventory_id, "item_name": i.item_name, "quantity": float(i.quantity),
         "unit_cost": float(i.unit_cost), "current_value": float(i.current_value)}
        for i in items
    ]}

@router.post("/business/inventory", status_code=201)
def create_inventory(body: InventoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = business_service.create_inventory(current_user.user_id, body, db)
    return {"success": True, "data": {"inventory_id": item.inventory_id}, "message": "Inventory added"}

@router.get("/business/receivables")
def list_receivables(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = business_service.get_receivables(current_user.user_id, db)
    return {"success": True, "data": [
        {"receivable_id": r.receivable_id, "customer_name": r.customer_name,
         "invoice_amount": float(r.invoice_amount), "due_date": r.due_date.isoformat() if r.due_date else None, "status": r.status}
        for r in items
    ]}

@router.post("/business/receivables", status_code=201)
def create_receivable(body: ReceivableCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = business_service.create_receivable(current_user.user_id, body, db)
    return {"success": True, "message": "Receivable added"}

@router.get("/business/payables")
def list_payables(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = business_service.get_payables(current_user.user_id, db)
    return {"success": True, "data": [
        {"payable_id": p.payable_id, "vendor_name": p.vendor_name,
         "bill_amount": float(p.bill_amount), "due_date": p.due_date.isoformat() if p.due_date else None, "status": p.status}
        for p in items
    ]}

@router.post("/business/payables", status_code=201)
def create_payable(body: PayableCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = business_service.create_payable(current_user.user_id, body, db)
    return {"success": True, "message": "Payable added"}
