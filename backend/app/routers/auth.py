"""
Auth Router — Registration and login endpoints.
POST /auth/register, POST /auth/login
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.tax import Tax
from app.models.personal_metrics import PersonalMetrics
from app.models.business_metrics import BusinessMetrics
from app.schemas.user_schema import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.security.hashing import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.security.auth_dependencies import (
    check_login_attempts, record_failed_login, record_successful_login, get_current_user
)
from app.engines.recalculation_engine import recalculate_all_metrics

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user (Step 2 of wizard).
    Creates user + tax + personal_metrics/business_metrics rows.
    """
    # Check duplicates
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    user = User(
        full_name=request.full_name,
        email=request.email,
        username=request.username,
        password_hash=hash_password(request.password),
        account_type=request.account_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create empty tax row
    tax = Tax(user_id=user.user_id, regime="new")
    db.add(tax)

    # Create metric rows based on account type
    if request.account_type in ("personal", "both"):
        personal = PersonalMetrics(user_id=user.user_id)
        db.add(personal)
    if request.account_type in ("business", "both"):
        business = BusinessMetrics(user_id=user.user_id)
        db.add(business)
    db.commit()

    # Generate token so frontend can auto-login
    token = create_access_token(data={"sub": str(user.user_id)})

    return {
        "success": True,
        "data": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "account_type": user.account_type,
            "token": token,
            "token_type": "bearer",
            "full_name": user.full_name,
        },
        "message": "Registration successful!",
    }


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Log in and receive a JWT token."""
    # Check login attempts
    check_login_attempts(request.username)

    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        record_failed_login(request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    record_successful_login(request.username)

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Generate token
    token = create_access_token(data={"sub": str(user.user_id)})

    return {
        "success": True,
        "data": {
            "user_id": user.user_id,
            "token": token,
            "token_type": "bearer",
            "expires_in": 1800,
            "account_type": user.account_type,
            "full_name": user.full_name,
        },
        "message": "Login successful",
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return {
        "success": True,
        "data": {
            "user_id": current_user.user_id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "username": current_user.username,
            "account_type": current_user.account_type,
            "monthly_income": float(current_user.monthly_income or 0),
            "monthly_expenses": float(current_user.monthly_expenses or 0),
        },
    }


@router.post("/complete-setup")
def complete_setup(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Called after 10-step registration wizard is complete. Triggers initial recalculation."""
    result = recalculate_all_metrics(current_user.user_id, db)
    return {
        "success": True,
        "message": "Setup complete! Dashboard ready.",
        "health_score": result.get("health_score", 0),
    }
