from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.asset import Asset, AssetType
from app.security.auth_dependencies import get_current_user
from app.engines.personal_recalculation_engine import recalculate_personal_metrics
from app.engines.business_recalculation_engine import recalculate_business_metrics

router = APIRouter(prefix="/assets", tags=["Finance - Assets"])

class AssetCreate(BaseModel):
    name: str
    asset_type: str
    value: float

@router.get("/")
def get_assets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assets = db.query(Asset).filter(Asset.user_id == current_user.user_id).all()
    return {"success": True, "data": [
        {
            "asset_id": a.asset_id,
            "name": a.name,
            "asset_type": a.asset_type.value,
            "value": float(a.value),
        } for a in assets
    ]}

@router.post("/")
def create_asset(req: AssetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        a_type = AssetType(req.asset_type)
    except ValueError:
        raise HTTPException(400, "Invalid asset type")

    asset = Asset(
        user_id=current_user.user_id,
        name=req.name,
        asset_type=a_type,
        value=Decimal(str(req.value))
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    if current_user.account_type in ["personal", "both"]:
        recalculate_personal_metrics(current_user.user_id, db)
    if current_user.account_type in ["business", "both"]:
        recalculate_business_metrics(current_user.user_id, db)
    
    return {"success": True, "message": "Asset created", "data": {"asset_id": asset.asset_id}}

@router.delete("/{asset_id}")
def delete_asset(asset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id, Asset.user_id == current_user.user_id).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
        
    db.delete(asset)
    db.commit()
    
    if current_user.account_type in ["personal", "both"]:
        recalculate_personal_metrics(current_user.user_id, db)
    if current_user.account_type in ["business", "both"]:
        recalculate_business_metrics(current_user.user_id, db)
    return {"success": True, "message": "Asset deleted"}
