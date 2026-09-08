"""Set Hussein volunteer GPS to Kisumu (not Meru/zone centroid)."""
from database.connection import reset_connection, get_database

reset_connection()
db = get_database()

kisumu = {"latitude": -0.0917, "longitude": 34.768, "base_location": "Kisumu"}

r = db["volunteers"].update_many(
    {"name": {"$regex": "^Hussein$", "$options": "i"}},
    {"$set": kisumu},
)
print("volunteers updated", r.modified_count)

r2 = db["users"].update_many(
    {"display_name": {"$regex": "^Hussein$", "$options": "i"}},
    {"$set": {"latitude": -0.0917, "longitude": 34.768, "zone_label": "Kisumu"}},
)
print("users updated", r2.modified_count)

for v in db["volunteers"].find({"name": {"$regex": "hussein", "$options": "i"}}):
    print(
        v.get("name"),
        v.get("latitude"),
        v.get("longitude"),
        v.get("base_location"),
        v.get("zone_id"),
    )
