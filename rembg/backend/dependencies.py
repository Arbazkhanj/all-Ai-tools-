"""FastAPI dependencies for authentication and database."""

import json
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, UserRole
from .services import AuthService, WalletService

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from session."""
    # Try to get user from session
    user_data = request.session.get("user")
    if not user_data:
        return None
    
    # Get email from user data
    email = user_data.get("email")
    if not email:
        return None
    
    # Get user from database
    user = AuthService.get_user_by_email(db, email)
    return user


async def get_current_user_or_none(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if logged in, otherwise None."""
    return await get_current_user(request, db)


async def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Require user to be logged in."""
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to access this resource",
        )
    return user


async def require_active_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Require active user."""
    user = await require_user(request, db)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been disabled",
        )
    return user


async def require_admin(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Require admin user."""
    user = await require_active_user(request, db)
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


class UserContext:
    """Context for user processing restrictions."""
    
    def __init__(
        self,
        user: Optional[User] = None,
        db: Optional[Session] = None,
    ):
        self.user = user
        self.db = db
        self.is_authenticated = user is not None
        self.has_active_plan = user.has_active_plan() if user else False
        self.wallet_balance = 0
        
        if user and db:
            self.wallet_balance = WalletService.get_balance(db, user.id)
    
    @property
    def can_use_hd(self) -> bool:
        """Check if user can use HD processing."""
        if not self.is_authenticated:
            return False
        if not self.has_active_plan:
            return False
        return self.wallet_balance >= 1
    
    @property
    def can_use_advanced_models(self) -> bool:
        """Check if user can use advanced models."""
        if not self.is_authenticated:
            return False
        if not self.has_active_plan:
            return False
        return self.wallet_balance >= 1
    
    @property
    def max_resolution(self) -> int:
        """Get max allowed resolution."""
        if self.can_use_hd:
            return 4096  # No practical limit for paid users
        return 480  # 480p for free users
    
    @property
    def should_add_watermark(self) -> bool:
        """Check if watermark should be added."""
        return not self.can_use_hd
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "is_authenticated": self.is_authenticated,
            "has_active_plan": self.has_active_plan,
            "wallet_balance": self.wallet_balance,
            "can_use_hd": self.can_use_hd,
            "can_use_advanced_models": self.can_use_advanced_models,
            "max_resolution": self.max_resolution,
            "should_add_watermark": self.should_add_watermark,
        }


async def get_user_context(
    request: Request,
    db: Session = Depends(get_db),
) -> UserContext:
    """Get user context with processing restrictions."""
    user = await get_current_user(request, db)
    return UserContext(user, db)
