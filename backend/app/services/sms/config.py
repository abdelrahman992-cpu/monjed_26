"""
MONJED SMS Configuration

Africa's Talking credentials.
"""


import os
from pathlib import Path

from dotenv import load_dotenv


_BACKEND_DIR = Path(__file__).resolve().parents[3]

load_dotenv(_BACKEND_DIR / ".env")



AFRICAS_TALKING_USERNAME = os.getenv(
    "AFRICAS_TALKING_USERNAME"
)


AFRICAS_TALKING_API_KEY = (
    os.getenv(
        "AFRICAS_TALKING_API_KEY",
        ""
    )
    .strip()
)


AFRICAS_TALKING_SENDER_ID = os.getenv(
    "AFRICAS_TALKING_SENDER_ID"
)


# Comma-separated E.164 numbers registered in the AT sandbox dashboard.
# Used only when username=sandbox and Mongo has no eligible users.
AFRICAS_TALKING_SANDBOX_PHONES = os.getenv(
    "AFRICAS_TALKING_SANDBOX_PHONES",
    "",
).strip()

