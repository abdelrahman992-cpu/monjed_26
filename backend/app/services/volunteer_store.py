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

def _normalize_skills(
    skills: list[str],
) -> list[str]:

    return list(
        dict.fromkeys(
            skill.strip()
            for skill in skills
            if skill and skill.strip()
        )
    )


def _document_to_record(
    document,
) -> VolunteerRecord | None:
    """
    Convert MongoDB document to VolunteerRecord safely.
    """

    if not document:
        return None

    data = dict(document)

    # Mongo internal field must never leak to API schema
    data.pop("_id", None)

    return VolunteerRecord(
        **data
    )


# ============================================================
# ADD VOLUNTEER / RESPONDER
# ============================================================

def add_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:
    """
    Register volunteer or trained responder
    and persist the profile in MongoDB.

    GPS coordinates are stored only for responder matching.
    """

    volunteer_data = data.model_dump()

    # Normalize zone
    volunteer_data["zone_id"] = (
        data.zone_id.strip()
    )

    # Normalize name
    volunteer_data["name"] = (
        data.name.strip()
    )

    # Normalize vehicle
    if data.vehicle_type:
        volunteer_data["vehicle_type"] = (
            data.vehicle_type.strip()
        )
    else:
        volunteer_data["vehicle_type"] = None

    # Normalize skills
    volunteer_data["skills"] = (
        _normalize_skills(
            data.skills
        )
    )

    volunteer = VolunteerRecord(
        volunteer_id=str(
            uuid4()
        ),
        **volunteer_data,
    )

    # Store plain serializable data in MongoDB
    create_volunteer(
        volunteer.model_dump()
    )

    return volunteer


# ============================================================
# GET VOLUNTEER
# ============================================================

def get_volunteer(
    volunteer_id: str,
) -> VolunteerRecord | None:

    volunteer_id = (
        volunteer_id.strip()
    )

    if not volunteer_id:
        return None

    document = db_get_volunteer(
        volunteer_id
    )

    return _document_to_record(
        document
    )


# ============================================================
# AVAILABLE VOLUNTEERS
# ============================================================

def get_available_volunteers(
    zone_id: str,
) -> list[VolunteerRecord]:
    """
    Returns available volunteers in same zone.

    Qualification and distance ranking remain handled
    by the volunteer matching engine.
    """

    zone_id = zone_id.strip()

    volunteers = get_all_volunteers()

    return [
        volunteer
        for volunteer in volunteers
        if (
            volunteer.available
            and
            volunteer.zone_id.strip() == zone_id
        )
    ]


# ============================================================
# UPDATE AVAILABILITY
# ============================================================

def set_volunteer_availability(
    volunteer_id: str,
    available: bool,
) -> VolunteerRecord | None:

    volunteer = get_volunteer(
        volunteer_id
    )

    if volunteer is None:
        return None

    update_volunteer(
        volunteer_id,
        {
            "available": bool(
                available
            )
        },
    )

    return get_volunteer(
        volunteer_id
    )


# ============================================================
# ALL VOLUNTEERS
# ============================================================

def get_all_volunteers() -> list[VolunteerRecord]:

    documents = db_get_all_volunteers()

    volunteers = []

    for document in documents:

        volunteer = _document_to_record(
            document
        )

        if volunteer is not None:
            volunteers.append(
                volunteer
            )

    return volunteers


# ============================================================
# CLEAR STORE
# ============================================================

def clear_volunteers():
    """
    Mainly intended for tests/dev resets.

    Unlike the old implementation, this clears MongoDB
    rather than temporary process memory.
    """

    collection = get_volunteer_collection()

    collection.delete_many({})