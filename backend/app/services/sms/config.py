# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parents[3]
env_path = _BACKEND_DIR / ".env"

if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

AFRICAS_TALKING_USERNAME = os.getenv("AFRICAS_TALKING_USERNAME", "").strip()
AFRICAS_TALKING_API_KEY = os.getenv("AFRICAS_TALKING_API_KEY", "").strip()
AFRICAS_TALKING_SENDER_ID = os.getenv("AFRICAS_TALKING_SENDER_ID", "").strip()
AFRICAS_TALKING_SANDBOX_PHONES = os.getenv("AFRICAS_TALKING_SANDBOX_PHONES", "").strip()