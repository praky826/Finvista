"""
Business Payables Model — Outstanding vendor bills.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BusinessPayable(Base):
    __tablename__ = "business_payables"

    payable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_name = Column(String(150), nullable=True)
    bill_number = Column(String(50), nullable=True)
    bill_amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending | partial | paid
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="business_payables")
