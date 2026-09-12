from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional, List

# استيراد دالة الاتصال المباشرة بقاعدة البيانات
from database.connection import get_database


# ============================================================
# COLLECTION
# ============================================================

def get_users_collection():
    """Returns the users collection instance from MongoDB."""
    db = get_database()
    return db["users"]


# ============================================================
# CREATE
# ============================================================

def create_user(data: Dict[str, Any]) -> str:
    """Inserts a new user record into the database."""
    collection = get_users_collection()
    
    # ضمان وجود القيم الافتراضية للتحقق
    data.setdefault("is_verified", False)
    data.setdefault("two_factor_enabled", False)
    now = datetime.now(timezone.utc)

    data.setdefault("created_at", now)
    data.setdefault("updated_at", now)
    
    collection.insert_one(data)
    return data.get("user_id", "")


# ============================================================
# VERIFICATION OPERATIONS (EMAIL OTP)
# ============================================================

def mark_user_as_verified(user_id: str) -> bool:
    """
    تفعيل حساب المستخدم رسمياً بعد إدخال كود الـ OTP الصحيح.
    """
    if not user_id:
        return False
        
    collection = get_users_collection()
    result = collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "is_verified": True,
                "verified_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    return result.modified_count > 0


# ============================================================
# GET BY USER ID
# ============================================================

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by unique user_id."""
    if not user_id:
        return None
    collection = get_users_collection()
    return collection.find_one({"user_id": user_id})


# ============================================================
# GET BY EMAIL
# ============================================================

def get_user_by_email(email: Optional[str]) -> Optional[Dict[str, Any]]:
    """Fetch user by email or work_email (case-insensitive)."""
    if not email:
        return None

    normalized_email = str(email).strip().lower()
    if not normalized_email:
        return None

    collection = get_users_collection()
    return collection.find_one(
        {
            "$or": [
                {"email": normalized_email},
                {"work_email": normalized_email},
            ]
        }
    )


# ============================================================
# GET BY PHONE
# ============================================================

def get_user_by_phone(phone: Optional[str]) -> Optional[Dict[str, Any]]:
    """Fetch user by primary phone or alternative phone_number."""
    if not phone:
        return None

    normalized_phone = str(phone).strip()
    if not normalized_phone:
        return None

    collection = get_users_collection()
    return collection.find_one(
        {
            "$or": [
                {"phone": normalized_phone},
                {"phone_number": normalized_phone},
            ]
        }
    )


# ============================================================
# ALL USERS
# ============================================================

def get_all_users() -> List[Dict[str, Any]]:
    """Retrieve all user records."""
    collection = get_users_collection()
    return list(collection.find())


# ============================================================
# USERS BY ZONE
# ============================================================

def get_users_by_zone(zone_id: str) -> List[Dict[str, Any]]:
    """Retrieve all users bound to a specific zone."""
    if not zone_id:
        return []
    collection = get_users_collection()
    return list(collection.find({"zone_id": zone_id}))


# ============================================================
# ALERT RECIPIENTS
# ============================================================

def get_alert_recipients_by_zone(zone_id: str) -> List[Dict[str, Any]]:
    """
    Return users who explicitly consented to notifications
    and have a valid stored phone number.
    """
    if not zone_id:
        return []

    collection = get_users_collection()

    users = list(
        collection.find(
            {
                "zone_id": zone_id,
                "$and": [
                    {
                        "$or": [
                            {"notification_consent": True},
                            {"notifications_enabled": True},
                        ]
                    },
                    {
                        "$or": [
                            {
                                "phone": {
                                    "$exists": True,
                                    "$nin": [None, ""],
                                }
                            },
                            {
                                "phone_number": {
                                    "$exists": True,
                                    "$nin": [None, ""],
                                }
                            },
                        ]
                    },
                ],
            }
        )
    )

    recipients = []

    for user in users:
        phone = user.get("phone") or user.get("phone_number")
        if not phone:
            continue

        recipients.append(
            {
                "user_id": user.get("user_id"),
                "phone": phone,
                "zone_id": user.get("zone_id"),
                "preferred_language": user.get("preferred_language", "en"),
                "accessibility_needs": user.get("accessibility_needs", []),
            }
        )

    return recipients


# ============================================================
# PHONE NUMBERS ONLY
# Legacy compatibility helper
# ============================================================

def get_recipient_phone_numbers(zone_id: str) -> List[str]:
    """Extract distinct recipient phone numbers for emergency alerts."""
    recipients = get_alert_recipients_by_zone(zone_id)
    numbers = []

    for recipient in recipients:
        phone = recipient.get("phone")
        if phone and phone not in numbers:
            numbers.append(phone)

    return numbers


# ============================================================
# UPDATE
# ============================================================

def update_user(user_id: str, data: Dict[str, Any]) -> int:
    """Update user payload by user_id."""
    if not user_id or not data:
        return 0
    collection = get_users_collection()
    
    data["updated_at"] = datetime.now(timezone.utc)
    result = collection.update_one({"user_id": user_id}, {"$set": data})
    return result.modified_count


# ============================================================
# DELETE
# ============================================================

def delete_user(user_id: str) -> int:
    """Remove user by user_id."""
    if not user_id:
        return 0
    collection = get_users_collection()
    result = collection.delete_one({"user_id": user_id})
    return result.deleted_count


# ============================================================
# GUEST AUTOMATIC CREATION
# ============================================================

def get_or_create_guest_user(phone_number: str) -> Dict[str, Any]:
    """
    Search for user by phone. If not found, create a temporary Guest user.
    """
    if not phone_number:
        raise ValueError("Phone number is required to create a guest account")

    normalized_phone = str(phone_number).strip()

    existing_user = get_user_by_phone(normalized_phone)
    if existing_user:
        return existing_user

    collection = get_users_collection()
    guest_id = f"guest_{uuid.uuid4().hex[:8]}"

    guest_user = {
        "user_id": guest_id,
        "phone": normalized_phone,
        "phone_number": normalized_phone,
        "is_guest": True,
        "is_verified": False,
        "status": "pending_completion",
        "notification_consent": True,
        "two_factor_enabled": False,
        "created_at": datetime.now(timezone.utc),
    }

    collection.insert_one(guest_user)
    return guest_user
