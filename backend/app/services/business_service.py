from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.business_inventory import BusinessInventory
from app.models.business_receivables import BusinessReceivable
from app.models.business_payables import BusinessPayable
from app.schemas.finance_schemas import (
    InventoryCreate, ReceivableCreate, PayableCreate
)
from app.engines.business_recalculation_engine import recalculate_business_metrics

class BusinessService:
    @staticmethod
    def _recalc(user_id: int, db: Session):
        recalculate_business_metrics(user_id, db)

    # ── Inventory ──
    @staticmethod
    def get_inventory(user_id: int, db: Session):
        return db.query(BusinessInventory).filter(BusinessInventory.user_id == user_id).all()

    @staticmethod
    def create_inventory(user_id: int, body: InventoryCreate, db: Session) -> BusinessInventory:
        value = Decimal(str(body.quantity)) * Decimal(str(body.unit_cost))
        item = BusinessInventory(
            user_id=user_id,
            item_name=body.item_name,
            quantity=Decimal(str(body.quantity)),
            unit_cost=Decimal(str(body.unit_cost)),
            current_value=value
        )
        db.add(item)
        db.commit()
        BusinessService._recalc(user_id, db)
        return item

    # ── Receivables ──
    @staticmethod
    def get_receivables(user_id: int, db: Session):
        return db.query(BusinessReceivable).filter(BusinessReceivable.user_id == user_id).all()

    @staticmethod
    def create_receivable(user_id: int, body: ReceivableCreate, db: Session) -> BusinessReceivable:
        item = BusinessReceivable(
            user_id=user_id,
            customer_name=body.customer_name,
            invoice_number=body.invoice_number,
            invoice_amount=Decimal(str(body.invoice_amount)),
            due_date=body.due_date
        )
        db.add(item)
        db.commit()
        BusinessService._recalc(user_id, db)
        return item

    # ── Payables ──
    @staticmethod
    def get_payables(user_id: int, db: Session):
        return db.query(BusinessPayable).filter(BusinessPayable.user_id == user_id).all()

    @staticmethod
    def create_payable(user_id: int, body: PayableCreate, db: Session) -> BusinessPayable:
        item = BusinessPayable(
            user_id=user_id,
            vendor_name=body.vendor_name,
            bill_number=body.bill_number,
            bill_amount=Decimal(str(body.bill_amount)),
            due_date=body.due_date
        )
        db.add(item)
        db.commit()
        BusinessService._recalc(user_id, db)
        return item

business_service = BusinessService()
