"""
Credit Card Model — Tracks credit limits, usage, and EMI.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class CreditCard(Base):
    __tablename__ = "credit_cards"

    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    card_name = Column(String(100), nullable=False)
    credit_limit = Column(Numeric(15, 2), nullable=False, default=0)
    credit_used = Column(Numeric(15, 2), nullable=False, default=0)
    emi = Column(Numeric(15, 2), default=0)
    next_due_date = Column(Date, nullable=True)  # V3: For payment reminders
    due_day_of_month = Column(Integer, nullable=True)  # V3: Day when payment is due
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="credit_cards")
