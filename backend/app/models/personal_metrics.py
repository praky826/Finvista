"""
Personal Metrics Model — Pre-calculated personal financial metrics.
Decoupled from business metrics for isolation and independent updates.
"""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class PersonalMetrics(Base):
    __tablename__ = "personal_metrics"

    metric_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # ── Personal Finance KPIs ──
    net_worth = Column(Numeric(15, 2), nullable=True)
    savings_ratio = Column(Numeric(6, 2), nullable=True)                # %
    dti = Column(Numeric(6, 2), nullable=True)                          # % (debt-to-income)
    emergency_fund = Column(Numeric(6, 2), nullable=True)               # months
    credit_utilization = Column(Numeric(6, 2), nullable=True)           # %
    liquid_asset_percentage = Column(Numeric(6, 2), nullable=True)      # %
    loan_to_asset = Column(Numeric(6, 2), nullable=True)                # ratio
    tax_estimate = Column(Numeric(15, 2), nullable=True)
    effective_tax_rate = Column(Numeric(6, 2), nullable=True)           # %
    credit_score_simulation = Column(Integer, nullable=True)            # 300-850
    health_score = Column(Numeric(6, 2), nullable=True)                 # 0-100
    cash_flow_monthly = Column(Numeric(15, 2), nullable=True)           # Monthly cash surplus/deficit
    cash_in_hand = Column(Numeric(15, 2), nullable=True)                # Personal cash

    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="personal_metrics")
