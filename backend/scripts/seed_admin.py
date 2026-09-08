"""
Seed an admin user into MongoDB.

Usage (from repo root):

  cd backend
  set PYTHONPATH=..   (Windows)
  python scripts/seed_admin.py

Configure in backend/.env (optional):

  ADMIN_EMAIL=admin@monjed.org
  ADMIN_PASSWORD=ChangeMe123!
  ADMIN_DISPLAY_NAME=MONJED Admin
  ADMIN_ZONE_ID=KE
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(_BACKEND_DIR / ".env")

from app.services.auth_service import hash_password
from database.connection import get_database, reset_connection
from database.users_repository import (
    create_user,
    get_user_by_email,
    update_user,
)


def main() -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@monjed.org").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "Admin123!")
    display_name = os.getenv("ADMIN_DISPLAY_NAME", "MONJED Admin").strip()
    zone_id = os.getenv("ADMIN_ZONE_ID", "KE").strip()

    if not email or "@" not in email:
        raise SystemExit("ADMIN_EMAIL must be a valid email address.")

    if len(password) < 8:
        raise SystemExit("ADMIN_PASSWORD must be at least 8 characters.")

    reset_connection()
    db = get_database()
    print(f"Connected to MongoDB database: {db.name}")

    existing = get_user_by_email(email)

    if existing is not None:
        user_id = existing.get("user_id")
        updates = {}

        if existing.get("role") != "admin":
            updates["role"] = "admin"

        if password:
            updates["password_hash"] = hash_password(password)

        if updates and user_id:
            update_user(user_id, updates)
            print(f"Updated existing account to admin: {email}")
        else:
            print(f"Admin already exists: {email}")

        print("Sign in at /volunteer -> Operations access")
        return

    user_id = f"user_{uuid4().hex}"

    create_user(
        {
            "user_id": user_id,
            "display_name": display_name,
            "email": email,
            "password_hash": hash_password(password),
            "role": "admin",
            "zone_id": zone_id,
            "country": "Kenya",
            "preferred_language": "en",
            "accessibility_needs": [],
            "notification_consent": False,
            "notifications_enabled": False,
            "organization": "MONJED Operations",
            "role_title": "Administrator",
        }
    )

    print("Admin user created.")
    print(f"  Email:    {email}")
    print(f"  Password: {password}")
    print(f"  Zone:     {zone_id}")
    print("Sign in at /volunteer -> Operations access")


if __name__ == "__main__":
    main()
