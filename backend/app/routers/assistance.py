from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List

from app.schemas.assistance import (
    AssistanceRequestInput,
    AssistanceRequestRecord,
    DistressRequest,
)

from app.schemas.volunteer import (
    VolunteerAvailabilityUpdate,
    VolunteerInput,
    VolunteerRecord,
)

from app.services.assistance_store import (
    create_assistance_request,
    get_request,
    get_pending_requests,
    get_all_requests,
    assign_request,
    start_request,
    resolve_request,
)

from app.services.volunteer_store import (
    add_volunteer,
    get_all_volunteers,
    get_available_volunteers,
    get_volunteer,
    set_volunteer_availability,
)

from app.engines.volunteer_matching import match_volunteer

# Repositories & Services for Automatic Guest handling
from database.users_repository import get_or_create_guest_user
from app.services.sms.sms_service import send_alert_sms as send_sms


# ============================================================
# ROUTER CONFIGURATION
# ============================================================

router = APIRouter(
    prefix="/assistance",
    tags=["Assistance & Volunteers"],
)


# ============================================================
# HELPERS
# ============================================================

def _get_request_or_404(request_id: str) -> AssistanceRequestRecord:
    request = get_request(request_id)
    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Assistance request not found.",
        )
    return request


def _requires_trained_responder(request: AssistanceRequestRecord) -> bool:
    return (
        request.requires_trained_responder
        or request.request_type == "rescue_support"
    )


# ============================================================
# DIRECT DISTRESS & GUEST WORKFLOW
# ============================================================

@router.post("/distress", response_model=dict)
async def create_distress_signal(
    payload: DistressRequest, 
    background_tasks: BackgroundTasks
):
    """
    Rapid distress endpoint.
    Automatically provisions/fetches a Guest account via phone number 
    and logs the emergency request.
    """
    # 1. Automatic Guest Account Provisioning
    user = get_or_create_guest_user(payload.phone)

    # 2. Build Assistance Request Payload
    assistance_input = AssistanceRequestInput(
        zone_id="emergency_default",
        location=f"GPS ({payload.latitude}, {payload.longitude})" if payload.latitude else "Unknown Location",
        latitude=payload.latitude,
        longitude=payload.longitude,
        hazard="flood",  # Default system emergency classification
        request_type="rescue_support",
        priority="critical",
        description=payload.details or "Direct distress signal submitted via guest flow.",
        requester_phone=payload.phone
    )

    # 3. Create Record
    record = create_assistance_request(assistance_input)

    # 4. Dispatch SMS Confirmation
    confirmation_msg = f"Emergency request received. ID: {record.request_id}. Help is on the way."
    background_tasks.add_task(send_sms, payload.phone, confirmation_msg)

    return {
        "status": "success",
        "guest_id": user.get("user_id"),
        "request_id": record.request_id,
        "message": "Distress request logged and responders notified."
    }


# ============================================================
# REGISTER VOLUNTEER
# ============================================================

@router.post(
    "/volunteers",
    response_model=VolunteerRecord,
)
def register_volunteer(
    data: VolunteerInput,
) -> VolunteerRecord:
    return add_volunteer(data)


# ============================================================
# LIST VOLUNTEERS
# ============================================================

@router.get(
    "/volunteers",
    response_model=List[VolunteerRecord],
)
def list_volunteers(
    available: Optional[bool] = None,
    zone_id: Optional[str] = None,
) -> List[VolunteerRecord]:
    """
    Return volunteers/responders for the frontend/admin panel.
    Optional query filters: available, zone_id.
    """
    volunteers = get_all_volunteers()

    if zone_id is not None:
        normalized_zone = zone_id.strip()
        volunteers = [
            volunteer
            for volunteer in volunteers
            if volunteer.zone_id.strip().upper() == normalized_zone.upper()
        ]

    if available is not None:
        volunteers = [
            v for v in volunteers if v.available == available
        ]

    return volunteers


# ============================================================
# UPDATE VOLUNTEER AVAILABILITY
# ============================================================

@router.patch(
    "/volunteers/{volunteer_id}",
    response_model=VolunteerRecord,
)
def update_volunteer_availability(
    volunteer_id: str,
    data: VolunteerAvailabilityUpdate,
) -> VolunteerRecord:
    volunteer = get_volunteer(volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404,
            detail="Volunteer or responder not found.",
        )

    updated = set_volunteer_availability(
        volunteer_id=volunteer.volunteer_id,
        available=data.available,
    )

    if updated is None:
        raise HTTPException(
            status_code=500,
            detail="Volunteer availability could not be updated.",
        )

    return updated


# ============================================================
# VOLUNTEER INBOX
# ============================================================

@router.get(
    "/volunteers/{volunteer_id}/requests",
    response_model=List[AssistanceRequestRecord],
)
def volunteer_requests(
    volunteer_id: str,
) -> List[AssistanceRequestRecord]:
    volunteer = get_volunteer(volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404,
            detail="Volunteer or responder not found.",
        )

    return [
        req for req in get_all_requests()
        if req.assigned_volunteer_id == volunteer.volunteer_id
    ]


# ============================================================
# CREATE REQUEST
# ============================================================

@router.post(
    "/requests",
    response_model=AssistanceRequestRecord,
)
def create_request(
    data: AssistanceRequestInput,
) -> AssistanceRequestRecord:
    return create_assistance_request(data)


# ============================================================
# LIST ALL REQUESTS (OPS)
# ============================================================

@router.get(
    "/requests",
    response_model=List[AssistanceRequestRecord],
)
def list_requests(
    status: Optional[str] = None,
) -> List[AssistanceRequestRecord]:
    requests = get_all_requests()

    if status is not None:
        normalized = status.strip().lower()
        requests = [
            req for req in requests if req.status == normalized
        ]

    return requests


# ============================================================
# GET PENDING REQUESTS
# NOTE: Must be registered before /requests/{request_id}
# ============================================================

@router.get(
    "/requests/pending",
    response_model=List[AssistanceRequestRecord],
)
def pending_requests():
    return get_pending_requests()


# ============================================================
# GET REQUEST BY ID
# ============================================================

@router.get(
    "/requests/{request_id}",
    response_model=AssistanceRequestRecord,
)
def read_request(
    request_id: str,
):
    return _get_request_or_404(request_id)


# ============================================================
# MATCH REQUEST WITH RESPONDER
# ============================================================

@router.post(
    "/requests/{request_id}/match",
    response_model=AssistanceRequestRecord,
)
def match_request(
    request_id: str,
):
    request = _get_request_or_404(request_id)

    if request.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Only pending requests can be matched.",
        )

    volunteers = get_available_volunteers(request.zone_id)
    if not volunteers:
        raise HTTPException(
            status_code=404,
            detail="No available responders found in this zone.",
        )

    volunteer = match_volunteer(
        request=request,
        volunteers=volunteers,
    )

    if volunteer is None:
        if _requires_trained_responder(request):
            raise HTTPException(
                status_code=404,
                detail="No qualified trained responder is currently available.",
            )
        raise HTTPException(
            status_code=404,
            detail="No qualified volunteer matches the required capabilities.",
        )

    assigned = assign_request(
        request_id=request.request_id,
        volunteer_id=volunteer.volunteer_id,
    )

    if assigned is None:
        raise HTTPException(
            status_code=409,
            detail="Request assignment failed.",
        )

    updated = set_volunteer_availability(
        volunteer_id=volunteer.volunteer_id,
        available=False,
    )

    if updated is None:
        raise HTTPException(
            status_code=500,
            detail="Responder availability update failed.",
        )

    return assigned


# ============================================================
# START REQUEST WORKFLOW
# ============================================================

@router.post(
    "/requests/{request_id}/start",
    response_model=AssistanceRequestRecord,
)
def start_assistance_request(
    request_id: str,
):
    request = _get_request_or_404(request_id)

    if request.status != "assigned":
        raise HTTPException(
            status_code=409,
            detail="Only assigned requests can be started.",
        )

    if not request.assigned_volunteer_id:
        raise HTTPException(
            status_code=409,
            detail="No responder assigned.",
        )

    volunteer = get_volunteer(request.assigned_volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=409,
            detail="Assigned responder not found.",
        )

    started = start_request(request_id)
    if started is None:
        raise HTTPException(
            status_code=409,
            detail="Request could not be started.",
        )

    return started


# ============================================================
# RESOLVE REQUEST WORKFLOW
# ============================================================

@router.post(
    "/requests/{request_id}/resolve",
    response_model=AssistanceRequestRecord,
)
def resolve_assistance_request(
    request_id: str,
):
    request = _get_request_or_404(request_id)

    if request.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Only active requests can be resolved.",
        )

    volunteer_id = request.assigned_volunteer_id
    if not volunteer_id:
        raise HTTPException(
            status_code=409,
            detail="No responder assigned.",
        )

    volunteer = get_volunteer(volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=409,
            detail="Assigned responder not found.",
        )

    resolved = resolve_request(request_id)
    if resolved is None:
        raise HTTPException(
            status_code=409,
            detail="Request could not be resolved.",
        )

    released = set_volunteer_availability(
        volunteer_id=volunteer_id,
        available=True,
    )

    if released is None:
        raise HTTPException(
            status_code=500,
            detail="Responder availability could not be restored.",
        )

    return resolved