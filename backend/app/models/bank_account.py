"""
Bank Account Model — Tracks savings, current, and salary accounts.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    account_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False, default="savings")  # savings | current | salary
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    mode = Column(String(20), nullable=False, default="personal")  # personal | business
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="bank_accounts")
