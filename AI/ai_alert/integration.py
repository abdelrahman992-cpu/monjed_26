"""
MONJED AI - Integration Layer

Bridge between Backend and AI modules.

Architecture:

Backend Assessment Object
            |
            v
AI Adapter
            |
            v
Gemini Alert Generator
            |
            v
Validated AI Alert
            |
            v
Backend Normalization Layer


Responsibilities:
------------------
- Convert backend assessment into AI payload
- Execute AI generation
- Return validated AI result


Does NOT:
-----------
- Calculate risk
- Change decisions
- Send SMS
- Dispatch alerts

Backend remains the source of truth.
"""


import json

from datetime import datetime, timezone


# ============================================================
# IMPORTS
# ============================================================


from backend.app.services.ai_adapter import (
    build_ai_payload,
)


from AI.ai_alert.gemini_alert import (
    generate_alert,
)



# ============================================================
# CONSTANTS
# ============================================================


AI_SOURCE = "MONJED_AI_PIPELINE"



# ============================================================
# HELPERS
# ============================================================


def _safe_print_json(
    title: str,
    data,
):
    """
    Safe debug output.
    """

    print(
        f"\n========== {title} =========="
    )


    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )



def _validate_assessment(
    assessment,
):
    """
    Validate MONJED assessment object.

    AI receives approved backend objects only.
    """


    if assessment is None:

        raise ValueError(
            "Assessment cannot be None."
        )



    if not hasattr(
        assessment,
        "risk",
    ):

        raise TypeError(
            "Invalid MONJED assessment object."
        )



# ============================================================
# MAIN PIPELINE
# ============================================================


def run_ai_pipeline(
    assessment,
    accessibility=None,
    language="en",
):
    """
    Execute complete MONJED AI pipeline.


    Flow:

    Assessment Object
            |
            v
    AI Adapter
            |
            v
    Gemini Generator
            |
            v
    Validated Alert


    Returns:

    {
        metadata,
        payload,
        alert
    }

    """


    # --------------------------------------------------------
    # 0. Validate Input
    # --------------------------------------------------------

    _validate_assessment(
        assessment
    )


    started_at = datetime.now(
        timezone.utc
    )



    # --------------------------------------------------------
    # 1. Build AI Payload
    # --------------------------------------------------------

    ai_payload = build_ai_payload(

        assessment=assessment,

        accessibility=accessibility,

        language=language,

    )



    _safe_print_json(
        "AI PAYLOAD",
        ai_payload,
    )



    # --------------------------------------------------------
    # 2. Generate AI Alert
    # --------------------------------------------------------

    ai_alert = generate_alert(

        ai_payload

    )



    if not isinstance(
        ai_alert,
        dict,
    ):

        raise RuntimeError(
            "Gemini alert generation returned invalid response."
        )



    _safe_print_json(
        "AI ALERT",
        ai_alert,
    )



    finished_at = datetime.now(
        timezone.utc
    )



    # --------------------------------------------------------
    # 3. Execution Metadata
    # --------------------------------------------------------

    metadata = {

        "source":
            AI_SOURCE,


        "status":
            "success",


        "started_at":
            started_at.isoformat(),


        "completed_at":
            finished_at.isoformat(),


        "processing_time_ms":
            int(

                (
                    finished_at - started_at

                ).total_seconds()
                *
                1000

            ),

    }



    # --------------------------------------------------------
    # 4. Final Result
    # --------------------------------------------------------

    return {

        "metadata":

            metadata,


        "payload":

            ai_payload,


        "alert":

            ai_alert,

    }



# ============================================================
# MODULE TEST
# ============================================================


if __name__ == "__main__":

    print(
        """
MONJED AI Integration Layer

This module is imported by backend services.
Run full tests through backend pipeline.
"""
    )