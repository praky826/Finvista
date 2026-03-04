"""
Business Receivables Model — Outstanding customer invoices.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class BusinessReceivable(Base):
    __tablename__ = "business_receivables"

    receivable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = Column(String(150), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    invoice_amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending | partial | received
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="business_receivables")
