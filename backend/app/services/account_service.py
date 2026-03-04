from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.bank_account import BankAccount
from app.models.cash import Cash
from app.schemas.finance_schemas import BankAccountCreate, BankAccountUpdate, CashCreate
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics

class AccountService:
    @staticmethod
    def _recalc(user_id: int, db: Session):
        recalculate_personal_metrics(user_id, db)
        recalculate_business_metrics(user_id, db)

    # ── Bank Accounts ──
    @staticmethod
    def get_accounts(user_id: int, db: Session):
        return db.query(BankAccount).filter(BankAccount.user_id == user_id).all()

    @staticmethod
    def create_account(user_id: int, body: BankAccountCreate, db: Session) -> BankAccount:
        acc = BankAccount(
            user_id=user_id,
            bank_name=body.bank_name,
            account_type=body.account_type,
            balance=Decimal(str(body.balance)),
            mode=body.mode
        )
        db.add(acc)
        db.commit()
        db.refresh(acc)
        AccountService._recalc(user_id, db)
        return acc

    @staticmethod
    def update_account(user_id: int, account_id: int, body: BankAccountUpdate, db: Session) -> BankAccount | None:
        acc = db.query(BankAccount).filter(BankAccount.account_id == account_id, BankAccount.user_id == user_id).first()
        if not acc:
            return None
            
        if body.bank_name is not None:
            acc.bank_name = body.bank_name
        if body.account_type is not None:
            acc.account_type = body.account_type
        if body.balance is not None:
            acc.balance = Decimal(str(body.balance))
            
        db.commit()
        AccountService._recalc(user_id, db)
        return acc

    @staticmethod
    def delete_account(user_id: int, account_id: int, db: Session) -> bool:
        acc = db.query(BankAccount).filter(BankAccount.account_id == account_id, BankAccount.user_id == user_id).first()
        if not acc:
            return False
            
        db.delete(acc)
        db.commit()
        AccountService._recalc(user_id, db)
        return True

    # ── Cash ──
    @staticmethod
    def get_cash_records(user_id: int, db: Session):
        return db.query(Cash).filter(Cash.user_id == user_id).all()

    @staticmethod
    def upsert_cash(user_id: int, body: CashCreate, db: Session) -> Cash:
        existing = db.query(Cash).filter(Cash.user_id == user_id, Cash.mode == body.mode).first()
        if existing:
            existing.amount = Decimal(str(body.amount))
            if body.description:
                existing.description = body.description
        else:
            existing = Cash(
                user_id=user_id, 
                amount=Decimal(str(body.amount)), 
                mode=body.mode, 
                description=body.description
            )
            db.add(existing)
            
        db.commit()
        AccountService._recalc(user_id, db)
        return existing

account_service = AccountService()
