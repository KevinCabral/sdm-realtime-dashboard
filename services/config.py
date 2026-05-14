import os
import secrets
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8050"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
REFRESH_INTERVAL_MS = int(os.getenv("REFRESH_INTERVAL_MS", "5000"))

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://user:password@postgres:5432/election")
REST_API_BASE_URL = os.getenv("REST_API_BASE_URL", "https://api.example.com")
CSV_DATA_PATH = os.getenv("CSV_DATA_PATH", "data/authorised_voters.csv")
REALTIME_BACKEND = os.getenv("REALTIME_BACKEND", "polling")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.warning("SECRET_KEY not set; using an ephemeral key. Set SECRET_KEY in .env for stable secure sessions.")
    SECRET_KEY = secrets.token_urlsafe(32)
