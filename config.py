import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration. Values are read from environment variables so that
    no secrets are ever hard-coded into source control."""

    # Flask secret key used to sign session cookies. MUST be overridden in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-in-production")

    # Database configuration.
    # Locally this defaults to a SQLite file inside the instance/ folder.
    # On Render, set DATABASE_URL to a persistent disk path or a managed Postgres URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'finance.db')}"
    )
    # Render/Heroku style URLs sometimes start with postgres:// which SQLAlchemy 1.4+ rejects.
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session / cookie security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    # Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    # App-level constants
    CURRENCY_SYMBOL = "\u20b9"  # INR symbol
    EXPENSE_CATEGORIES = [
        "Rent", "Food", "Transport", "Entertainment",
        "Education", "Healthcare", "Utilities", "Other",
    ]
    INCOME_CATEGORIES = [
        "Salary", "Freelance", "Allowance", "Business", "Investment", "Other",
    ]
    USER_TYPES = ["Student", "Salaried", "Freelancer", "Household"]
