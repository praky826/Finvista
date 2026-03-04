"""
Auth Dependencies — FastAPI Depends() for protecting routes.
Includes login attempt rate limiting.
"""
from datetime import datetime, timezone
from typing import Dict, Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.security.jwt_handler import decode_token
from app.models.user import User

# Bearer token scheme
security_scheme = HTTPBearer()

# In-memory login attempt tracker (production: use Redis)
# Format: { "username": (attempt_count, first_attempt_time, locked_until) }
_login_attempts: Dict[str, Tuple[int, datetime, datetime | None]] = {}

# Constants
MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 10
ATTEMPT_WINDOW_MINUTES = 30


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: Extract user from JWT token.
    Raises 401 if token is invalid, expired, or user not found.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user ID",
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def check_login_attempts(username: str) -> None:
    """
    Check if a user account is locked due to failed login attempts.
    Rule: 5 failed attempts in 30 minutes → lock for 10 minutes.
    """
    if username not in _login_attempts:
        return

    count, first_attempt, locked_until = _login_attempts[username]
    now = datetime.now(timezone.utc)

    # Check if currently locked
    if locked_until and now < locked_until:
        remaining = int((locked_until - now).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {remaining} minutes.",
        )

    # Reset if window has expired
    if (now - first_attempt).total_seconds() > ATTEMPT_WINDOW_MINUTES * 60:
        del _login_attempts[username]


def record_failed_login(username: str) -> None:
    """Record a failed login attempt and lock account if limit exceeded."""
    now = datetime.now(timezone.utc)

    if username not in _login_attempts:
        _login_attempts[username] = (1, now, None)
        return

    count, first_attempt, _ = _login_attempts[username]

    # Reset if window expired
    if (now - first_attempt).total_seconds() > ATTEMPT_WINDOW_MINUTES * 60:
        _login_attempts[username] = (1, now, None)
        return

    count += 1
    locked_until = None
    if count >= MAX_LOGIN_ATTEMPTS:
        from datetime import timedelta
        locked_until = now + timedelta(minutes=LOCK_DURATION_MINUTES)

    _login_attempts[username] = (count, first_attempt, locked_until)


def record_successful_login(username: str) -> None:
    """Clear login attempt history on successful login."""
    if username in _login_attempts:
        del _login_attempts[username]
