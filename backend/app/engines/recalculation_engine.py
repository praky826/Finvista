"""
Recalculation Engine — Backward-compatible wrapper.
Delegates to the decoupled personal and business recalculation engines.
"""
from sqlalchemy.orm import Session
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics


def recalculate_all_metrics(user_id: int, db: Session) -> dict:
    """
    BACKWARD-COMPATIBLE WRAPPER — Calls both engines sequentially.
    Used by auth.py complete-setup and any code that needs full recalculation.
    """
    personal_result = recalculate_personal_metrics(user_id, db)

    business_result = recalculate_business_metrics(user_id, db)

    return {
        "success": True,
        "message": "All metrics recalculated",
        "health_score": personal_result.get("health_score", 0),
    }
