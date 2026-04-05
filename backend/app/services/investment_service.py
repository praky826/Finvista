from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.investment import Investment
from app.models.goal import Goal
from app.schemas.finance_schemas import InvestmentCreate, InvestmentUpdate, GoalCreate, GoalUpdate
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics

class InvestmentService:
    @staticmethod
    def _recalc(user_id: int, db: Session):
        recalculate_personal_metrics(user_id, db)
        recalculate_business_metrics(user_id, db)

    # ── Investments ──
    @staticmethod
    def get_investments(user_id: int, db: Session):
        return db.query(Investment).filter(Investment.user_id == user_id).all()

    @staticmethod
    def create_investment(user_id: int, body: InvestmentCreate, db: Session) -> Investment:
        inv = Investment(
            user_id=user_id,
            type=body.type,
            value=Decimal(str(body.value)),
            interest_rate=Decimal(str(body.interest_rate)) if body.interest_rate else None,
            tenure_months=body.tenure_months,
            maturity_date=body.maturity_date,
            purchase_date=body.purchase_date
        )
        db.add(inv)
        db.commit()
        InvestmentService._recalc(user_id, db)
        return inv

    @staticmethod
    def update_investment(user_id: int, investment_id: int, body: InvestmentUpdate, db: Session) -> Investment | None:
        inv = db.query(Investment).filter(Investment.investment_id == investment_id, Investment.user_id == user_id).first()
        if not inv:
            return None
            
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(inv, k, Decimal(str(v)) if isinstance(v, (int, float)) else v)
            
        db.commit()
        InvestmentService._recalc(user_id, db)
        return inv

    @staticmethod
    def delete_investment(user_id: int, investment_id: int, db: Session) -> bool:
        inv = db.query(Investment).filter(Investment.investment_id == investment_id, Investment.user_id == user_id).first()
        if not inv:
            return False
            
        db.delete(inv)
        db.commit()
        InvestmentService._recalc(user_id, db)
        return True

    # ── Goals ──
    @staticmethod
    def get_goals(user_id: int, db: Session):
        return db.query(Goal).filter(Goal.user_id == user_id).all()

    @staticmethod
    def create_goal(user_id: int, body: GoalCreate, db: Session) -> Goal:
        goal = Goal(
            user_id=user_id,
            goal_name=body.goal_name,
            target=Decimal(str(body.target)),
            deadline=body.deadline,
            current_savings=Decimal(str(body.current_savings)),
            mode=body.mode,
            priority=body.priority
        )
        db.add(goal)
        db.commit()
        InvestmentService._recalc(user_id, db)
        return goal

    @staticmethod
    def update_goal(user_id: int, goal_id: int, body: GoalUpdate, db: Session) -> Goal | None:
        goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            return None
            
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(goal, k, Decimal(str(v)) if isinstance(v, float) else v)
            
        db.commit()
        InvestmentService._recalc(user_id, db)
        return goal

    @staticmethod
    def delete_goal(user_id: int, goal_id: int, db: Session) -> bool:
        goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
        if not goal:
            return False
            
        db.delete(goal)
        db.commit()
        InvestmentService._recalc(user_id, db)
        return True

investment_service = InvestmentService()
