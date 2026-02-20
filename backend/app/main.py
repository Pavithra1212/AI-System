import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pathlib import Path

from app.database import engine, Base, SessionLocal
from app.seed import seed_users
from app.websocket_manager import manager
from app.routes.auth_routes import router as auth_router
from app.routes.report_routes import router as report_router
from app.routes.admin_routes import router as admin_router
from app.config import DEBUG, UPLOAD_DIR, ALLOWED_ORIGINS

# ── Logging ───────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Security Headers Middleware ───────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if not DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# ── Lifespan ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Application shutting down")


# ── FastAPI App ───────────────────────────────────
app = FastAPI(
    title="AI Campus Lost & Found",
    version="1.0.0",
    debug=DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# ── CORS ──────────────────────────────────────────
# In debug: allow all origins for local development
# In production: use ALLOWED_ORIGINS env var (comma-separated)
cors_origins = ["*"] if DEBUG else (ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Security Headers ─────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# ── API Routes ────────────────────────────────────
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(admin_router)

# ── Static Files ──────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

# ── Health Check ─────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health endpoint for Railway / Docker / load-balancer probes."""
    return {"status": "ok", "version": "1.0.0"}


# ── Global Error Handler ─────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )



# ── WebSocket ─────────────────────────────────────
@app.websocket("/ws/admin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


# ── Frontend Routes ───────────────────────────────
@app.get("/")
async def serve_login():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/student")
async def serve_student():
    return FileResponse(str(FRONTEND_DIR / "student.html"))


@app.get("/admin")
async def serve_admin():
    return FileResponse(str(FRONTEND_DIR / "admin.html"))
