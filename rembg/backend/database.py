"""Database configuration and session management."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Database URL - use SQLite by default, can be configured via environment variable
# Use /tmp for Railway (ephemeral storage), or current directory for local
default_db_path = "/tmp/rembg_payments.db" if os.getenv("RAILWAY_ENVIRONMENT") else "./rembg_payments.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get database session as context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from .models import Base
    Base.metadata.create_all(bind=engine)


def seed_initial_data() -> None:
    """Seed initial data like pricing plans and model configs."""
    from .models import (
        ModelConfig,
        PricingPlan,
        PlanType,
    )
    
    with get_db_context() as db:
        # Seed pricing plans if not exists
        existing_plans = db.query(PricingPlan).count()
        if existing_plans == 0:
            plans = [
                PricingPlan(
                    name=PlanType.BASIC.value,
                    display_name="Basic Plan",
                    price_inr=20,
                    credits=10,
                    description="10 photo credits for ₹20",
                    allows_hd=True,
                    allows_all_models=True,
                ),
                PricingPlan(
                    name=PlanType.STANDARD.value,
                    display_name="Standard Plan",
                    price_inr=50,
                    credits=30,
                    description="30 photo credits for ₹50 (Save ₹10)",
                    allows_hd=True,
                    allows_all_models=True,
                ),
                PricingPlan(
                    name=PlanType.PREMIUM.value,
                    display_name="Premium Plan",
                    price_inr=100,
                    credits=70,
                    description="70 photo credits for ₹100 (Save ₹40)",
                    allows_hd=True,
                    allows_all_models=True,
                ),
            ]
            for plan in plans:
                db.add(plan)
        
        # Seed model configs if not exists
        existing_models = db.query(ModelConfig).count()
        if existing_models == 0:
            models = [
                ModelConfig(
                    model_name="u2net",
                    display_name="U2Net (General Purpose)",
                    is_basic=True,
                    description="Default model for general background removal",
                ),
                ModelConfig(
                    model_name="u2netp",
                    display_name="U2NetP (Lightweight)",
                    is_basic=True,
                    description="Lightweight version of U2Net",
                ),
                ModelConfig(
                    model_name="u2net_human_seg",
                    display_name="U2Net Human Segmentation",
                    is_basic=True,
                    description="Optimized for human segmentation",
                ),
                ModelConfig(
                    model_name="silueta",
                    display_name="Silueta",
                    is_basic=True,
                    description="Lightweight model (43MB)",
                ),
                ModelConfig(
                    model_name="isnet-general-use",
                    display_name="ISNet General Use",
                    is_basic=False,
                    description="High accuracy for general use cases",
                ),
                ModelConfig(
                    model_name="isnet-anime",
                    display_name="ISNet Anime",
                    is_basic=False,
                    description="High accuracy for anime characters",
                ),
                ModelConfig(
                    model_name="sam",
                    display_name="SAM (Segment Anything)",
                    is_basic=False,
                    description="Advanced segmentation model",
                ),
                ModelConfig(
                    model_name="birefnet-general",
                    display_name="BiRefNet General",
                    is_basic=False,
                    description="State-of-the-art general background removal",
                ),
                ModelConfig(
                    model_name="birefnet-general-lite",
                    display_name="BiRefNet General Lite",
                    is_basic=False,
                    description="Lightweight BiRefNet model",
                ),
                ModelConfig(
                    model_name="birefnet-portrait",
                    display_name="BiRefNet Portrait",
                    is_basic=False,
                    description="Optimized for portraits",
                ),
                ModelConfig(
                    model_name="birefnet-dis",
                    display_name="BiRefNet DIS",
                    is_basic=False,
                    description="Dichotomous image segmentation",
                ),
                ModelConfig(
                    model_name="birefnet-hrsod",
                    display_name="BiRefNet HRSOD",
                    is_basic=False,
                    description="High-resolution salient object detection",
                ),
                ModelConfig(
                    model_name="birefnet-cod",
                    display_name="BiRefNet COD",
                    is_basic=False,
                    description="Concealed object detection",
                ),
                ModelConfig(
                    model_name="birefnet-massive",
                    display_name="BiRefNet Massive",
                    is_basic=False,
                    description="Trained on massive dataset",
                ),
                ModelConfig(
                    model_name="bria-rmbg",
                    display_name="BRIA RMBG",
                    is_basic=False,
                    description="State-of-the-art model by BRIA AI",
                ),
                ModelConfig(
                    model_name="u2net_cloth_seg",
                    display_name="U2Net Cloth Segmentation",
                    is_basic=False,
                    description="Clothes parsing from portrait",
                ),
            ]
            for model in models:
                db.add(model)
        
        db.commit()
