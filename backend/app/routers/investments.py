from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.finance_schemas import (
    InvestmentCreate, InvestmentUpdate,
    GoalCreate, GoalUpdate
)
from app.security.auth_dependencies import get_current_user
from app.services.investment_service import investment_service

router = APIRouter(tags=["Finance - Investments & Goals"])

# ═══════════════════════════════════════════
#  INVESTMENTS
# ═══════════════════════════════════════════

@router.get("/investments")
def list_investments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invs = investment_service.get_investments(current_user.user_id, db)
    return {"success": True, "data": [
        {"investment_id": i.investment_id, "type": i.type, "value": float(i.value or 0),
         "interest_rate": float(i.interest_rate) if i.interest_rate else None,
         "tenure_months": i.tenure_months}
        for i in invs
    ]}

@router.post("/investments", status_code=201)
def create_investment(body: InvestmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = investment_service.create_investment(current_user.user_id, body, db)
    return {"success": True, "data": {"investment_id": inv.investment_id}, "message": "Investment added"}

@router.put("/investments/{investment_id}")
def update_investment(investment_id: int, body: InvestmentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = investment_service.update_investment(current_user.user_id, investment_id, body, db)
    if not inv:
        raise HTTPException(404, "Investment not found")
    return {"success": True, "message": "Investment updated"}

@router.delete("/investments/{investment_id}")
def delete_investment(investment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = investment_service.delete_investment(current_user.user_id, investment_id, db)
    if not deleted:
        raise HTTPException(404, "Investment not found")
    return {"success": True, "message": "Investment deleted"}

# ═══════════════════════════════════════════
#  GOALS
# ═══════════════════════════════════════════

@router.get("/goals")
def list_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = investment_service.get_goals(current_user.user_id, db)
    return {"success": True, "data": [
        {"goal_id": g.goal_id, "goal_name": g.goal_name, "target": float(g.target),
         "deadline": g.deadline.isoformat() if g.deadline else None,
         "current_savings": float(g.current_savings or 0), "mode": g.mode, "priority": g.priority}
        for g in goals
    ]}

@router.post("/goals", status_code=201)
def create_goal(body: GoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = investment_service.create_goal(current_user.user_id, body, db)
    return {"success": True, "data": {"goal_id": goal.goal_id}, "message": "Goal created"}

@router.put("/goals/{goal_id}")
def update_goal(goal_id: int, body: GoalUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = investment_service.update_goal(current_user.user_id, goal_id, body, db)
    if not goal:
        raise HTTPException(404, "Goal not found")
    return {"success": True, "message": "Goal updated"}

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = investment_service.delete_goal(current_user.user_id, goal_id, db)
    if not deleted:
        raise HTTPException(404, "Goal not found")
    return {"success": True, "message": "Goal deleted"}
