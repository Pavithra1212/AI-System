import os
import sys
import secrets
import logging
from pathlib import Path

_config_logger = logging.getLogger("app.config")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug — defaults to False (production-safe)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Server port — Railway, Render, Heroku inject $PORT at runtime
PORT = int(os.getenv("PORT", "8000"))

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-insecure-key-do-not-use-in-production"
    else:
        SECRET_KEY = secrets.token_hex(32)
        _config_logger.warning(
            "⚠️  SECRET_KEY not set! Generated a random key. "
            "JWTs will be invalidated on every restart. "
            "Set SECRET_KEY in your Railway environment variables!"
        )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'lost_found.db'}")

# CORS — comma-separated origins allowed in production
# Example: ALLOWED_ORIGINS=https://myapp.up.railway.app,https://mydomain.com
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Uploads
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(5 * 1024 * 1024)))  # 5 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# AI Matching
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.70"))
IMAGE_WEIGHT = float(os.getenv("IMAGE_WEIGHT", "0.4"))
TEXT_WEIGHT = float(os.getenv("TEXT_WEIGHT", "0.6"))
