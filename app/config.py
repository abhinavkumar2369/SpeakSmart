import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Database
    DATABASE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "speaksmart.db",
    )

    # Google Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Flask
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    PORT = int(os.getenv("FLASK_PORT", 5000))
