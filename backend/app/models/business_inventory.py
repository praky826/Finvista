"""
Business Inventory Model — Tracks inventory items and values for working capital.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BusinessInventory(Base):
    __tablename__ = "business_inventory"

    inventory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False, default=0)
    unit_cost = Column(Numeric(15, 2), nullable=False, default=0)
    current_value = Column(Numeric(15, 2), nullable=False, default=0)  # quantity × unit_cost
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="business_inventory")
