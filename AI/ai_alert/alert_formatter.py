"""
MONJED AI - Alert Formatter

Converts validated MONJED alerts into
communication formats:

- Dashboard
- SMS
- Voice-ready format

IMPORTANT:
- This module does NOT make decisions.
- It only formats validated alerts.
"""


import json



# ============================================================
# LANGUAGE LABELS
# ============================================================


LANGUAGE_LABELS = {


    "en": {

        "title":
            "MONJED ALERT",

        "action":
            "Action",

        "backup":
            "Backup",

        "risk":
            "Risk",

        "score":
            "Score",

    },


    "ar": {

        "title":
            "تنبيه MONJED",

        "action":
            "الإجراء",

        "backup":
            "الإجراء البديل",

        "risk":
            "الخطورة",

        "score":
            "الدرجة",

    },


    "fr": {

        "title":
            "ALERTE MONJED",

        "action":
            "Action",

        "backup":
            "Alternative",

        "risk":
            "Risque",

        "score":
            "Score",

    },


    "sw": {

        "title":
            "TAHADHARI MONJED",

        "action":
            "Hatua",

        "backup":
            "Hatua mbadala",

        "risk":
            "Hatari",

        "score":
            "Alama",

    },

}



# ============================================================
# HELPERS
# ============================================================


def _get_language(
    alert: dict,
) -> str:

    language = alert.get(
        "language",
        "en",
    )


    if language not in LANGUAGE_LABELS:

        return "en"


    return language



def _safe_value(
    value,
    default="",
):

    if value is None:

        return default

    return value



def _get_hazards(
    alert: dict,
):

    hazards = alert.get(
        "hazards",
        [],
    )


    if not isinstance(
        hazards,
        list,
    ):

        return []


    return hazards



# ============================================================
# DASHBOARD FORMAT
# ============================================================


def format_dashboard_alert(
    alert: dict,
) -> dict:

    """
    Convert validated MONJED AI alert into
    dashboard-friendly format.

    Dashboard receives only validated data.
    """



    hazards = []


    for hazard in _get_hazards(alert):


        if not isinstance(
            hazard,
            dict,
        ):

            continue



        hazards.append(

            {

                "type":
                    hazard.get(
                        "type",
                        "unknown",
                    ),


                "risk_score":
                    hazard.get(
                        "risk_score",
                        0,
                    ),


                "risk_level":
                    hazard.get(
                        "risk_level",
                        "unknown",
                    ),


                "confidence":
                    hazard.get(
                        "confidence",
                    ),


                "message":
                    hazard.get(
                        "message",
                        "",
                    ),

            }

        )



    final_decision = alert.get(
        "final_decision",
        {},
    )


    if not isinstance(
        final_decision,
        dict,
    ):

        final_decision = {}



    return {


        "title":
            _safe_value(
                alert.get("title"),
                "MONJED Alert",
            ),



        "zone_id":
            _safe_value(
                alert.get("zone_id"),
                "UNKNOWN",
            ),



        "country":
            _safe_value(
                alert.get("country"),
                "UNKNOWN",
            ),



        "language":
            _get_language(
                alert
            ),



        "generated_at":
            alert.get(
                "generated_at"
            ),



        "hazards":
            hazards,



        "community_evidence_summary":
            _safe_value(
                alert.get(
                    "community_evidence_summary"
                )
            ),



        "decision_status":
            final_decision.get(
                "decision_status"
            ),



        "current_action":
            final_decision.get(
                "current_action"
            ),



        "backup_action":
            final_decision.get(
                "backup_action"
            ),



        "accessibility_instructions":
            final_decision.get(
                "accessibility_instructions",
                [],
            ),



        "accessibility_needs":
            alert.get(
                "accessibility_needs",
                [],
            ),



        "alert_message":
            _safe_value(
                alert.get(
                    "alert_message"
                )
            ),



        "alert_source":
            alert.get(
                "alert_source",
                "UNKNOWN",
            ),

    }



# ============================================================
# SMS FORMAT
# ============================================================


def format_sms_alert(
    alert: dict,
) -> str:

    """
    Convert MONJED alert into
    human-readable emergency SMS.

    Optimized for:
    - Low bandwidth
    - Fast reading
    - Multiple languages
    """

    language = _get_language(alert)

    labels = {

        "en": {
            "do": "DO NOW",
            "avoid": "AVOID",
            "help": "Need help? Contact emergency support.",
        },

        "ar": {
            "do": "افعل الآن",
            "avoid": "تجنب",
            "help": "تحتاج مساعدة؟ تواصل مع الطوارئ.",
        },

        "fr": {
            "do": "À FAIRE",
            "avoid": "ÉVITER",
            "help": "Besoin d'aide ? Contactez les secours.",
        },

        "sw": {
            "do": "FANYA SASA",
            "avoid": "EPUKA",
            "help": "Unahitaji msaada? Wasiliana na huduma za dharura.",
        },

    }[language]


    title = LANGUAGE_LABELS[language]["title"]


    message = (
        f"{title} ⚠️\n\n"
    )


    # -------------------------
    # Hazard
    # -------------------------

    for hazard in _get_hazards(alert):

        hazard_type = hazard.get(
            "type",
            "unknown",
        )

        level = hazard.get(
            "risk_level",
            "unknown",
        )


        message += (
            f"{hazard_type.upper()} "
            f"RISK: {level.upper()}\n\n"
        )


        hazard_message = hazard.get(
            "message"
        )


        if hazard_message:

            message += (
                f"{hazard_message}\n\n"
            )


    # -------------------------
    # Actions
    # -------------------------

    decision = alert.get(
        "final_decision",
        {},
    )


    if not isinstance(
        decision,
        dict,
    ):

        decision = {}


    action = decision.get(
        "current_action"
    )


    if action:

        message += (
            f"{labels['do']}:\n"
            f"{action}\n\n"
        )


    backup = decision.get(
        "backup_action"
    )


    if backup:

        message += (
            f"{labels['avoid']}:\n"
            f"{backup}\n\n"
        )


    message += labels["help"]


    return message.strip()

    """
    Convert validated MONJED alert into
    concise SMS format.

    Designed for:
    - Low bandwidth
    - Multiple languages
    - Emergency communication
    """



    language = _get_language(
        alert
    )


    labels = LANGUAGE_LABELS[
        language
    ]



    country = alert.get(
        "country",
        "UNKNOWN",
    )



    message = (

        f"{labels['title']} - {country}\n"

    )



    # --------------------------------------------------------
    # Hazards
    # --------------------------------------------------------


    for hazard in _get_hazards(alert):


        hazard_type = hazard.get(
            "type",
            "unknown",
        )


        level = hazard.get(
            "risk_level",
            "unknown",
        )


        score = hazard.get(
            "risk_score",
            0,
        )


        message += (

            f"{hazard_type}: "
            f"{level} "
            f"({labels['score']}: {score})\n"

        )



        hazard_message = hazard.get(
            "message"
        )


        if hazard_message:

            message += (

                f"{hazard_message}\n"

            )



    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------


    decision = alert.get(
        "final_decision",
        {},
    )


    if not isinstance(
        decision,
        dict,
    ):

        decision = {}



    action = decision.get(
        "current_action"
    )


    if action:

        message += (

            f"{labels['action']}: "
            f"{action}\n"

        )



    backup = decision.get(
        "backup_action"
    )


    if backup:

        message += (

            f"{labels['backup']}: "
            f"{backup}"

        )



    return message.strip()



# ============================================================
# VOICE READY FORMAT
# ============================================================


def format_voice_alert(
    alert: dict,
) -> dict:

    """
    Prepare alert for future Text-To-Speech integration.
    """

    decision = alert.get(
        "final_decision",
        {},
    )


    return {


        "language":
            _get_language(
                alert
            ),


        "priority":
            alert.get(
                "risk_level",
                "unknown",
            ),


        "message":
            alert.get(
                "alert_message",
                "",
            ),


        "action":
            decision.get(
                "current_action",
                "",
            ),


        "accessibility_needs":
            alert.get(
                "accessibility_needs",
                [],
            ),

    }



# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":


    sample_alert = {


        "title":
            "MONJED Alert - Zone test_01",


        "zone_id":
            "test_01",


        "country":
            "Egypt",


        "language":
            "en",


        "generated_at":
            "2026-08-24T00:00:00Z",


        "hazards":

            [

                {

                    "type":
                        "earthquake",

                    "risk_score":
                        73,

                    "risk_level":
                        "high",

                    "confidence":
                        0.9,

                    "message":
                        "Strong earthquake magnitude",

                }

            ],


        "final_decision":

            {

                "decision_status":
                    "human_review_required",


                "current_action":
                    "Request emergency assistance.",


                "backup_action":
                    "Do not attempt unsafe rescue actions.",


                "accessibility_instructions":
                    [

                        "Request trained assistance."

                    ]

            },


        "accessibility_needs":
            [

                "mobility"

            ],


        "alert_message":
            "High risk earthquake alert."

    }



    print(
        json.dumps(
            format_dashboard_alert(
                sample_alert
            ),
            indent=2,
            ensure_ascii=False,
        )
    )



    print(
        format_sms_alert(
            sample_alert
        )
    )