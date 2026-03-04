"""
Cash Model — Cash in hand for personal and business modes.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Cash(Base):
    __tablename__ = "cash"

    cash_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False, default=0)
    description = Column(String(200), nullable=True)
    mode = Column(String(20), nullable=False, default="personal")  # personal | business
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # One cash record per mode per user
    __table_args__ = (
        UniqueConstraint("user_id", "mode", name="uq_user_cash_mode"),
    )

    # Relationship
    user = relationship("User", back_populates="cash_records")
