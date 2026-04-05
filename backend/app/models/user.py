"""
User Model — Core authentication and profile table.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    account_type = Column(String(20), nullable=False, default="personal")  # personal | business | both
    monthly_income = Column(Numeric(15, 2), default=0)
    monthly_savings = Column(Numeric(15, 2), default=0)
    monthly_expenses = Column(Numeric(15, 2), default=0)
    other_monthly_income = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    credit_cards = relationship("CreditCard", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    tax = relationship("Tax", back_populates="user", cascade="all, delete-orphan", uselist=False)
    personal_metrics = relationship("PersonalMetrics", back_populates="user", cascade="all, delete-orphan", uselist=False)
    business_metrics = relationship("BusinessMetrics", back_populates="user", cascade="all, delete-orphan", uselist=False)
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    cash_records = relationship("Cash", back_populates="user", cascade="all, delete-orphan")
    business_inventory = relationship("BusinessInventory", back_populates="user", cascade="all, delete-orphan")
    business_receivables = relationship("BusinessReceivable", back_populates="user", cascade="all, delete-orphan")
    business_payables = relationship("BusinessPayable", back_populates="user", cascade="all, delete-orphan")
    scheduled_alerts = relationship("ScheduledAlert", back_populates="user", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
