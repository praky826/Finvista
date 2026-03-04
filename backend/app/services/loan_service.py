from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.loan import Loan
from app.models.credit_card import CreditCard
from app.schemas.finance_schemas import LoanCreate, LoanUpdate, CreditCardCreate, CreditCardUpdate
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics

class LoanService:
    @staticmethod
    def _recalc(user_id: int, db: Session):
        recalculate_personal_metrics(user_id, db)
        recalculate_business_metrics(user_id, db)

    # ── Loans ──
    @staticmethod
    def get_loans(user_id: int, db: Session):
        return db.query(Loan).filter(Loan.user_id == user_id).all()

    @staticmethod
    def create_loan(user_id: int, body: LoanCreate, db: Session) -> Loan:
        loan = Loan(
            user_id=user_id,
            loan_name=body.loan_name,
            loan_type=body.loan_type,
            outstanding=Decimal(str(body.outstanding)),
            emi=Decimal(str(body.emi)),
            interest_rate=Decimal(str(body.interest_rate)) if body.interest_rate else None,
            tenure_months=body.tenure_months,
            mode=body.mode,
            emi_day_of_month=body.emi_day_of_month
        )
        db.add(loan)
        db.commit()
        LoanService._recalc(user_id, db)
        return loan

    @staticmethod
    def update_loan(user_id: int, loan_id: int, body: LoanUpdate, db: Session) -> Loan | None:
        loan = db.query(Loan).filter(Loan.loan_id == loan_id, Loan.user_id == user_id).first()
        if not loan:
            return None
            
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(loan, k, Decimal(str(v)) if isinstance(v, (int, float)) and k != "emi_day_of_month" else v)
            
        db.commit()
        LoanService._recalc(user_id, db)
        return loan

    @staticmethod
    def delete_loan(user_id: int, loan_id: int, db: Session) -> bool:
        loan = db.query(Loan).filter(Loan.loan_id == loan_id, Loan.user_id == user_id).first()
        if not loan:
            return False
            
        db.delete(loan)
        db.commit()
        LoanService._recalc(user_id, db)
        return True

    # ── Credit Cards ──
    @staticmethod
    def get_credit_cards(user_id: int, db: Session):
        return db.query(CreditCard).filter(CreditCard.user_id == user_id).all()

    @staticmethod
    def create_credit_card(user_id: int, body: CreditCardCreate, db: Session) -> CreditCard:
        cc = CreditCard(
            user_id=user_id,
            card_name=body.card_name,
            credit_limit=Decimal(str(body.credit_limit)),
            credit_used=Decimal(str(body.credit_used)),
            emi=Decimal(str(body.emi)),
            due_day_of_month=body.due_day_of_month
        )
        db.add(cc)
        db.commit()
        LoanService._recalc(user_id, db)
        return cc

    @staticmethod
    def update_credit_card(user_id: int, card_id: int, body: CreditCardUpdate, db: Session) -> CreditCard | None:
        cc = db.query(CreditCard).filter(CreditCard.card_id == card_id, CreditCard.user_id == user_id).first()
        if not cc:
            return None
            
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(cc, k, Decimal(str(v)) if isinstance(v, (int, float)) else v)
            
        db.commit()
        LoanService._recalc(user_id, db)
        return cc

    @staticmethod
    def delete_credit_card(user_id: int, card_id: int, db: Session) -> bool:
        cc = db.query(CreditCard).filter(CreditCard.card_id == card_id, CreditCard.user_id == user_id).first()
        if not cc:
            return False
            
        db.delete(cc)
        db.commit()
        LoanService._recalc(user_id, db)
        return True

loan_service = LoanService()
