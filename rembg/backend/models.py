"""Database models for User, Wallet, Transactions, and Photo Usage."""

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles for access control."""
    USER = "user"
    ADMIN = "admin"


class PlanType(str, enum.Enum):
    """Available pricing plans."""
    FREE = "free"
    BASIC = "basic"  # ₹20 - 10 photos
    STANDARD = "standard"  # ₹50 - 30 photos
    PREMIUM = "premium"  # ₹100 - 70 photos


class TransactionType(str, enum.Enum):
    """Types of wallet transactions."""
    CREDIT = "credit"  # Adding funds
    DEBIT = "debit"    # Using credits
    REFUND = "refund"  # Refunding credits


class TransactionStatus(str, enum.Enum):
    """Transaction status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(512), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Plan information
    plan_type = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    plan_activated_at = Column(DateTime, nullable=True)
    plan_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("WalletTransaction", back_populates="user")
    photo_usage = relationship("PhotoUsage", back_populates="user")

    def has_active_plan(self) -> bool:
        """Check if user has an active paid plan."""
        if self.plan_type == PlanType.FREE:
            return False
        if self.plan_expires_at and self.plan_expires_at < datetime.utcnow():
            return False
        return True
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "role": self.role.value,
            "plan_type": self.plan_type.value,
            "has_active_plan": self.has_active_plan(),
            "plan_activated_at": self.plan_activated_at.isoformat() if self.plan_activated_at else None,
            "plan_expires_at": self.plan_expires_at.isoformat() if self.plan_expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Wallet(Base):
    """Wallet model for storing user credits."""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=0, nullable=False)  # Number of photo credits
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wallet")

    def has_sufficient_balance(self, amount: int = 1) -> bool:
        """Check if wallet has sufficient balance."""
        return self.balance >= amount
    
    def deduct(self, amount: int = 1) -> bool:
        """Deduct credits from wallet."""
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False
    
    def add(self, amount: int) -> None:
        """Add credits to wallet."""
        self.balance += amount
    
    def to_dict(self) -> dict:
        """Convert wallet to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": self.balance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WalletTransaction(Base):
    """Transaction history for wallet."""
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for credit, negative for debit
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    description = Column(String(255), nullable=True)
    
    # For payments
    payment_id = Column(String(255), nullable=True)  # External payment ID
    payment_method = Column(String(100), nullable=True)
    
    # For photo usage
    photo_usage_id = Column(Integer, ForeignKey("photo_usage.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    photo_usage = relationship("PhotoUsage", back_populates="transaction")

    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "status": self.status.value,
            "description": self.description,
            "payment_id": self.payment_id,
            "payment_method": self.payment_method,
            "photo_usage_id": self.photo_usage_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PhotoUsage(Base):
    """History of photo processing."""
    __tablename__ = "photo_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image details
    original_filename = Column(String(255), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Processing details
    model_used = Column(String(100), nullable=False)
    was_hd = Column(Boolean, default=False, nullable=False)
    resolution = Column(String(50), nullable=True)  # e.g., "1920x1080"
    
    # Credit deduction
    credits_deducted = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="photo_usage")
    transaction = relationship("WalletTransaction", back_populates="photo_usage", uselist=False)

    def to_dict(self) -> dict:
        """Convert photo usage to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_filename": self.original_filename,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "model_used": self.model_used,
            "was_hd": self.was_hd,
            "resolution": self.resolution,
            "credits_deducted": self.credits_deducted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PricingPlan(Base):
    """Pricing plans configuration."""
    __tablename__ = "pricing_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "basic"
    display_name = Column(String(255), nullable=False)  # e.g., "Basic Plan"
    price_inr = Column(Integer, nullable=False)  # Price in INR (₹)
    credits = Column(Integer, nullable=False)  # Number of photo credits
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Features
    allows_hd = Column(Boolean, default=True, nullable=False)
    allows_all_models = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert pricing plan to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "price_inr": self.price_inr,
            "credits": self.credits,
            "description": self.description,
            "is_active": self.is_active,
            "allows_hd": self.allows_hd,
            "allows_all_models": self.allows_all_models,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelConfig(Base):
    """AI Model configuration and access control."""
    __tablename__ = "model_configs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    is_basic = Column(Boolean, default=False, nullable=False)  # Available to free users
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Convert model config to dictionary."""
        return {
            "id": self.id,
            "model_name": self.model_name,
            "display_name": self.display_name,
            "is_basic": self.is_basic,
            "is_active": self.is_active,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
