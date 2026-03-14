"""Services layer for authentication, wallet, and image processing."""

import io
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from PIL import Image
from sqlalchemy.orm import Session

from .models import (
    ModelConfig,
    PhotoUsage,
    PlanType,
    PricingPlan,
    TransactionStatus,
    TransactionType,
    User,
    UserRole,
    Wallet,
    WalletTransaction,
)

logger = logging.getLogger(__name__)

# Constants
FREE_MAX_RESOLUTION = 480  # 480p for free users
HD_MIN_RESOLUTION = 720    # HD starts from 720p
CREDITS_PER_PHOTO = 1      # 1 credit per photo


class AuthService:
    """Service for user authentication and management."""
    
    @staticmethod
    def get_or_create_user(
        db: Session,
        email: str,
        google_id: Optional[str] = None,
        name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> User:
        """Get existing user or create new one."""
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update last login and profile info
            user.last_login_at = datetime.utcnow()
            if name:
                user.name = name
            if picture:
                user.picture = picture
            if google_id and not user.google_id:
                user.google_id = google_id
            db.commit()
            return user
        
        # Create new user
        user = User(
            email=email,
            google_id=google_id,
            name=name,
            picture=picture,
            role=UserRole.USER,
            plan_type=PlanType.FREE,
            last_login_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create wallet for new user
        wallet = Wallet(user_id=user.id, balance=0)
        db.add(wallet)
        db.commit()
        
        logger.info(f"Created new user: {email}")
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()


class WalletService:
    """Service for wallet operations."""
    
    @staticmethod
    def get_wallet(db: Session, user_id: int) -> Optional[Wallet]:
        """Get user's wallet."""
        return db.query(Wallet).filter(Wallet.user_id == user_id).first()
    
    @staticmethod
    def get_balance(db: Session, user_id: int) -> int:
        """Get wallet balance."""
        wallet = WalletService.get_wallet(db, user_id)
        return wallet.balance if wallet else 0
    
    @staticmethod
    def has_sufficient_balance(db: Session, user_id: int, amount: int = CREDITS_PER_PHOTO) -> bool:
        """Check if user has sufficient balance."""
        balance = WalletService.get_balance(db, user_id)
        return balance >= amount
    
    @staticmethod
    def add_credits(
        db: Session,
        user_id: int,
        amount: int,
        description: str = "",
        payment_id: Optional[str] = None,
        payment_method: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Add credits to wallet (e.g., after purchase)."""
        wallet = WalletService.get_wallet(db, user_id)
        if not wallet:
            return False, "Wallet not found"
        
        try:
            # Add credits
            wallet.add(amount)
            
            # Create transaction record
            transaction = WalletTransaction(
                user_id=user_id,
                amount=amount,
                transaction_type=TransactionType.CREDIT,
                status=TransactionStatus.COMPLETED,
                description=description or f"Added {amount} credits",
                payment_id=payment_id,
                payment_method=payment_method,
            )
            db.add(transaction)
            db.commit()
            
            logger.info(f"Added {amount} credits to user {user_id}")
            return True, f"Successfully added {amount} credits"
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add credits: {e}")
            return False, str(e)
    
    @staticmethod
    def deduct_credits_for_photo(
        db: Session,
        user_id: int,
        photo_usage_id: int,
        amount: int = CREDITS_PER_PHOTO,
    ) -> Tuple[bool, str]:
        """Deduct credits for photo processing."""
        wallet = WalletService.get_wallet(db, user_id)
        if not wallet:
            return False, "Wallet not found"
        
        if wallet.balance < amount:
            return False, "Insufficient balance"
        
        try:
            # Deduct credits
            wallet.deduct(amount)
            
            # Create transaction record
            transaction = WalletTransaction(
                user_id=user_id,
                amount=-amount,
                transaction_type=TransactionType.DEBIT,
                status=TransactionStatus.COMPLETED,
                description=f"Used {amount} credit(s) for photo processing",
                photo_usage_id=photo_usage_id,
            )
            db.add(transaction)
            db.commit()
            
            logger.info(f"Deducted {amount} credits from user {user_id}")
            return True, f"Deducted {amount} credit(s)"
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to deduct credits: {e}")
            return False, str(e)
    
    @staticmethod
    def get_transaction_history(db: Session, user_id: int, limit: int = 50) -> List[WalletTransaction]:
        """Get user's transaction history."""
        return (
            db.query(WalletTransaction)
            .filter(WalletTransaction.user_id == user_id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
            .all()
        )


class PlanService:
    """Service for pricing plans and purchases."""
    
    PLAN_CONFIGS = {
        PlanType.BASIC: {"price": 20, "credits": 10},
        PlanType.STANDARD: {"price": 50, "credits": 30},
        PlanType.PREMIUM: {"price": 100, "credits": 70},
    }
    
    @staticmethod
    def get_all_plans(db: Session, include_inactive: bool = False) -> List[PricingPlan]:
        """Get all pricing plans."""
        query = db.query(PricingPlan)
        if not include_inactive:
            query = query.filter(PricingPlan.is_active == True)
        return query.order_by(PricingPlan.price_inr).all()
    
    @staticmethod
    def get_plan_by_name(db: Session, name: str) -> Optional[PricingPlan]:
        """Get plan by name."""
        return db.query(PricingPlan).filter(PricingPlan.name == name).first()
    
    @staticmethod
    def purchase_plan(
        db: Session,
        user_id: int,
        plan_type: PlanType,
        payment_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Process plan purchase."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
        
        plan_config = PlanService.PLAN_CONFIGS.get(plan_type)
        if not plan_config:
            return False, "Invalid plan type"
        
        try:
            # Update user plan
            user.plan_type = plan_type
            user.plan_activated_at = datetime.utcnow()
            # Plan expires in 1 year
            user.plan_expires_at = datetime.utcnow() + timedelta(days=365)
            
            # Add credits to wallet
            credits = plan_config["credits"]
            success, message = WalletService.add_credits(
                db=db,
                user_id=user_id,
                amount=credits,
                description=f"Purchased {plan_type.value} plan",
                payment_id=payment_id,
                payment_method="razorpay",  # Default payment method
            )
            
            if not success:
                db.rollback()
                return False, f"Failed to add credits: {message}"
            
            db.commit()
            logger.info(f"User {user_id} purchased plan {plan_type.value}")
            return True, f"Successfully purchased {plan_type.value} plan with {credits} credits"
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to purchase plan: {e}")
            return False, str(e)


class ModelService:
    """Service for AI model management."""
    
    @staticmethod
    def get_all_models(db: Session, include_inactive: bool = False) -> List[ModelConfig]:
        """Get all AI models."""
        query = db.query(ModelConfig)
        if not include_inactive:
            query = query.filter(ModelConfig.is_active == True)
        return query.order_by(ModelConfig.model_name).all()
    
    @staticmethod
    def get_basic_models(db: Session) -> List[ModelConfig]:
        """Get basic models available to free users."""
        return (
            db.query(ModelConfig)
            .filter(ModelConfig.is_basic == True, ModelConfig.is_active == True)
            .all()
        )
    
    @staticmethod
    def is_model_allowed(db: Session, model_name: str, user: Optional[User] = None) -> Tuple[bool, str]:
        """Check if a model is allowed for the user."""
        model = db.query(ModelConfig).filter(ModelConfig.model_name == model_name).first()
        
        if not model:
            return False, f"Model '{model_name}' not found"
        
        if not model.is_active:
            return False, f"Model '{model_name}' is currently disabled"
        
        # If model is basic, it's allowed to everyone
        if model.is_basic:
            return True, "OK"
        
        # For advanced models, user must be logged in and have active plan with credits
        if not user:
            return False, "Please login to use advanced models"
        
        if not user.has_active_plan():
            return False, "Please purchase a plan to use advanced models"
        
        # Check wallet balance
        wallet = WalletService.get_wallet(db, user.id)
        if not wallet or wallet.balance < CREDITS_PER_PHOTO:
            return False, "Insufficient credits. Please recharge your wallet."
        
        return True, "OK"
    
    @staticmethod
    def toggle_model(db: Session, model_name: str, is_active: bool) -> Tuple[bool, str]:
        """Enable or disable a model (admin only)."""
        model = db.query(ModelConfig).filter(ModelConfig.model_name == model_name).first()
        if not model:
            return False, f"Model '{model_name}' not found"
        
        model.is_active = is_active
        db.commit()
        status = "enabled" if is_active else "disabled"
        return True, f"Model '{model_name}' {status}"
    
    @staticmethod
    def set_model_basic(db: Session, model_name: str, is_basic: bool) -> Tuple[bool, str]:
        """Set whether a model is basic (available to free users)."""
        model = db.query(ModelConfig).filter(ModelConfig.model_name == model_name).first()
        if not model:
            return False, f"Model '{model_name}' not found"
        
        model.is_basic = is_basic
        db.commit()
        category = "basic" if is_basic else "advanced"
        return True, f"Model '{model_name}' is now {category}"


class PhotoService:
    """Service for photo processing and history."""
    
    @staticmethod
    def record_usage(
        db: Session,
        user_id: int,
        model_used: str,
        was_hd: bool,
        resolution: str,
        original_filename: Optional[str] = None,
    ) -> Optional[PhotoUsage]:
        """Record photo processing usage."""
        try:
            usage = PhotoUsage(
                user_id=user_id,
                model_used=model_used,
                was_hd=was_hd,
                resolution=resolution,
                original_filename=original_filename,
                credits_deducted=CREDITS_PER_PHOTO,
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
            return usage
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record usage: {e}")
            return None
    
    @staticmethod
    def get_usage_history(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PhotoUsage]:
        """Get user's photo processing history."""
        return (
            db.query(PhotoUsage)
            .filter(PhotoUsage.user_id == user_id)
            .order_by(PhotoUsage.processed_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def get_usage_count(db: Session, user_id: int) -> int:
        """Get total number of processed photos for user."""
        return db.query(PhotoUsage).filter(PhotoUsage.user_id == user_id).count()


class ImageProcessingService:
    """Service for image processing with restrictions."""
    
    @staticmethod
    def resize_for_free_user(image: Image.Image) -> Image.Image:
        """Resize image to max 480p for free users."""
        width, height = image.size
        
        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            # Landscape
            if width > FREE_MAX_RESOLUTION:
                ratio = FREE_MAX_RESOLUTION / width
                new_width = FREE_MAX_RESOLUTION
                new_height = int(height * ratio)
                return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            # Portrait
            if height > FREE_MAX_RESOLUTION:
                ratio = FREE_MAX_RESOLUTION / height
                new_height = FREE_MAX_RESOLUTION
                new_width = int(width * ratio)
                return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def add_watermark(image: Image.Image, text: str = "Free Version") -> Image.Image:
        """Add watermark to image for free users."""
        from PIL import ImageDraw, ImageFont
        
        # Create a copy to avoid modifying original
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on image size
        width, height = img.size
        font_size = max(12, min(width, height) // 20)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (bottom right)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = width - text_width - 10
        y = height - text_height - 10
        
        # Draw text with semi-transparent background
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [x - 5, y - 2, x + text_width + 5, y + text_height + 2],
            fill=(0, 0, 0, 128)
        )
        
        # Composite overlay onto image
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        return img
    
    @staticmethod
    def get_resolution_string(image: Image.Image) -> str:
        """Get resolution as string."""
        return f"{image.size[0]}x{image.size[1]}"
    
    @staticmethod
    def is_hd(image: Image.Image) -> bool:
        """Check if image is HD (>= 720p in any dimension)."""
        width, height = image.size
        return width >= HD_MIN_RESOLUTION or height >= HD_MIN_RESOLUTION
