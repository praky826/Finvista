"""
Goal Model — Financial goals with targets and deadlines.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    goal_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    goal_name = Column(String(150), nullable=False)
    target = Column(Numeric(15, 2), nullable=False)
    deadline = Column(Date, nullable=False)
    current_savings = Column(Numeric(15, 2), nullable=False, default=0)
    mode = Column(String(20), nullable=False, default="personal")  # personal | business
    priority = Column(String(20), default="medium")  # low | medium | high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="goals")
