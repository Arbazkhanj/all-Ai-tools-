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
from fastapi import Depends, FastAPI, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

from .. import __version__
from ..bg import remove
from ..session_factory import new_session
from ..sessions import sessions_names
from ..sessions.base import BaseSession

# Get the path to the static files
STATIC_DIR = Path(__file__).parent.parent / "static"

# OAuth setup
oauth = OAuth()

# Get Google OAuth credentials from environment or use provided Client ID
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '894379656916-rtiufltvtpemq1fu8mpi0guq5hm486lc.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

# Demo mode flag - when True, uses mock authentication
# For Google One Tap, we only need Client ID (Secret is for server-side OAuth)
DEMO_MODE = GOOGLE_CLIENT_ID == 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'

if not DEMO_MODE:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@click.command(  # type: ignore
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
    secret_key = secrets.token_urlsafe(32)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)
    
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

    def im_without_bg(content: bytes, commons: CommonQueryParams) -> Response:
        kwargs = {}

        if commons.extras:
            try:
                kwargs.update(json.loads(commons.extras))
            except Exception:
                pass

        session = sessions.get(commons.model)
        if session is None:
            session = new_session(commons.model, **kwargs)
            sessions[commons.model] = session

        return Response(
            remove(
                content,
                session=session,
                alpha_matting=commons.a,
                alpha_matting_foreground_threshold=commons.af,
                alpha_matting_background_threshold=commons.ab,
                alpha_matting_erode_size=commons.ae,
                only_mask=commons.om,
                post_process_mask=commons.ppm,
                bgcolor=commons.bgc,
                **kwargs,
            ),
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

    # Auth routes
    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        html_path = STATIC_DIR / "login.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        return HTMLResponse(content="<h1>Login</h1><p>Login page not found</p>")

    @app.get("/auth/google")
    async def auth_google(request: Request):
        if DEMO_MODE:
            # In demo mode, create a mock user
            request.session['user'] = {
                'email': 'demo@khanjanseva.com',
                'name': 'Demo User',
                'picture': None,
                'sub': 'demo123'
            }
            return RedirectResponse(url='/')
        
        redirect_uri = request.url_for('auth_google_callback')
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @app.get("/auth/callback")
    async def auth_google_callback(request: Request):
        if DEMO_MODE:
            return RedirectResponse(url='/')
        
        try:
            token = await oauth.google.authorize_access_token(request)
            user = token.get('userinfo')
            if user:
                request.session['user'] = dict(user)
            return RedirectResponse(url='/')
        except Exception as e:
            return HTMLResponse(content=f"<h1>Authentication Error</h1><p>{str(e)}</p><a href='/login'>Try Again</a>")

    @app.get("/auth/logout")
    async def auth_logout(request: Request):
        request.session.pop('user', None)
        return RedirectResponse(url='/login')

    @app.get("/auth/me")
    async def auth_me(request: Request):
        user = request.session.get('user')
        if not user:
            return Response(content='{"error": "Not authenticated"}', media_type="application/json", status_code=401)
        return Response(content=json.dumps(user), media_type="application/json")

    # Google One Tap token verification endpoint
    @app.post("/auth/google/token")
    async def auth_google_token(request: Request):
        """
        Handle Google One Tap / Sign-In token
        Receives the ID token from frontend and verifies it
        """
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
        
        try:
            body = await request.json()
            id_token_str = body.get('credential')
            client_id = body.get('client_id', GOOGLE_CLIENT_ID)
            
            if not id_token_str:
                return Response(
                    content=json.dumps({"success": False, "message": "Missing credential"}),
                    media_type="application/json",
                    status_code=400
                )
            
            # In demo mode or if no Google credentials configured, accept any token
            if DEMO_MODE:
                # Create mock user from token payload (without verification for demo)
                import base64
                try:
                    # Try to decode payload part of JWT for demo
                    parts = id_token_str.split('.')
                    if len(parts) == 3:
                        # Add padding if needed
                        padding = 4 - len(parts[1]) % 4
                        if padding != 4:
                            parts[1] += '=' * padding
                        payload = json.loads(base64.urlsafe_b64decode(parts[1]))
                        user = {
                            'id': payload.get('sub', 'demo123'),
                            'email': payload.get('email', 'user@example.com'),
                            'name': payload.get('name', 'Google User'),
                            'picture': payload.get('picture'),
                            'is_new': False
                        }
                    else:
                        # Generate random demo user
                        import random
                        user_num = random.randint(1000, 9999)
                        user = {
                            'id': f'demo{user_num}',
                            'email': f'user{user_num}@example.com',
                            'name': f'Demo User {user_num}',
                            'picture': None,
                            'is_new': True
                        }
                except Exception as e:
                    # Generate random demo user on error
                    import random
                    user_num = random.randint(1000, 9999)
                    user = {
                        'id': f'demo{user_num}',
                        'email': f'user{user_num}@example.com',
                        'name': f'Demo User {user_num}',
                        'picture': None,
                        'is_new': True
                    }
                
                request.session['user'] = user
                return Response(content=json.dumps({
                    "success": True,
                    "message": "Authentication successful (Demo Mode)",
                    "token": id_token_str[:50] + "...",
                    "user": user
                }), media_type="application/json")
            
            # Real Google token verification
            try:
                idinfo = google_id_token.verify_oauth2_token(
                    id_token_str,
                    google_requests.Request(),
                    client_id,
                    clock_skew_in_seconds=10
                )
                
                # Check issuer
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Invalid issuer')
                
                # Create user from verified token
                user = {
                    'id': idinfo['sub'],
                    'email': idinfo['email'],
                    'name': idinfo.get('name', idinfo['email'].split('@')[0]),
                    'picture': idinfo.get('picture'),
                    'is_new': True  # You would check your database here
                }
                
                request.session['user'] = user
                
                return Response(content=json.dumps({
                    "success": True,
                    "message": "Authentication successful",
                    "user": user
                }), media_type="application/json")
                
            except Exception as e:
                return Response(
                    content=json.dumps({"success": False, "message": f"Token verification failed: {str(e)}"}),
                    media_type="application/json",
                    status_code=401
                )
                
        except Exception as e:
            return Response(
                content=json.dumps({"success": False, "message": str(e)}),
                media_type="application/json",
                status_code=500
            )

    # Serve custom UI
    @app.get("/", response_class=HTMLResponse)
    async def serve_ui(request: Request):
        # Check if user is logged in
        user = request.session.get('user')
        
        html_path = STATIC_DIR / "index.html"
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Inject user info if logged in
            if user:
                user_script = f'''
                <script>
                    window.currentUser = {json.dumps(user)};
                </script>
                '''
                content = content.replace('</head>', user_script + '</head>')
            
            return content
        return HTMLResponse(content="<h1>Khan Jan Seva Kendra</h1><p>UI not found</p>")

    @app.get(
        path="/api/remove",
        tags=["Background Removal"],
        summary="Remove from URL",
        description="Removes the background from an image obtained by retrieving an URL.",
    )
    async def get_index(
        url: str = Query(
            default=..., description="URL of the image that has to be processed."
        ),
        commons: CommonQueryParams = Depends(),
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                file = await response.read()
                return await asyncify(im_without_bg)(file, commons)

    @app.post(
        path="/api/remove",
        tags=["Background Removal"],
        summary="Remove from Stream",
        description="Removes the background from an image sent within the request itself.",
    )
    async def post_index(
        file: bytes = File(
            default=...,
            description="Image file (byte stream) that has to be processed.",
        ),
        commons: CommonQueryPostParams = Depends(),
    ):
        return await asyncify(im_without_bg)(file, commons)  # type: ignore

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
        f"📚 API Docs: http://{'localhost' if host == '0.0.0.0' else host}:{port}/api"
    )
    
    if DEMO_MODE:
        print(
            f"⚠️  DEMO MODE: Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars."
        )
        print(
            f"   Using mock authentication for testing."
        )

    uvicorn.run(app, host=host, port=port, log_level=log_level)
