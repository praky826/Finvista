"""
Tax Model — Personal and business tax information.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Tax(Base):
    __tablename__ = "tax"

    tax_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # Personal Income Tax
    annual_income = Column(Numeric(15, 2), nullable=True)
    monthly_income = Column(Numeric(15, 2), nullable=True)
    deductions_80c = Column(Numeric(15, 2), default=0)  # Life Insurance, PPF, ELSS (max ₹1.5L)
    deductions_80d = Column(Numeric(15, 2), default=0)  # Health insurance (max ₹25,000)
    deductions_80tta = Column(Numeric(15, 2), default=0)  # Savings interest (max ₹10,000)
    other_deductions = Column(Numeric(15, 2), default=0)
    regime = Column(String(20), default="new")  # old | new

    # Business Tax
    business_revenue = Column(Numeric(15, 2), nullable=True)
    business_expenses = Column(Numeric(15, 2), nullable=True)
    cogs = Column(Numeric(15, 2), nullable=True)  # Cost of Goods Sold
    business_deductions = Column(Numeric(15, 2), default=0)
    corporate_tax_percent = Column(Numeric(5, 2), default=30)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="tax")
