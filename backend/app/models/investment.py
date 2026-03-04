"""
Investment Model — Tracks FDs, stocks, mutual funds, gold, and property.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Investment(Base):
    __tablename__ = "investments"

    investment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # fd | stock | mf | gold | property
    value = Column(Numeric(15, 2), nullable=False, default=0)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    tenure_months = Column(Integer, nullable=True)
    maturity_date = Column(Date, nullable=True)  # V3: For FD maturity alerts
    purchase_date = Column(Date, nullable=True)  # V3: When investment was made
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="investments")
