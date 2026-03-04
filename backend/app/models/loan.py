"""
Loan Model — Tracks home, personal, business, and education loans.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    loan_name = Column(String(100), nullable=False)
    loan_type = Column(String(50), default="personal")  # home | personal | business | education | other
    outstanding = Column(Numeric(15, 2), nullable=False, default=0)
    emi = Column(Numeric(15, 2), nullable=False, default=0)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    tenure_months = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=True)
    mode = Column(String(20), nullable=False, default="personal")  # personal | business
    next_emi_due_date = Column(Date, nullable=True)  # V3: For EMI reminders
    emi_day_of_month = Column(Integer, nullable=True)  # V3: Day when EMI is due (1-31)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="loans")
