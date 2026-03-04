"""
Business Metrics Model — Pre-calculated business financial metrics.
Decoupled from personal metrics for isolation and independent updates.
"""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BusinessMetrics(Base):
    __tablename__ = "business_metrics"

    metric_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # ── Business Finance KPIs ──
    business_net_worth = Column(Numeric(15, 2), nullable=True)
    net_profit = Column(Numeric(15, 2), nullable=True)
    working_capital = Column(Numeric(15, 2), nullable=True)
    cash_flow = Column(Numeric(15, 2), nullable=True)
    debt_ratio = Column(Numeric(6, 2), nullable=True)                   # %
    liquidity_ratio = Column(Numeric(6, 2), nullable=True)
    gross_profit_margin = Column(Numeric(6, 2), nullable=True)          # %
    net_profit_margin = Column(Numeric(6, 2), nullable=True)            # %
    emi_burden_ratio = Column(Numeric(6, 2), nullable=True)             # %
    total_inventory_value = Column(Numeric(15, 2), nullable=True)
    total_receivables = Column(Numeric(15, 2), nullable=True)
    total_payables = Column(Numeric(15, 2), nullable=True)
    cash_in_hand = Column(Numeric(15, 2), nullable=True)                # Business cash

    # Timestamps
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="business_metrics")
