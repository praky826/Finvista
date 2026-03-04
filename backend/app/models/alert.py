"""
Alert Model — Rule-based financial alerts with deduplication.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # e.g. HIGH_DTI, LOW_EMERGENCY_FUND
    severity = Column(String(20), default="info")  # info | warning | critical
    message = Column(String(500), nullable=False)
    metric_value = Column(Numeric(15, 2), nullable=True)  # Current value that triggered alert
    threshold = Column(Numeric(15, 2), nullable=True)  # Threshold that was crossed
    status = Column(String(20), default="active", index=True)  # active | resolved | ignored
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Prevent duplicate active alerts of same type per user
    __table_args__ = (
        UniqueConstraint("user_id", "alert_type", "status", name="uq_user_alert_status"),
    )

    # Relationship
    user = relationship("User", back_populates="alerts")
