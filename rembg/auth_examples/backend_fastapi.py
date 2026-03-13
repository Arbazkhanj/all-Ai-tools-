"""
Google One Tap Sign-In Backend - FastAPI (Python)
================================================

This backend handles Google OAuth 2.0 authentication using ID tokens.
It verifies the token, extracts user info, and manages user sessions.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

# JWT for session management
from jose import JWTError, jwt
from passlib.context import CryptContext

# ============================================
# CONFIGURATION
# ============================================

# Get from environment variables
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

app = FastAPI(title="Google One Tap Auth API")

# CORS - Allow your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7860", "http://127.0.0.1:7860", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing (if you want to add password-based auth later)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# DATABASE (Use real database in production)
# ============================================

# In-memory database for demo - Replace with PostgreSQL/MySQL
users_db = {}
sessions_db = {}

class User:
    def __init__(self, google_id, email, name, picture=None):
        self.id = secrets.token_urlsafe(16)
        self.google_id = google_id
        self.email = email
        self.name = name
        self.picture = picture
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()
        self.login_count = 1

# ============================================
# Pydantic Models
# ============================================

class GoogleTokenRequest(BaseModel):
    credential: str  # The ID token from Google
    client_id: str

class TokenResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str]
    created_at: datetime

# ============================================
# JWT TOKEN UTILITIES
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

# ============================================
# GOOGLE TOKEN VERIFICATION
# ============================================

def verify_google_token(id_token: str, client_id: str):
    """
    Verify Google ID token and return user info
    
    This validates:
    - Token signature
    - Token expiration
    - Audience (your client ID)
    - Issuer (Google)
    """
    try:
        # Verify the token with Google's public keys
        idinfo = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            client_id,
            clock_skew_in_seconds=10
        )
        
        # Check issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
        
        return idinfo
        
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

# ============================================
# USER MANAGEMENT
# ============================================

def get_or_create_user(google_user_info: dict) -> User:
    """
    Get existing user or create new one
    Implements the logic: If user exists -> login, If new -> create account
    """
    google_id = google_user_info['sub']
    email = google_user_info['email']
    name = google_user_info.get('name', email.split('@')[0])
    picture = google_user_info.get('picture')
    
    # Check if user exists by Google ID
    existing_user = None
    for user in users_db.values():
        if user.google_id == google_id:
            existing_user = user
            break
    
    if existing_user:
        # Update last login
        existing_user.last_login = datetime.utcnow()
        existing_user.login_count += 1
        if picture:
            existing_user.picture = picture
        print(f"User logged in: {email} (Login #{existing_user.login_count})")
        return existing_user
    else:
        # Create new user
        new_user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture
        )
        users_db[new_user.id] = new_user
        print(f"New user created: {email}")
        return new_user

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    return users_db.get(user_id)

# ============================================
# API ENDPOINTS
# ============================================

@app.post("/auth/google/token", response_model=TokenResponse)
async def google_auth(request: GoogleTokenRequest):
    """
    Handle Google One Tap / Sign-In token
    
    Flow:
    1. Verify Google ID token
    2. Get or create user
    3. Create session (JWT)
    4. Return token and user info
    """
    try:
        # Step 1: Verify Google token
        google_user_info = verify_google_token(request.credential, request.client_id)
        
        if not google_user_info:
            return TokenResponse(
                success=False,
                message="Invalid Google token"
            )
        
        # Step 2: Get or create user
        user = get_or_create_user(google_user_info)
        
        # Step 3: Create JWT token
        access_token = create_access_token(data={
            "sub": user.id,
            "email": user.email,
            "name": user.name
        })
        
        # Step 4: Return response
        return TokenResponse(
            success=True,
            message="Authentication successful",
            token=access_token,
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "created_at": user.created_at.isoformat(),
                "is_new": user.login_count == 1
            }
        )
        
    except Exception as e:
        print(f"Auth error: {e}")
        return TokenResponse(
            success=False,
            message="Authentication failed"
        )

@app.get("/auth/me")
async def get_current_user(request: Request):
    """
    Get current logged-in user info
    Requires valid JWT token in Authorization header
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get('sub')
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "last_login": user.last_login.isoformat()
    }

@app.get("/auth/logout")
async def logout(request: Request):
    """Logout user (client should also clear localStorage)"""
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        # In production, add token to blacklist
        
    return JSONResponse(content={"success": True, "message": "Logged out successfully"})

@app.get("/auth/users")
async def list_users():
    """Admin endpoint - list all users (for debugging)"""
    return {
        "total_users": len(users_db),
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "login_count": u.login_count,
                "last_login": u.last_login.isoformat()
            }
            for u in users_db.values()
        ]
    }

# ============================================
# PROTECTED ROUTE EXAMPLE
# ============================================

@app.get("/api/protected")
async def protected_route(request: Request):
    """Example of a protected route that requires authentication"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "message": "This is a protected route",
        "user": payload.get('email'),
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Google One Tap Auth API Server")
    print("=" * 50)
    print(f"JWT Secret: {JWT_SECRET_KEY[:10]}...")
    print(f"Google Client ID: {GOOGLE_CLIENT_ID[:20]}..." if GOOGLE_CLIENT_ID != 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com' else "⚠️  Google Client ID not configured!")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
