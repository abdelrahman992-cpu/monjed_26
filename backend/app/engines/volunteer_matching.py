from math import (
    radians,
    sin,
    cos,
    sqrt,
    atan2,
)

from app.schemas.assistance import (
    AssistanceRequestRecord,
)

from app.schemas.volunteer import (
    VolunteerRecord,
)



# ============================================================
# REQUIRED SKILLS
# ============================================================

SKILL_MAPPING = {

    "evacuation": (
        "evacuation",
        "transportation",
    ),

    "transportation": (
        "transportation",
    ),

    "mobility_assistance": (
        "mobility_assistance",
    ),

    "medical_support": (
        "medical_support",
    ),

    "rescue_support": (
        "rescue_support",
    ),

    "other": (
        "general_support",
    ),
}



# ============================================================
# DISTANCE
# ============================================================

def calculate_distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):

    if None in (
        lat1,
        lon1,
        lat2,
        lon2,
    ):
        return None


    radius = 6371


    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)


    dlat = lat2 - lat1
    dlon = lon2 - lon1


    a = (
        sin(dlat / 2)**2
        +
        cos(lat1)
        *
        cos(lat2)
        *
        sin(dlon / 2)**2
    )


    return radius * (
        2 * atan2(
            sqrt(a),
            sqrt(1-a)
        )
    )



# ============================================================
# SAFETY
# ============================================================

def requires_trained_responder(
    request,
):

    return (
        request.requires_trained_responder
        or
        request.request_type
        ==
        "rescue_support"
    )



def has_transport(
    volunteer,
):

    return bool(
        volunteer.vehicle_type
    )



def can_use_skill(
    volunteer,
    request,
    skill,
):


    if skill not in volunteer.skills:

        return False



    if (
        request.request_type
        ==
        "transportation"
        and
        skill
        ==
        "transportation"
    ):

        return has_transport(
            volunteer
        )



    return True



# ============================================================
# QUALIFICATION
# ============================================================

def is_qualified(
    volunteer,
    request,
):


    if not volunteer.available:

        return False



    if (
        volunteer.zone_id.strip()
        !=
        request.zone_id.strip()
    ):

        return False



    if requires_trained_responder(request):

        if (
            volunteer.responder_level
            !=
            "trained_responder"
        ):

            return False



    required_skills = SKILL_MAPPING.get(
        request.request_type,
        (),
    )


    return any(

        can_use_skill(
            volunteer,
            request,
            skill,
        )

        for skill in required_skills

    )



# ============================================================
# MATCH ENGINE
# ============================================================

def match_volunteer(
    request: AssistanceRequestRecord,
    volunteers: list[VolunteerRecord],
):


    qualified = [

        volunteer

        for volunteer in volunteers

        if is_qualified(
            volunteer,
            request,
        )

    ]


    if not qualified:

        return None



    def ranking(
        volunteer
    ):


        distance = calculate_distance_km(

            request.latitude,

            request.longitude,

            volunteer.latitude,

            volunteer.longitude,

        )


        # Missing GPS goes last

        if distance is None:

            distance = 999999



        # Trained responder priority

        responder_priority = (

            0

            if volunteer.responder_level
            ==
            "trained_responder"

            else

            1

        )


        return (

            responder_priority,

            distance,

        )



    qualified.sort(
        key=ranking
    )


    return qualified[0]