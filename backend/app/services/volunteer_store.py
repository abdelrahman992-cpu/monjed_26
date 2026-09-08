from uuid import uuid4

from app.schemas.volunteer import (
    VolunteerInput,
    VolunteerRecord,
)

from database.volunteers_repository import (
    create_volunteer,
    get_volunteer as db_get_volunteer,
    get_all_volunteers as db_get_all_volunteers,
    update_volunteer,
    get_volunteer_collection,
)


# ============================================================
# HELPERS
# ============================================================


def _normalize_skills(skills: list[str]) -> list[str]:
    return list(
        dict.fromkeys(
            skill.strip()
            for skill in skills
            if skill and str(skill).strip()
        )
    )


def _document_to_record(document) -> VolunteerRecord | None:
    """Convert MongoDB document to VolunteerRecord safely."""
    if not document:
        return None

    data = dict(document)
    data.pop("_id", None)
    data.pop("linked_user_id", None)

    if data.get("zone_id"):
        data["zone_id"] = str(data["zone_id"]).strip().upper()

    if isinstance(data.get("skills"), list):
        data["skills"] = _normalize_skills(data["skills"])

    allowed = set(VolunteerRecord.model_fields.keys())
    data = {k: v for k, v in data.items() if k in allowed}

    try:
        return VolunteerRecord(**data)
    except Exception:
        return None


# ============================================================
# ADD VOLUNTEER / RESPONDER
# ============================================================


def add_volunteer(
    data: VolunteerInput,
    linked_user_id: str | None = None,
) -> VolunteerRecord:
    """
    Register volunteer or trained responder and persist in MongoDB.
    GPS coordinates are stored only for responder matching.
    """
    volunteer_data = data.model_dump()
    volunteer_data["zone_id"] = data.zone_id.strip().upper()
    volunteer_data["name"] = data.name.strip()

    if data.vehicle_type:
        volunteer_data["vehicle_type"] = data.vehicle_type.strip()
    else:
        volunteer_data["vehicle_type"] = None

    skills = _normalize_skills(data.skills)
    if "general_support" not in skills:
        skills.append("general_support")
    volunteer_data["skills"] = skills

    volunteer = VolunteerRecord(
        volunteer_id=str(uuid4()),
        **volunteer_data,
    )

    doc = volunteer.model_dump(mode="json")
    if linked_user_id:
        doc["linked_user_id"] = linked_user_id
    create_volunteer(doc)

    return volunteer


# ============================================================
# GET VOLUNTEER
# ============================================================


def get_volunteer(volunteer_id: str) -> VolunteerRecord | None:
    volunteer_id = (volunteer_id or "").strip()
    if not volunteer_id:
        return None

    document = db_get_volunteer(volunteer_id)
    return _document_to_record(document)


# ============================================================
# AVAILABLE VOLUNTEERS
# ============================================================


def get_available_volunteers(zone_id: str) -> list[VolunteerRecord]:
    """
    Returns available volunteers in same zone (case-insensitive).
    Qualification and distance ranking remain in the matching engine.
    """
    zone = (zone_id or "").strip().upper()
    volunteers = get_all_volunteers()

    return [
        volunteer
        for volunteer in volunteers
        if volunteer.available and volunteer.zone_id.strip().upper() == zone
    ]


# ============================================================
# UPDATE AVAILABILITY
# ============================================================


def set_volunteer_availability(
    volunteer_id: str,
    available: bool,
) -> VolunteerRecord | None:
    volunteer = get_volunteer(volunteer_id)
    if volunteer is None:
        return None

    update_volunteer(
        volunteer_id,
        {"available": bool(available)},
    )
    return get_volunteer(volunteer_id)


# ============================================================
# ALL VOLUNTEERS
# ============================================================


def get_all_volunteers() -> list[VolunteerRecord]:
    documents = db_get_all_volunteers()
    volunteers = []
    for document in documents:
        volunteer = _document_to_record(document)
        if volunteer is not None:
            volunteers.append(volunteer)
    return volunteers


# ============================================================
# CLEAR STORE
# ============================================================


def clear_volunteers():
    """
    Mainly intended for tests/dev resets.
    Clears MongoDB rather than temporary process memory.
    """
    collection = get_volunteer_collection()
    collection.delete_many({})
