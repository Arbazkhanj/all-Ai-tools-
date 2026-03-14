import io
import json
import os
import secrets
import webbrowser
from pathlib import Path
from typing import Optional, Tuple, cast

import aiohttp
import click
import uvicorn
from asyncer import asyncify
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from PIL import Image
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from .. import __version__
from ..bg import remove
from ..session_factory import new_session
from ..sessions import sessions_names
from ..sessions.base import BaseSession

# Import backend modules
from ..backend.database import init_db, seed_initial_data, get_db
from ..backend.models import PlanType, UserRole
from ..backend.services import (
    AuthService,
    ImageProcessingService,
    ModelService,
    PhotoService,
    PlanService,
    WalletService,
)
from ..backend.dependencies import (
    get_current_user,
    get_current_user_or_none,
    get_user_context,
    require_user,
    require_active_user,
    require_admin,
    UserContext,
)
from sqlalchemy.orm import Session

# Get the path to the static files
STATIC_DIR = Path(__file__).parent.parent / "static"

# OAuth setup
oauth = OAuth()

# Get Google OAuth credentials from environment
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '894379656916-rtiufltvtpemq1fu8mpi0guq5hm486lc.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# OAuth setup - only if secret is configured
oauth_enabled = bool(GOOGLE_CLIENT_SECRET)
if not oauth_enabled:
    print("⚠️  WARNING: GOOGLE_CLIENT_SECRET not set!")
    print("   Google OAuth is DISABLED. Set GOOGLE_CLIENT_SECRET to enable.")
    print("")
else:
    # Register OAuth
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@click.command(
    name="s",
    help="for a http server",
)
@click.option(
    "-p",
    "--port",
    default=7000,
    type=int,
    show_default=True,
    help="port",
)
@click.option(
    "-h",
    "--host",
    default="0.0.0.0",
    type=str,
    show_default=True,
    help="host",
)
@click.option(
    "-l",
    "--log_level",
    default="info",
    type=str,
    show_default=True,
    help="log level",
)
@click.option(
    "-t",
    "--threads",
    default=None,
    type=int,
    show_default=True,
    help="number of worker threads",
)
def s_command(port: int, host: str, log_level: str, threads: int) -> None:
    """
    Command-line interface for running the FastAPI web server.

    This function starts the FastAPI web server with the specified port and log level.
    If the number of worker threads is specified, it sets the thread limiter accordingly.
    """
    # Initialize database
    init_db()
    seed_initial_data()
    
    sessions: dict[str, BaseSession] = {}
    tags_metadata = [
        {
            "name": "Background Removal",
            "description": "Endpoints that perform background removal with different image sources.",
            "externalDocs": {
                "description": "GitHub Source",
                "url": "https://github.com/danielgatis/rembg",
            },
        },
        {
            "name": "Authentication",
            "description": "User authentication and session management.",
        },
        {
            "name": "User",
            "description": "User profile, wallet, and dashboard.",
        },
        {
            "name": "Payments",
            "description": "Pricing plans and payment processing.",
        },
        {
            "name": "Admin",
            "description": "Admin controls for users, wallets, and models.",
        },
    ]
    app = FastAPI(
        title="Khan Jan Seva Kendra - Background Remover",
        description="AI-powered background removal service by Khan Jan Seva Kendra",
        version=__version__,
        contact={
            "name": "Khan Jan Seva Kendra",
            "url": "http://localhost:7860",
            "email": "support@khanjanseva.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://github.com/danielgatis/rembg/blob/main/LICENSE.txt",
        },
        openapi_tags=tags_metadata,
        docs_url="/api",
    )

    # Secret key for session management
    # Use environment variable or generate a fixed key for development
    session_secret = os.environ.get('SESSION_SECRET_KEY')
    if not session_secret:
        # For development, use a fixed key so sessions persist across restarts
        session_secret = 'rembg-dev-secret-key-change-in-production-32chars'
    app.add_middleware(SessionMiddleware, secret_key=session_secret)
    
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class CommonQueryParams:
        def __init__(
            self,
            model: str = Query(
                description="Model to use when processing image",
                pattern=r"(" + "|".join(sessions_names) + ")",
                default="u2net",
            ),
            a: bool = Query(default=False, description="Enable Alpha Matting"),
            af: int = Query(
                default=240,
                ge=0,
                le=255,
                description="Alpha Matting (Foreground Threshold)",
            ),
            ab: int = Query(
                default=10,
                ge=0,
                le=255,
                description="Alpha Matting (Background Threshold)",
            ),
            ae: int = Query(
                default=10, ge=0, description="Alpha Matting (Erode Structure Size)"
            ),
            om: bool = Query(default=False, description="Only Mask"),
            ppm: bool = Query(default=False, description="Post Process Mask"),
            bgc: Optional[str] = Query(default=None, description="Background Color"),
            extras: Optional[str] = Query(
                default=None, description="Extra parameters as JSON"
            ),
        ):
            self.model = model
            self.a = a
            self.af = af
            self.ab = ab
            self.ae = ae
            self.om = om
            self.ppm = ppm
            self.extras = extras
            self.bgc = (
                cast(Tuple[int, int, int, int], tuple(map(int, bgc.split(","))))
                if bgc
                else None
            )

    class CommonQueryPostParams:
        def __init__(
            self,
            model: str = Form(
                description="Model to use when processing image",
                pattern=r"(" + "|".join(sessions_names) + ")",
                default="u2net",
            ),
            a: bool = Form(default=False, description="Enable Alpha Matting"),
            af: int = Form(
                default=240,
                ge=0,
                le=255,
                description="Alpha Matting (Foreground Threshold)",
            ),
            ab: int = Form(
                default=10,
                ge=0,
                le=255,
                description="Alpha Matting (Background Threshold)",
            ),
            ae: int = Form(
                default=10, ge=0, description="Alpha Matting (Erode Structure Size)"
            ),
            om: bool = Form(default=False, description="Only Mask"),
            ppm: bool = Form(default=False, description="Post Process Mask"),
            bgc: Optional[str] = Query(default=None, description="Background Color"),
            extras: Optional[str] = Query(
                default=None, description="Extra parameters as JSON"
            ),
        ):
            self.model = model
            self.a = a
            self.af = af
            self.ab = ab
            self.ae = ae
            self.om = om
            self.ppm = ppm
            self.extras = extras
            self.bgc = (
                cast(Tuple[int, int, int, int], tuple(map(int, bgc.split(","))))
                if bgc
                else None
            )

    def im_without_bg(
        content: bytes,
        commons: CommonQueryParams,
        user: Optional = None,
        db: Optional[Session] = None,
        original_filename: Optional[str] = None,
    ) -> Response:
        """Process image with user restrictions."""
        kwargs = {}

        if commons.extras:
            try:
                kwargs.update(json.loads(commons.extras))
            except Exception:
                pass

        # Load image to check resolution
        img = Image.open(io.BytesIO(content))
        original_size = img.size
        was_hd = ImageProcessingService.is_hd(img)
        
        # Check user restrictions
        user_context = UserContext(user, db)
        
        # Check if model is allowed
        allowed, message = ModelService.is_model_allowed(db, commons.model, user)
        if not allowed:
            return Response(
                content=json.dumps({"error": message}),
                media_type="application/json",
                status_code=403,
            )
        
        # Apply resolution restrictions for free users
        if not user_context.can_use_hd:
            img = ImageProcessingService.resize_for_free_user(img)
            was_hd = False  # Reset HD flag since we resized
        
        # Convert image back to bytes for processing
        img_bytes = io.BytesIO()
        img.convert("RGB").save(img_bytes, format="PNG")
        img_bytes.seek(0)
        content_to_process = img_bytes.read()

        # Get or create session
        session = sessions.get(commons.model)
        if session is None:
            session = new_session(commons.model, **kwargs)
            sessions[commons.model] = session

        # Process image
        result = remove(
            content_to_process,
            session=session,
            alpha_matting=commons.a,
            alpha_matting_foreground_threshold=commons.af,
            alpha_matting_background_threshold=commons.ab,
            alpha_matting_erode_size=commons.ae,
            only_mask=commons.om,
            post_process_mask=commons.ppm,
            bgcolor=commons.bgc,
            **kwargs,
        )

        # Add watermark for free users
        if user_context.should_add_watermark and not commons.om:
            result_img = Image.open(io.BytesIO(result))
            result_img = ImageProcessingService.add_watermark(result_img)
            output = io.BytesIO()
            result_img.save(output, format="PNG")
            output.seek(0)
            result = output.read()

        # Record usage and deduct credits for logged-in users with active plan
        if user and user_context.has_active_plan and user_context.wallet_balance > 0:
            # Record usage
            usage = PhotoService.record_usage(
                db=db,
                user_id=user.id,
                model_used=commons.model,
                was_hd=was_hd,
                resolution=ImageProcessingService.get_resolution_string(img),
                original_filename=original_filename,
            )
            
            # Deduct credits
            if usage:
                WalletService.deduct_credits_for_photo(db, user.id, usage.id)

        return Response(
            result,
            media_type="image/png",
        )

    @app.on_event("startup")
    def startup():
        try:
            webbrowser.open(f"http://{'localhost' if host == '0.0.0.0' else host}:{port}")
        except Exception:
            pass

        if threads is not None:
            from anyio import CapacityLimiter
            from anyio.lowlevel import RunVar

            RunVar("_default_thread_limiter").set(CapacityLimiter(threads))

    # =========================================================================
    # AUTHENTICATION ENDPOINTS
    # =========================================================================

    @app.get("/login", response_class=HTMLResponse, tags=["Authentication"])
    async def login_page(request: Request):
        html_path = STATIC_DIR / "login.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return HTMLResponse(content="<h1>Login</h1><p>Login page not found</p>")

    @app.get("/auth/google", tags=["Authentication"])
    async def auth_google(request: Request):
        if not oauth_enabled:
            return HTMLResponse(content="<h1>Authentication Disabled</h1><p>Google OAuth is not configured.</p>", status_code=503)
        redirect_uri = request.url_for('auth_google_callback')
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @app.get("/auth/callback", tags=["Authentication"])
    async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
        if not oauth_enabled:
            return HTMLResponse(content="<h1>Authentication Disabled</h1><p>Google OAuth is not configured.</p>", status_code=503)
        try:
            token = await oauth.google.authorize_access_token(request)
            user_info = token.get('userinfo')
            if user_info:
                # Get or create user in database
                user = AuthService.get_or_create_user(
                    db=db,
                    email=user_info.get('email'),
                    google_id=user_info.get('sub'),
                    name=user_info.get('name'),
                    picture=user_info.get('picture'),
                )
                
                request.session['user'] = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'picture': user.picture,
                }
            return RedirectResponse(url='/')
        except Exception as e:
            return HTMLResponse(content=f"<h1>Authentication Error</h1><p>{str(e)}</p><a href='/login'>Try Again</a>")

    @app.get("/auth/logout", tags=["Authentication"])
    async def auth_logout(request: Request):
        request.session.pop('user', None)
        return RedirectResponse(url='/login')

    @app.get("/auth/me", tags=["Authentication"])
    async def auth_me(
        request: Request,
        db: Session = Depends(get_db),
    ):
        user = await get_current_user(request, db)
        if not user:
            return JSONResponse(
                content={"error": "Not authenticated"},
                status_code=401,
            )
        
        # Get wallet balance
        wallet = WalletService.get_wallet(db, user.id)
        
        response_data = user.to_dict()
        response_data["wallet_balance"] = wallet.balance if wallet else 0
        
        return JSONResponse(content=response_data)

    @app.post("/auth/google/token", tags=["Authentication"])
    async def auth_google_token(request: Request, db: Session = Depends(get_db)):
        """Handle Google One Tap / Sign-In token"""
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
        
        try:
            body = await request.json()
            id_token_str = body.get('credential')
            client_id = body.get('client_id', GOOGLE_CLIENT_ID)
            
            if not id_token_str:
                return JSONResponse(
                    content={"success": False, "message": "Missing credential"},
                    status_code=400,
                )
            
            # Verify Google token
            try:
                idinfo = google_id_token.verify_oauth2_token(
                    id_token_str,
                    google_requests.Request(),
                    client_id,
                    clock_skew_in_seconds=10
                )
                
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Invalid issuer')
                
                # Get or create user
                user = AuthService.get_or_create_user(
                    db=db,
                    email=idinfo['email'],
                    google_id=idinfo['sub'],
                    name=idinfo.get('name'),
                    picture=idinfo.get('picture'),
                )
                
                request.session['user'] = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'picture': user.picture,
                }
                
                return JSONResponse(content={
                    "success": True,
                    "message": "Authentication successful",
                    "user": user.to_dict(),
                })
                
            except Exception as e:
                return JSONResponse(
                    content={"success": False, "message": f"Token verification failed: {str(e)}"},
                    status_code=401,
                )
                
        except Exception as e:
            return JSONResponse(
                content={"success": False, "message": str(e)},
                status_code=500,
            )

    # =========================================================================
    # USER DASHBOARD ENDPOINTS
    # =========================================================================

    @app.get("/api/user/profile", tags=["User"])
    async def get_user_profile(
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Get complete user profile with wallet."""
        try:
            wallet = WalletService.get_wallet(db, user.id)
            user_dict = user.to_dict()
            
            # Include wallet balance in user dict for convenience
            if wallet:
                user_dict["wallet_balance"] = wallet.balance
            else:
                user_dict["wallet_balance"] = 0
            
            return {
                "user": user_dict,
                "wallet": wallet.to_dict() if wallet else {"balance": 0, "user_id": user.id},
            }
        except Exception as e:
            import logging
            logging.error(f"Error in get_user_profile: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/user/wallet", tags=["User"])
    async def get_wallet(
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Get user's wallet balance."""
        wallet = WalletService.get_wallet(db, user.id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return wallet.to_dict()

    @app.get("/api/user/transactions", tags=["User"])
    async def get_transactions(
        limit: int = 50,
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Get user's transaction history."""
        try:
            transactions = WalletService.get_transaction_history(db, user.id, limit)
            return {
                "transactions": [t.to_dict() for t in transactions],
                "count": len(transactions),
            }
        except Exception as e:
            import logging
            logging.error(f"Error in get_transactions: {e}")
            return {"transactions": [], "count": 0}

    @app.get("/api/user/photo-history", tags=["User"])
    async def get_photo_history(
        limit: int = 50,
        offset: int = 0,
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Get user's photo processing history."""
        try:
            history = PhotoService.get_usage_history(db, user.id, limit, offset)
            total = PhotoService.get_usage_count(db, user.id)
            
            return {
                "history": [h.to_dict() for h in history],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            import logging
            logging.error(f"Error in get_photo_history: {e}")
            return {"history": [], "total": 0, "limit": limit, "offset": offset}

    @app.get("/api/user/context", tags=["User"])
    async def get_context(
        request: Request,
        db: Session = Depends(get_db),
    ):
        """Get user context with processing restrictions."""
        context = await get_user_context(request, db)
        return context.to_dict()

    # =========================================================================
    # PRICING & PAYMENTS ENDPOINTS
    # =========================================================================

    @app.get("/api/plans", tags=["Payments"])
    async def get_plans(db: Session = Depends(get_db)):
        """Get all available pricing plans."""
        plans = PlanService.get_all_plans(db)
        return {
            "plans": [p.to_dict() for p in plans],
        }

    @app.post("/api/plans/purchase", tags=["Payments"])
    async def purchase_plan(
        plan_name: str,
        payment_id: Optional[str] = None,
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Purchase a pricing plan."""
        try:
            plan_type = PlanType(plan_name)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan type. Available: {[p.value for p in PlanType if p != PlanType.FREE]}",
            )
        
        success, message = PlanService.purchase_plan(db, user.id, plan_type, payment_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}

    @app.post("/api/payments/create", tags=["Payments"])
    async def create_payment(
        plan_name: str,
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Create Instamojo payment for plan purchase."""
        from ..backend.payments import payment_service
        
        # Get plan
        plan = PlanService.get_plan_by_name(db, plan_name)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Create payment
        success, result = payment_service.create_plan_purchase_payment(
            db=db,
            user=user,
            plan=plan,
            redirect_url=f"http://localhost:7002/dashboard?payment=success",
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create payment"))
        
        return {
            "success": True,
            "payment_url": result["payment_url"],
            "payment_request_id": result["payment_request_id"],
            "order_id": result["order_id"],
        }

    @app.post("/api/payments/webhook", tags=["Payments"])
    async def payment_webhook(
        request: Request,
        db: Session = Depends(get_db),
    ):
        """Handle Instamojo payment webhook."""
        from ..backend.payments import payment_service
        
        try:
            # Get webhook data
            data = await request.form()
            data_dict = dict(data)
            
            # Process webhook
            success, message = payment_service.process_payment_webhook(db, data_dict)
            
            return {"success": success, "message": message}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @app.get("/api/payments/status/{payment_request_id}", tags=["Payments"])
    async def check_payment_status(
        payment_request_id: str,
        user = Depends(require_active_user),
        db: Session = Depends(get_db),
    ):
        """Check payment status."""
        from ..backend.payments import payment_service
        
        success, result = payment_service.check_payment_status(db, payment_request_id)
        
        if not success:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to check status"))
        
        return result

    # =========================================================================
    # MODELS ENDPOINTS
    # =========================================================================

    @app.get("/api/models", tags=["Background Removal"])
    async def get_models(
        request: Request,
        db: Session = Depends(get_db),
    ):
        """Get available models based on user status."""
        user = await get_current_user_or_none(request, db)
        
        if user and user.has_active_plan():
            # Return all active models for paid users
            models = ModelService.get_all_models(db)
        else:
            # Return only basic models for free users
            models = ModelService.get_basic_models(db)
        
        return {
            "models": [m.to_dict() for m in models],
            "is_logged_in": user is not None,
            "has_active_plan": user.has_active_plan() if user else False,
        }

    @app.get("/api/models/check", tags=["Background Removal"])
    async def check_model(
        model: str,
        request: Request,
        db: Session = Depends(get_db),
    ):
        """Check if a model is allowed for current user."""
        user = await get_current_user_or_none(request, db)
        allowed, message = ModelService.is_model_allowed(db, model, user)
        
        return {
            "allowed": allowed,
            "message": message,
        }

    # =========================================================================
    # BACKGROUND REMOVAL ENDPOINTS (with restrictions)
    # =========================================================================

    @app.get(
        path="/api/remove",
        tags=["Background Removal"],
        summary="Remove from URL",
        description="Removes the background from an image obtained by retrieving an URL.",
    )
    async def get_index(
        request: Request,
        url: str = Query(
            default=..., description="URL of the image that has to be processed."
        ),
        commons: CommonQueryParams = Depends(),
        db: Session = Depends(get_db),
    ):
        user = await get_current_user_or_none(request, db)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                file = await response.read()
                return await asyncify(im_without_bg)(file, commons, user, db)

    @app.post(
        path="/api/remove",
        tags=["Background Removal"],
        summary="Remove from Stream",
        description="Removes the background from an image sent within the request itself.",
    )
    async def post_index(
        request: Request,
        file: bytes = File(
            default=...,
            description="Image file (byte stream) that has to be processed.",
        ),
        commons: CommonQueryPostParams = Depends(),
        db: Session = Depends(get_db),
    ):
        user = await get_current_user_or_none(request, db)
        return await asyncify(im_without_bg)(file, commons, user, db)

    # =========================================================================
    # ADMIN ENDPOINTS
    # =========================================================================

    @app.get("/api/admin/users", tags=["Admin"])
    async def admin_get_users(
        skip: int = 0,
        limit: int = 100,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Get all users (admin only)."""
        from sqlalchemy import func
        from ..backend.models import User as UserModel
        
        total = db.query(func.count(UserModel.id)).scalar()
        users = db.query(UserModel).offset(skip).limit(limit).all()
        
        return {
            "users": [u.to_dict() for u in users],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @app.get("/api/admin/users/{user_id}", tags=["Admin"])
    async def admin_get_user(
        user_id: int,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Get specific user details (admin only)."""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        wallet = WalletService.get_wallet(db, user_id)
        transactions = WalletService.get_transaction_history(db, user_id, 20)
        
        return {
            "user": user.to_dict(),
            "wallet": wallet.to_dict() if wallet else None,
            "recent_transactions": [t.to_dict() for t in transactions],
        }

    @app.get("/api/admin/transactions", tags=["Admin"])
    async def admin_get_transactions(
        skip: int = 0,
        limit: int = 100,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Get all wallet transactions (admin only)."""
        from sqlalchemy import func
        from ..backend.models import WalletTransaction
        
        total = db.query(func.count(WalletTransaction.id)).scalar()
        transactions = (
            db.query(WalletTransaction)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return {
            "transactions": [t.to_dict() for t in transactions],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @app.post("/api/admin/users/{user_id}/add-credits", tags=["Admin"])
    async def admin_add_credits(
        user_id: int,
        amount: int,
        description: str = "Admin credit addition",
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Add credits to user wallet (admin only)."""
        success, message = WalletService.add_credits(
            db=db,
            user_id=user_id,
            amount=amount,
            description=description,
            payment_method="admin",
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}

    @app.put("/api/admin/plans/{plan_name}", tags=["Admin"])
    async def admin_update_plan(
        plan_name: str,
        price_inr: Optional[int] = None,
        credits: Optional[int] = None,
        is_active: Optional[bool] = None,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Update pricing plan (admin only)."""
        plan = PlanService.get_plan_by_name(db, plan_name)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if price_inr is not None:
            plan.price_inr = price_inr
        if credits is not None:
            plan.credits = credits
        if is_active is not None:
            plan.is_active = is_active
        
        db.commit()
        
        return {"success": True, "plan": plan.to_dict()}

    @app.post("/api/admin/models/{model_name}/toggle", tags=["Admin"])
    async def admin_toggle_model(
        model_name: str,
        is_active: bool,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Enable or disable AI model (admin only)."""
        success, message = ModelService.toggle_model(db, model_name, is_active)
        
        if not success:
            raise HTTPException(status_code=404, detail=message)
        
        return {"success": True, "message": message}

    @app.post("/api/admin/models/{model_name}/set-basic", tags=["Admin"])
    async def admin_set_model_basic(
        model_name: str,
        is_basic: bool,
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Set model as basic (available to free users) or advanced (admin only)."""
        success, message = ModelService.set_model_basic(db, model_name, is_basic)
        
        if not success:
            raise HTTPException(status_code=404, detail=message)
        
        return {"success": True, "message": message}

    @app.get("/api/admin/stats", tags=["Admin"])
    async def admin_get_stats(
        admin = Depends(require_admin),
        db: Session = Depends(get_db),
    ):
        """Get admin dashboard statistics."""
        from sqlalchemy import func
        from ..backend.models import User, WalletTransaction, PhotoUsage, Wallet
        
        total_users = db.query(func.count(User.id)).scalar()
        total_transactions = db.query(func.count(WalletTransaction.id)).scalar()
        total_photos_processed = db.query(func.count(PhotoUsage.id)).scalar()
        
        # Calculate total credits distributed
        total_credits = db.query(func.sum(Wallet.balance)).scalar() or 0
        
        # Recent activity
        recent_transactions = (
            db.query(WalletTransaction)
            .order_by(WalletTransaction.created_at.desc())
            .limit(10)
            .all()
        )
        
        return {
            "stats": {
                "total_users": total_users,
                "total_transactions": total_transactions,
                "total_photos_processed": total_photos_processed,
                "total_credits_in_system": total_credits,
            },
            "recent_transactions": [t.to_dict() for t in recent_transactions],
        }

    # =========================================================================
    # STATIC FILES & UI
    # =========================================================================

    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok", "message": "Server is running"}

    @app.get("/api/payments/health", tags=["Payments"])
    async def payment_health_check():
        """Check payment gateway status."""
        from ..backend.payments import INSTAMOJO_API_KEY, INSTAMOJO_AUTH_TOKEN
        return {
            "status": "ok",
            "gateway": "Instamojo",
            "api_key_configured": bool(INSTAMOJO_API_KEY),
            "auth_token_configured": bool(INSTAMOJO_AUTH_TOKEN),
        }

    @app.get("/", response_class=HTMLResponse)
    async def serve_ui(request: Request):
        user = request.session.get('user')
        
        html_path = STATIC_DIR / "index.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if user:
                user_script = f'''
                <script>
                    window.currentUser = {json.dumps(user)};
                </script>
                '''
                content = content.replace('</head>', user_script + '</head>')
            
            return content
        return HTMLResponse(content="<h1>Khan Jan Seva Kendra</h1><p>UI not found</p>")

    @app.get("/dashboard", response_class=HTMLResponse)
    async def serve_dashboard(request: Request):
        """Serve user dashboard."""
        html_path = STATIC_DIR / "dashboard.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return HTMLResponse(content="<h1>Dashboard</h1><p>Dashboard not found</p>")

    @app.get("/admin", response_class=HTMLResponse)
    async def serve_admin(request: Request):
        """Serve admin panel."""
        html_path = STATIC_DIR / "admin.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return HTMLResponse(content="<h1>Admin Panel</h1><p>Admin panel not found</p>")

    # Print startup messages
    print(
        f"🚀 Khan Jan Seva Kendra is running!"
    )
    print(
        f"📱 Web UI: http://{'localhost' if host == '0.0.0.0' else host}:{port}"
    )
    print(
        f"🔐 Login Page: http://{'localhost' if host == '0.0.0.0' else host}:{port}/login"
    )
    print(
        f"📊 Dashboard: http://{'localhost' if host == '0.0.0.0' else host}:{port}/dashboard"
    )
    print(
        f"⚙️  Admin Panel: http://{'localhost' if host == '0.0.0.0' else host}:{port}/admin"
    )
    print(
        f"📚 API Docs: http://{'localhost' if host == '0.0.0.0' else host}:{port}/api"
    )

    uvicorn.run(app, host=host, port=port, log_level=log_level)
