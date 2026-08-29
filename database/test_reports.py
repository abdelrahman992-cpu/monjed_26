from datetime import datetime, timezone

from connection import get_database
from reports_repository import create_report


db = get_database()

print("Database:", db.name)

now = datetime.now(timezone.utc)

data = {
    "report_id": "REP-001",
    "type": "Flood",
    "country": "Egypt",
    "zone": "Cairo",
    "location": {
        "type": "Point",
        "coordinates": [31.2357, 30.0444],
        "address": "Cairo, Egypt"
    },
    "confidence": 85,
    "status": "pending",
    "created_at": now,
    "updated_at": now
}

result = create_report(data)

print("Inserted Report ID:", result)
