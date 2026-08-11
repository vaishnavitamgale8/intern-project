"""Application configuration for ImpactBridge AI.

All settings can be overridden via environment variables so the app
can be deployed anywhere (local dev, university server, etc.) with
zero code changes.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    JSON_SORT_KEYS = False

    # Database – SQLite by default so the project runs anywhere instantly
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'impactbridge.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER", str(BASE_DIR / "app" / "static" / "uploads")
    )
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 16)) * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

    # Site
    SITE_NAME = os.environ.get("SITE_NAME", "ImpactBridge AI")
    SITE_TAGLINE = os.environ.get(
        "SITE_TAGLINE", "Connecting People. Creating Impact."
    )

    # Local AI (Ollama)
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
    # Set OLLAMA_ENABLED=true in .env to use Ollama live answers;
    # otherwise the built-in rule-based fallback engine is used.
    OLLAMA_ENABLED = os.environ.get("OLLAMA_ENABLED", "false").lower() in ("1", "true", "yes", "on")

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Pagination
    PER_PAGE = 12


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    UPLOAD_FOLDER = str(BASE_DIR / "tests" / "tmp_uploads")


class ProductionConfig(Config):
    DEBUG = False


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "development").lower()
    return {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }.get(env, DevelopmentConfig)()