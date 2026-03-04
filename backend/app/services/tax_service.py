from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tax import Tax
from app.schemas.finance_schemas import TaxUpdate
from app.schemas.user_schema import UpdateIncomeRequest
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics

class TaxService:
    @staticmethod
    def _recalc(user_id: int, db: Session):
        recalculate_personal_metrics(user_id, db)
        recalculate_business_metrics(user_id, db)

    # ── Income ──
    @staticmethod
    def update_income(user_id: int, body: UpdateIncomeRequest, db: Session) -> User | None:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
            
        if body.monthly_income is not None:
            user.monthly_income = Decimal(str(body.monthly_income))
        if body.monthly_expenses is not None:
            user.monthly_expenses = Decimal(str(body.monthly_expenses))
        if body.other_monthly_income is not None:
            user.other_monthly_income = Decimal(str(body.other_monthly_income))
            
        db.commit()
        TaxService._recalc(user_id, db)
        return user

    # ── Tax ──
    @staticmethod
    def get_tax(user_id: int, db: Session):
        return db.query(Tax).filter(Tax.user_id == user_id).first()

    @staticmethod
    def update_tax(user_id: int, body: TaxUpdate, db: Session) -> Tax:
        tax = db.query(Tax).filter(Tax.user_id == user_id).first()
        if not tax:
            tax = Tax(user_id=user_id)
            db.add(tax)
            
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(tax, k, Decimal(str(v)) if isinstance(v, (int, float)) else v)
            
        db.commit()
        TaxService._recalc(user_id, db)
        return tax

tax_service = TaxService()
