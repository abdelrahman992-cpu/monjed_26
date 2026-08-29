from datetime import datetime, timezone

from connection import get_database
from risk_repository import create_risk_snapshot


db = get_database()

print("Database:", db.name)

now = datetime.now(timezone.utc)

data = {
    "country": "Egypt",
    "zone": "Cairo",
    "hazard": "Flood",
    "score": 75,
    "level": "high",
    "reasons": [
        "Heavy rainfall",
        "Low drainage capacity"
    ],
    "source": "AI",
    "source_timestamp": now,
    "created_at": now,
}

result = create_risk_snapshot(data)

print("Inserted ID:", result)
