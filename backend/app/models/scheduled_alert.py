"""
Scheduled Alert Model — Proactive reminders (EMI, FD maturity, tax due dates).
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class ScheduledAlert(Base):
    __tablename__ = "scheduled_alerts"

    scheduled_alert_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # EMI_REMINDER, FD_MATURITY, TAX_DUE
    reference_id = Column(Integer, nullable=True)  # FK to loans, credit_cards, investments, or goals
    reference_table = Column(String(50), nullable=True)  # 'loans', 'credit_cards', 'investments', 'goals'
    scheduled_date = Column(Date, nullable=False, index=True)  # When alert should trigger
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user = relationship("User", back_populates="scheduled_alerts")
