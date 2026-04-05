"""
Asset Model — Custom user assets like Land, House, Automobiles, etc.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AssetType(str, enum.Enum):
    land = "Land"
    house = "House"
    automobile = "Automobiles"
    others = "Others"


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False, default=AssetType.others)
    value = Column(Numeric(15, 2), nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="assets")
