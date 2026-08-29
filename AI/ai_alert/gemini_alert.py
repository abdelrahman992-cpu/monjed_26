"""
Monjed AI - Gemini Alert Layer

Production Architecture:

Risk Engine
      ↓
Decision Engine
      ↓
Accessibility Layer
      ↓
AI Adapter
      ↓
Gemini Alert Layer
      ↓
Validation
      ↓
Dashboard / SMS


IMPORTANT:
- Gemini is a communication layer only.
- Gemini does NOT calculate risk.
- Gemini does NOT make decisions.
- Gemini does NOT receive raw environmental data.
- The backend payload is the source of truth.
- Gemini cannot modify safety-critical backend values.
- If Gemini is unavailable or returns invalid output,
  a deterministic fallback alert is returned.
"""


import json
import os
import time


from datetime import datetime, timezone


from dotenv import load_dotenv


from google import genai
from google.genai import types



# ============================================================
# CONSTANTS
# ============================================================


SUPPORTED_LANGUAGES = [
    "en",
    "ar",
    "fr",
    "sw",
]


VALID_DECISION_STATUSES = [
    "no_adjustment",
    "action_adjusted",
    "human_review_required",
]


VALID_HAZARDS = {
    "flood",
    "earthquake",
}


VALID_ACCESSIBILITY_NEEDS = {
    "mobility",
    "visual",
    "hearing",
    "cognitive",
}


VALID_AI_SOURCE = (
    "MONJED_BACKEND"
)


VALID_AI_ROLE = (
    "communication_only"
)



FALLBACK_TITLES = {

    "en":
        "MONJED Alert",

    "ar":
        "تنبيه MONJED",

    "fr":
        "Alerte MONJED",

    "sw":
        "Tahadhari ya MONJED",
}



DEFAULT_ACTION = (
    "Follow official safety guidance."
)


DEFAULT_BACKUP_ACTION = (
    "Follow local authority instructions if conditions change."
)



# ============================================================
# ENVIRONMENT
# ============================================================


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)



# ============================================================
# GEMINI CLIENT
# ============================================================


client = None


if GEMINI_API_KEY:

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )


    except Exception as error:

        print(
            "Gemini client initialization failed. "
            "Deterministic fallback mode will be used."
        )


        print(
            f"Client error: {error}"
        )



# ============================================================
# BASIC HELPERS
# ============================================================


def _utc_timestamp() -> str:
    """
    Return the current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



def _normalize_language(
    language,
) -> str:
    """
    Normalize language safely.
    """

    value = (
        str(language)
        .lower()
        .strip()
    )


    if value not in SUPPORTED_LANGUAGES:

        return "en"


    return value



def _validate_ai_metadata(
    payload: dict,
):
    """
    Validate that the payload comes from MONJED backend.

    Gemini must never receive arbitrary data pretending
    to be an approved backend decision.
    """

    source = payload.get(
        "source"
    )


    role = payload.get(
        "ai_role"
    )


    if source != VALID_AI_SOURCE:

        raise ValueError(
            "Invalid AI payload source."
        )


    if role != VALID_AI_ROLE:

        raise ValueError(
            "Invalid AI role."
        )



def _validate_confidence(
    confidence,
):
    """
    Validate AI confidence field.

    Confidence is informational only and never
    replaces backend risk confidence.
    """

    if confidence is None:

        return True


    if not isinstance(
        confidence,
        (int, float),
    ):

        return False


    return (
        0 <= confidence <= 1
    )

    # ============================================================
# GEMINI ERROR HANDLING
# ============================================================


def _is_non_retryable_gemini_error(
    error: Exception,
) -> bool:
    """
    Detect Gemini errors where retrying the same request
    immediately is unlikely to help.

    MONJED prefers deterministic fallback over adding
    unnecessary latency in safety-related communication.
    """

    message = str(
        error
    ).lower()


    non_retryable_indicators = (

        # Quota / rate limit
        "429",
        "resource_exhausted",
        "quota exceeded",
        "too_many_requests",
        "rate limit",
        "rate-limit",


        # Authentication
        "401",
        "unauthenticated",
        "invalid api key",
        "api key not valid",


        # Permission
        "403",
        "permission_denied",
        "permission denied",


        # Invalid request/model
        "400",
        "invalid_argument",
        "invalid argument",

        "404",
        "not_found",
        "model not found",
    )


    return any(
        indicator in message
        for indicator in non_retryable_indicators
    )



# ============================================================
# PAYLOAD HELPERS
# ============================================================


def _get_hazards(
    payload: dict,
) -> list:
    """
    Return normalized hazards from AI Adapter payload.
    """

    hazards = payload.get(
        "hazards",
        []
    )


    if not isinstance(
        hazards,
        list,
    ):

        return []


    return hazards



def _get_decision(
    payload: dict,
) -> dict:
    """
    Return deterministic backend decision.
    """

    decision = payload.get(
        "decision",
        {}
    )


    if not isinstance(
        decision,
        dict,
    ):

        return {}


    return decision



def _get_accessibility_needs(
    payload: dict,
) -> list:
    """
    Safely return accessibility needs.
    """

    needs = payload.get(
        "accessibility_needs",
        []
    )


    if not isinstance(
        needs,
        list,
    ):

        return []


    return needs



def _build_community_summary(
    payload: dict,
) -> str:
    """
    Build deterministic community evidence summary.

    IMPORTANT:
    - Does not verify reports.
    - Only describes evidence considered by backend.
    """

    evidence = payload.get(
        "community_evidence",
        {}
    )


    if not isinstance(
        evidence,
        dict,
    ):

        return (
            "No recent community evidence items "
            "were used in the operational decision."
        )



    evidence_items = evidence.get(
        "matching_reports",
        0,
    )


    if not isinstance(
        evidence_items,
        int,
    ):

        evidence_items = 0



    evidence_items = max(
        0,
        evidence_items,
    )



    if evidence_items == 1:

        return (
            "1 recent community evidence item "
            "was considered in the operational decision."
        )



    if evidence_items > 1:

        return (
            f"{evidence_items} recent community evidence items "
            "were considered in the operational decision."
        )



    return (
        "No recent community evidence items "
        "were used in the operational decision."
    )



# ============================================================
# DETERMINISTIC FALLBACK ALERT
# ============================================================


def build_fallback_alert(
    payload: dict,
) -> dict:
    """
    Build deterministic alert when Gemini fails.

    Backend remains the only source of truth.
    """


    _validate_ai_metadata(
        payload
    )


    zone_id = payload.get(
        "zone_id",
        "UNKNOWN",
    )


    country = payload.get(
        "country",
        "UNKNOWN",
    )


    language = _normalize_language(
        payload.get(
            "language",
            "en",
        )
    )



    hazards = _get_hazards(
        payload
    )


    decision = _get_decision(
        payload
    )



    accessibility_needs = (
        _get_accessibility_needs(
            payload
        )
    )



    decision_status = decision.get(
        "decision_status",
        "no_adjustment",
    )


    if decision_status not in VALID_DECISION_STATUSES:

        decision_status = (
            "no_adjustment"
        )



    current_action = decision.get(
        "current_action",
        DEFAULT_ACTION,
    )


    backup_action = decision.get(
        "backup_action",
        DEFAULT_BACKUP_ACTION,
    )



    accessibility_instructions = decision.get(
        "accessibility_instructions",
        [],
    )


    if not isinstance(
        accessibility_instructions,
        list,
    ):

        accessibility_instructions = []



    formatted_hazards = []



    for hazard in hazards:


        if not isinstance(
            hazard,
            dict,
        ):

            continue



        hazard_type = hazard.get(
            "hazard",
            "unknown",
        )


        risk_score = hazard.get(
            "risk_score",
            0,
        )


        risk_level = hazard.get(
            "risk_level",
            "low",
        )



        reasons = hazard.get(
            "reasons",
            [],
        )



        if isinstance(
            reasons,
            list,
        ) and reasons:

            message = str(
                reasons[0]
            )

        else:

            message = (
                f"{hazard_type} risk "
                "is currently monitored."
            )



        formatted_hazards.append(

            {

                "type":
                    hazard_type,


                "risk_score":
                    risk_score,


                "risk_level":
                    risk_level,


                "confidence":
                    hazard.get(
                        "confidence"
                    ),


                "message":
                    message,

            }

        )



    alert_message = (

        f"Zone {zone_id} in {country}. "

        f"Current action: {current_action}. "

        f"Backup action: {backup_action}"

    )



    return {


        "title":
            f"{FALLBACK_TITLES[language]} - Zone {zone_id}",


        "zone_id":
            zone_id,


        "country":
            country,


        "language":
            language,


        "hazards":
            formatted_hazards,


        "community_evidence_summary":
            _build_community_summary(
                payload
            ),



        "final_decision":

            {

                "decision_status":
                    decision_status,


                "current_action":
                    current_action,


                "backup_action":
                    backup_action,


                "accessibility_instructions":
                    accessibility_instructions,

            },



        "accessibility_needs":
            accessibility_needs,



        "alert_message":
            alert_message,



        "alert_source":
            "DETERMINISTIC_FALLBACK",


        "generated_by":
            "DETERMINISTIC_FALLBACK",


        "generated_at":
            _utc_timestamp(),


        "confidence_source":
            "backend",

    }

    # ============================================================
# VALIDATE AI ALERT
# ============================================================


def validate_ai_alert(
    backend_payload: dict,
    ai_alert: dict,
) -> dict:
    """
    Validate Gemini output against backend truth.

    Gemini output is accepted only if it preserves
    backend-controlled values.
    """


    errors = []



    # --------------------------------------------------------
    # Metadata validation
    # --------------------------------------------------------

    try:

        _validate_ai_metadata(
            backend_payload
        )

    except Exception as error:

        errors.append(
            str(error)
        )



    if not isinstance(
        ai_alert,
        dict,
    ):

        return {

            "valid": False,

            "errors": [
                "AI response is not a dictionary."
            ],

        }



    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [

        "title",
        "country",
        "timestamp",
        "summary",
        "hazards",
        "recommended_action",
        "confidence",

    ]


    for field in required_fields:

        if field not in ai_alert:

            errors.append(
                f"Missing field: {field}"
            )



    # --------------------------------------------------------
    # Country protection
    # --------------------------------------------------------

    if ai_alert.get(
        "country"
    ) != backend_payload.get(
        "country"
    ):

        errors.append(
            "Country was modified by AI."
        )



    # --------------------------------------------------------
    # Language validation
    # --------------------------------------------------------

    language = ai_alert.get(
        "language",
        backend_payload.get(
            "language",
            "en"
        ),
    )


    if language not in SUPPORTED_LANGUAGES:

        errors.append(
            "Unsupported language."
        )



    # --------------------------------------------------------
    # Score protection
    # --------------------------------------------------------

    backend_score = None


    hazards = _get_hazards(
        backend_payload
    )


    if hazards:

        backend_score = hazards[0].get(
            "risk_score"
        )


    ai_score = ai_alert.get(
        "score"
    )


    # if backend_score is not None:

    #     if ai_score != backend_score:

    #         errors.append(
    #             "Risk score modified by AI."
    #         )

    # --------------------------------------------------------
    # Hazard validation
    # --------------------------------------------------------

    ai_hazards = ai_alert.get(
        "hazards",
        []
    )


    if not isinstance(
        ai_hazards,
        list,
    ):

        errors.append(
            "Hazards must be a list."
        )


    else:

        for hazard in ai_hazards:

            if not isinstance(
                hazard,
                dict,
            ):

                errors.append(
                    "Invalid hazard format."
                )

                continue



            hazard_type = hazard.get(
                "type"
            )


            if hazard_type not in VALID_HAZARDS:

                errors.append(
                    f"Invalid hazard type: {hazard_type}"
                )



    # --------------------------------------------------------
    # Confidence validation
    # --------------------------------------------------------

    confidence = ai_alert.get(
        "confidence"
    )


    if not _validate_confidence(
        confidence
    ):

        errors.append(
            "Invalid confidence value."
        )



    # --------------------------------------------------------
    # Decision protection
    # --------------------------------------------------------

    backend_decision = _get_decision(
        backend_payload
    )


    recommended_action = ai_alert.get(
        "recommended_action"
    )


    if recommended_action is None:

        errors.append(
            "Missing recommended action."
        )



    # AI can explain action but cannot replace it
    if (
        backend_decision.get(
            "current_action"
        )
        and
        recommended_action
        not in
        backend_decision.get(
            "current_action"
        )
    ):

     if not backend_decision.lower() in ai_action.lower():
        errors.append(
            "Recommended action does not preserve backend action."
        )



    return {

        "valid":
            len(errors) == 0,


        "errors":
            errors,

    }




# Compatibility alias
# Some backend modules may import validate_alert

validate_alert = validate_ai_alert




# ============================================================
# GEMINI JSON SCHEMA
# ============================================================


GEMINI_RESPONSE_SCHEMA = {

    "type": "object",

    "required": [
        "title",
        "country",
        "summary",
        "hazards",
        "recommended_action",
    ],

    "properties": {

        "title": {
            "type": "string"
        },

        "country": {
            "type": "string"
        },

        "summary": {
            "type": "string"
        },

        "recommended_action": {
            "type": "string"
        },


        "hazards": {

            "type": "array",

            "items": {

                "type": "object",

                "required": [
                    "type",
                    "level",
                    "score",
                    "reasons",
                ],

                "properties": {

                    "type": {
                        "type": "string"
                    },


                    "level": {

                        "type": "string",

                        "enum": [
                            "low",
                            "moderate",
                            "high",
                            "critical"
                        ]

                    },


                    "score": {

                        "type": "number",

                        "minimum": 0,

                        "maximum": 100

                    },


                    "reasons": {

                        "type": "array",

                        "items": {
                            "type": "string"
                        }

                    }

                }

            }

        },


        "confidence": {

            "type": "number",

            "minimum": 0,

            "maximum": 1

        }

    }

}


# ============================================================
# PROMPT BUILDER
# ============================================================


def _build_prompt(
    payload: dict,
) -> str:

    return f"""

You are MONJED AI emergency communication layer.

Your role is ONLY to transform approved backend
assessment into a human-readable alert.

The backend payload is the absolute source of truth.

STRICT RULES:

1. Copy risk_score exactly.
2. Copy risk_level exactly.
3. Never calculate risk.
4. Never create new hazards.
5. Never change recommended actions.
6. Never remove accessibility instructions.
7. Never add assumptions.
8. Output ONLY valid JSON matching the schema.

For these fields:
- score = backend risk_score
- risk_level = backend risk_level
- recommended_action = backend current_action

Backend payload:

{json.dumps(
    payload,
    indent=2
)}

"""




# ============================================================
# GEMINI GENERATION
# ============================================================


def _call_gemini(
    payload: dict,
):

    if client is None:

        return None



    prompt = _build_prompt(
        payload
    )



    attempts = 3



    for attempt in range(
        attempts
    ):

        try:

            response = client.models.generate_content(

                model=GEMINI_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(

                    temperature=0.2,

                    response_mime_type=
                    "application/json",

                    response_schema=
                    GEMINI_RESPONSE_SCHEMA,

                ),

            )



            if not response.text:

                return None



            return json.loads(
                response.text
            )



        except Exception as error:


            print(
                f"Gemini attempt {attempt+1} failed: {error}"
            )


            if _is_non_retryable_gemini_error(
                error
            ):

                return None



            if attempt < attempts - 1:

                time.sleep(
                    2 ** attempt
                )



    return None




# ============================================================
# PUBLIC GENERATOR
# ============================================================


def generate_alert(
    payload: dict,
) -> dict:
    """
    Main MONJED AI alert generator.

    Pipeline:

    Backend payload
          |
          v
       Gemini
          |
          v
     Validation
          |
          v
 Valid response OR fallback
    """



    _validate_ai_metadata(
        payload
    )



    ai_alert = _call_gemini(
        payload
    )



    if ai_alert:


        validation = validate_ai_alert(

            payload,

            ai_alert,

        )

        if not validation["valid"]:

            print(
                "Gemini validation failed:"
            )

            print(
                validation["errors"]
            )

        if validation["valid"]:


            ai_alert["alert_source"] = (
                "GEMINI"
            )


            ai_alert["generated_at"] = (
                _utc_timestamp()
            )


            return ai_alert



    fallback = build_fallback_alert(
        payload
    )


    fallback["validation"] = {

        "valid": False,

        "reason":
            "Gemini unavailable or failed validation."

    }


    return fallback