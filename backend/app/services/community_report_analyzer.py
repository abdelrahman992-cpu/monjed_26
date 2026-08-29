"""
MONJED - Community Report Analyzer

Architecture:

Community Report
      ↓
Gemini Structured Extraction
      ↓
Backend Validation
      ↓
Community Evidence
      ↓
Decision Engine

If Gemini is unavailable:

Community Report
      ↓
Conservative Deterministic Fallback
      ↓
Community Evidence
      ↓
Decision Engine


IMPORTANT:
- This layer does NOT verify reports.
- This layer does NOT calculate scientific risk.
- This layer does NOT make operational decisions.
- analysis_confidence means confidence in extraction only.
- Deterministic fallback extracts only explicit signals.
"""

import os

from dotenv import load_dotenv
from google import genai

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
    AnalysisSource,
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


COMMUNITY_REPORT_MODEL = os.getenv(
    "COMMUNITY_REPORT_MODEL",
    GEMINI_MODEL,
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
            "Community report analyzer: "
            "Gemini client initialization failed. "
            "Deterministic fallback will be used."
        )

        print(
            f"Client error: {error}"
        )


# ============================================================
# TEXT HELPERS
# ============================================================

def _normalize_text(
    text: str,
) -> str:
    """
    Normalize text for conservative keyword matching.
    """

    return (
        text
        .lower()
        .strip()
    )


def _contains_any(
    text: str,
    phrases: tuple[str, ...],
) -> bool:
    """
    Return True when at least one explicit phrase
    appears in the text.
    """

    return any(
        phrase in text
        for phrase in phrases
    )


def _has_signal(
    text: str,
    positive_phrases: tuple[str, ...],
    negative_phrases: tuple[str, ...] = (),
) -> bool:
    """
    Conservative signal detection.

    Explicit negative statements take precedence over
    positive keyword matches.

    Example:
    "No people are reported trapped"
    must NOT produce people_trapped=True.
    """

    if _contains_any(
        text,
        negative_phrases,
    ):
        return False

    return _contains_any(
        text,
        positive_phrases,
    )


# ============================================================
# QUOTA / API ERROR DETECTION
# ============================================================

def _is_rate_limit_error(
    error: Exception,
) -> bool:
    """
    Detect Gemini quota/rate-limit errors without depending
    on one SDK-specific exception class.

    This keeps the analyzer resilient across SDK versions.
    """

    message = str(
        error
    ).lower()

    indicators = (
        "429",
        "resource_exhausted",
        "quota exceeded",
        "too_many_requests",
        "rate limit",
        "rate-limit",
    )

    return any(
        indicator in message
        for indicator in indicators
    )


# ============================================================
# DETERMINISTIC FALLBACK SIGNALS
# ============================================================

FLOOD_TERMS = (
    "flood",
    "flooding",
    "floodwater",
    "flood water",
    "inundation",
    "فيضان",
    "فيضانات",
    "مياه الفيضان",
)


EARTHQUAKE_TERMS = (
    "earthquake",
    "quake",
    "aftershock",
    "زلزال",
    "هزة أرضية",
    "هزه ارضيه",
)


RISING_WATER_TERMS = (
    "water is rising",
    "water level is rising",
    "water levels are rising",
    "rising water",
    "rising floodwater",
    "floodwater is rising",
    "water is entering",
    "water is spreading",
    "المياه ترتفع",
    "منسوب المياه يرتفع",
    "المياه بتزيد",
)


RISING_WATER_NEGATIONS = (
    "water is not rising",
    "water levels are not rising",
    "water level is not rising",
    "المياه لا ترتفع",
)


BLOCKED_ROAD_TERMS = (
    "road is blocked",
    "road blocked",
    "blocked road",
    "route is blocked",
    "route blocked",
    "road is flooded",
    "route is flooded",
    "vehicles cannot pass",
    "vehicles can't pass",
    "cannot pass safely",
    "can't pass safely",
    "road cannot be used",
    "route cannot be used",
    "road is impassable",
    "route is impassable",
    "الطريق مغلق",
    "الطريق مسدود",
    "لا يمكن المرور",
)


BLOCKED_ROAD_NEGATIONS = (
    "road is not blocked",
    "route is not blocked",
    "vehicles can pass",
    "road remains open",
    "الطريق غير مغلق",
    "الطريق مفتوح",
)


BUILDING_DAMAGE_TERMS = (
    "building collapsed",
    "building has collapsed",
    "building partially collapsed",
    "part of the building collapsed",
    "part of a residential building collapsed",
    "collapsed building",
    "structural damage",
    "major structural damage",
    "major cracks",
    "large cracks",
    "wall collapsed",
    "wall has collapsed",
    "ceiling collapsed",
    "building is unsafe",
    "building was damaged",
    "building is damaged",
    "انهيار مبنى",
    "انهار المبنى",
    "المبنى انهار",
    "تصدعات كبيرة",
    "أضرار هيكلية",
)


BUILDING_DAMAGE_NEGATIONS = (
    "building is not damaged",
    "no building damage",
    "no structural damage",
    "building remains safe",
    "لا توجد أضرار بالمبنى",
    "المبنى غير متضرر",
)


INFRASTRUCTURE_DAMAGE_TERMS = (
    "bridge collapsed",
    "bridge is damaged",
    "road is damaged",
    "road was damaged",
    "power lines are down",
    "power line is down",
    "electricity infrastructure damaged",
    "water infrastructure damaged",
    "communications infrastructure damaged",
    "utility infrastructure damaged",
    "water main broken",
    "communications are down",
    "bridge damaged",
    "جسر منهار",
    "الجسر متضرر",
    "أضرار بالبنية التحتية",
    "انقطاع بسبب أضرار بالبنية التحتية",
)


INFRASTRUCTURE_DAMAGE_NEGATIONS = (
    "no infrastructure damage",
    "infrastructure is not damaged",
    "لا توجد أضرار بالبنية التحتية",
)


PEOPLE_TRAPPED_TERMS = (
    "people are trapped",
    "people trapped",
    "person is trapped",
    "person trapped",
    "people are stuck inside",
    "person is stuck inside",
    "cannot get out",
    "can't get out",
    "unable to get out",
    "unable to leave",
    "cannot leave",
    "buried under",
    "trapped under",
    "محاصر",
    "محاصرين",
    "محاصرون",
    "عالق",
    "عالقون",
    "لا يستطيع الخروج",
    "لا يستطيعون الخروج",
)


PEOPLE_TRAPPED_NEGATIONS = (
    "no people are trapped",
    "no people are reported trapped",
    "no one is trapped",
    "nobody is trapped",
    "nobody trapped",
    "people are not trapped",
    "person is not trapped",
    "لا يوجد أشخاص محاصرون",
    "لا يوجد محاصرون",
    "لا أحد محاصر",
)


HELP_NEEDED_TERMS = (
    "help is needed",
    "need help",
    "needs help",
    "emergency help is needed",
    "emergency assistance is needed",
    "requesting help",
    "requesting assistance",
    "need assistance",
    "needs assistance",
    "نحتاج مساعدة",
    "يحتاج مساعدة",
    "مساعدة طارئة",
    "نحتاج للمساعدة",
)


TRANSPORTATION_NEEDED_TERMS = (
    "need transportation",
    "needs transportation",
    "transportation is needed",
    "need a vehicle",
    "needs a vehicle",
    "need a ride",
    "needs a ride",
    "evacuation transport is needed",
    "no transportation available",
    "no transport available",
    "نحتاج وسيلة نقل",
    "نحتاج سيارة",
    "لا توجد وسيلة نقل",
)


MOBILITY_ASSISTANCE_TERMS = (
    "uses a wheelchair",
    "using a wheelchair",
    "wheelchair user",
    "cannot walk",
    "can't walk",
    "unable to walk",
    "mobility assistance",
    "physical evacuation assistance",
    "needs help moving",
    "needs assistance moving",
    "كرسي متحرك",
    "لا يستطيع المشي",
    "لا تستطيع المشي",
    "يحتاج مساعدة في الحركة",
)


# ============================================================
# DETERMINISTIC FALLBACK ANALYZER
# ============================================================

def _build_deterministic_fallback(
    report: CommunityReportInput,
) -> CommunityReportAnalysis:
    """
    Conservative deterministic extraction.

    This fallback intentionally recognizes only explicit
    phrases. It prefers missing an ambiguous signal over
    inventing a dangerous one.
    """

    text = _normalize_text(
        report.report_text
    )

    # ========================================================
    # HAZARD
    # ========================================================

    # Rising water is itself an explicit flood signal.
    # We calculate it before hazard classification so the
    # fallback does not return hazard_type="unknown" while
    # simultaneously returning rising_water=True.
    rising_water_signal = _has_signal(
        text,
        RISING_WATER_TERMS,
        RISING_WATER_NEGATIONS,
    )

    flood_detected = (
        _contains_any(
            text,
            FLOOD_TERMS,
        )
        or rising_water_signal
    )

    earthquake_detected = _contains_any(
        text,
        EARTHQUAKE_TERMS,
    )

    # If both hazard types are explicitly present, do not
    # guess which one is primary.
    if (
        flood_detected
        and not earthquake_detected
    ):
        hazard_type = "flood"

    elif (
        earthquake_detected
        and not flood_detected
    ):
        hazard_type = "earthquake"

    else:
        hazard_type = "unknown"

    # ========================================================
    # OPERATIONAL SIGNALS
    # ========================================================

    rising_water = rising_water_signal

    blocked_road = _has_signal(
        text,
        BLOCKED_ROAD_TERMS,
        BLOCKED_ROAD_NEGATIONS,
    )

    building_damage = _has_signal(
        text,
        BUILDING_DAMAGE_TERMS,
        BUILDING_DAMAGE_NEGATIONS,
    )

    infrastructure_damage = _has_signal(
        text,
        INFRASTRUCTURE_DAMAGE_TERMS,
        INFRASTRUCTURE_DAMAGE_NEGATIONS,
    )

    people_trapped = _has_signal(
        text,
        PEOPLE_TRAPPED_TERMS,
        PEOPLE_TRAPPED_NEGATIONS,
    )

    transportation_needed = _contains_any(
        text,
        TRANSPORTATION_NEEDED_TERMS,
    )

    mobility_assistance_needed = (
        _contains_any(
            text,
            MOBILITY_ASSISTANCE_TERMS,
        )
    )

    help_needed = _contains_any(
        text,
        HELP_NEEDED_TERMS,
    )

    # Being explicitly trapped necessarily implies
    # an assistance need, but does NOT verify the report.
    if people_trapped:
        help_needed = True

    # ========================================================
    # EXTRACTED EVIDENCE
    # ========================================================

    extracted_evidence: list[str] = []

    if rising_water:
        extracted_evidence.append(
            "The report explicitly indicates rising water."
        )

    if blocked_road:
        extracted_evidence.append(
            "The report explicitly indicates a blocked or unsafe route."
        )

    if building_damage:
        extracted_evidence.append(
            "The report explicitly indicates building or structural damage."
        )

    if infrastructure_damage:
        extracted_evidence.append(
            "The report explicitly indicates infrastructure damage."
        )

    if people_trapped:
        extracted_evidence.append(
            "The report explicitly indicates that people are trapped."
        )

    if transportation_needed:
        extracted_evidence.append(
            "The report explicitly indicates a transportation need."
        )

    if mobility_assistance_needed:
        extracted_evidence.append(
            "The report explicitly indicates a mobility assistance need."
        )

    if (
        help_needed
        and not people_trapped
    ):
        extracted_evidence.append(
            "The report explicitly requests assistance."
        )

    # ========================================================
    # SEVERITY
    #
    # Conservative hierarchy.
    # ========================================================

    if people_trapped:

        severity = "critical"

    elif (
        building_damage
        or infrastructure_damage
        or rising_water
    ):

        severity = "high"

    elif (
        blocked_road
        or transportation_needed
        or mobility_assistance_needed
        or help_needed
    ):

        severity = "moderate"

    else:

        severity = "low"

    # ========================================================
    # EXTRACTION CONFIDENCE
    #
    # This represents confidence in deterministic text
    # interpretation only — never event verification.
    # ========================================================

    signal_count = sum(
        (
            rising_water,
            blocked_road,
            building_damage,
            infrastructure_damage,
            people_trapped,
            transportation_needed,
            help_needed,
            mobility_assistance_needed,
        )
    )

    if (
        hazard_type != "unknown"
        and signal_count >= 2
    ):

        analysis_confidence = 0.80

    elif (
        hazard_type != "unknown"
        and signal_count == 1
    ):

        analysis_confidence = 0.75

    elif signal_count > 0:

        analysis_confidence = 0.65

    else:

        analysis_confidence = 0.50

    return CommunityReportAnalysis(
        hazard_type=hazard_type,
        severity=severity,

        rising_water=rising_water,
        blocked_road=blocked_road,

        building_damage=building_damage,
        infrastructure_damage=infrastructure_damage,

        people_trapped=people_trapped,

        transportation_needed=transportation_needed,
        help_needed=help_needed,
        mobility_assistance_needed=mobility_assistance_needed,

        analysis_confidence=analysis_confidence,

        extracted_evidence=extracted_evidence,
    )


# ============================================================
# GEMINI PROMPT
# ============================================================

def _build_prompt(
    report: CommunityReportInput,
) -> str:
    """
    Build the Gemini extraction prompt.
    """

    return f"""
You are the community-report analysis component of MONJED,
a disaster decision-support and early-warning system.

Your role is INFORMATION EXTRACTION ONLY.

You do NOT verify whether the submitted report is true.
You do NOT calculate scientific hazard risk.
You do NOT make operational decisions.

Analyze the community report below.

ZONE:
{report.zone_id}

LOCATION:
{report.location}

REPORT:
{report.report_text}


============================================================
GENERAL SAFETY RULES
============================================================

- Extract only information supported by the report.
- Do not invent facts.
- Do not assume facts that are not stated or strongly
  and directly supported by the report.
- A community report is NOT automatically verified.
- Do not treat analysis_confidence as verification.
- analysis_confidence means confidence that you correctly
  understood and extracted the information in the text.
- If something is not mentioned or cannot be inferred safely,
  set its boolean field to false.
- extracted_evidence must contain only short factual statements
  directly supported by the report.
- Do not include recommendations or safety instructions inside
  extracted_evidence.


============================================================
HAZARD CLASSIFICATION
============================================================

Set hazard_type to:

"flood"
ONLY when the report clearly describes flooding, floodwater,
rising water, inundation, or another clearly flood-related event.

"earthquake"
ONLY when the report clearly describes an earthquake,
earthquake shaking, earthquake-related structural damage,
or earthquake-related impact.

"unknown"
when the hazard cannot be determined safely from the text.

Do not classify structural damage as earthquake-related unless
the report clearly connects it to an earthquake or earthquake
context.


============================================================
FLOOD / ROUTE SIGNALS
============================================================

rising_water = true ONLY when the report indicates that:
- water is rising,
- floodwater levels are increasing,
- water is entering or spreading into an area,
- or equivalent directly supported evidence exists.

Do NOT set rising_water=true merely because floodwater exists
if the report does not indicate that the water level is rising.


blocked_road = true ONLY when the report indicates that:
- a road is blocked,
- a route cannot be used safely,
- vehicles cannot pass,
- floodwater prevents passage,
- debris prevents passage,
- or equivalent route obstruction is directly supported.


============================================================
EARTHQUAKE / DAMAGE SIGNALS
============================================================

building_damage = true ONLY when the report directly indicates
damage to a building or structure, such as:
- partial or complete collapse,
- major cracks,
- walls or ceilings falling,
- structural damage,
- a building becoming unsafe.

Do not infer building damage merely because an earthquake
occurred.


infrastructure_damage = true ONLY when the report directly
indicates damage to infrastructure such as:
- roads,
- bridges,
- utilities,
- electricity infrastructure,
- water infrastructure,
- communications infrastructure,
- or other public infrastructure.

Do not set infrastructure_damage=true merely because a route
is temporarily blocked unless actual infrastructure damage
is stated.


============================================================
HUMAN SAFETY SIGNALS
============================================================

people_trapped = true ONLY when the report directly indicates
that one or more people are:
- trapped,
- stuck inside a dangerous location,
- unable to leave because of collapse or obstruction,
- buried,
- isolated in a way that prevents safe exit.

Do NOT infer people_trapped merely because help is requested.


help_needed = true when the report explicitly indicates that:
- assistance is needed,
- emergency help is requested,
- people cannot safely manage the situation without help,
- or equivalent assistance need is clearly supported.


mobility_assistance_needed = true when the report clearly
indicates that a person may be physically unable to carry out
a required evacuation or safety action without assistance.

Examples include explicit mention of:
- wheelchair use,
- inability to walk,
- serious movement limitation,
- needing physical evacuation assistance.

Do NOT infer disability or mobility limitation without
supporting information in the report.


transportation_needed = true ONLY when the report explicitly
indicates:
- transportation is needed,
- a vehicle is needed,
- a ride is needed,
- evacuation transport is needed,
- or transportation is unavailable.

Do NOT set transportation_needed=true simply because:
- someone needs help,
- someone has limited mobility,
- a road is blocked.


============================================================
SEVERITY
============================================================

Choose severity using ONLY the situation described in the report.

Use "critical" when the report clearly describes an immediate
life-safety emergency, such as people trapped or another
directly stated severe threat to life.

Use "high" when the report clearly describes serious conditions
such as major structural damage, significant infrastructure
damage, dangerous rising water, or an unusable critical route.

Use "moderate" when the report describes a meaningful local
hazard or disruption that does not clearly indicate an
immediate life-threatening emergency.

Use "low" when the report describes limited impact or minor
conditions.

Do NOT increase severity using external knowledge or assumptions.


============================================================
ANALYSIS CONFIDENCE
============================================================

analysis_confidence represents ONLY how confident you are that
the report text was correctly interpreted.

It does NOT represent:
- probability that the event happened,
- verification of the reporter,
- scientific hazard confidence,
- risk probability.

============================================================
LANGUAGE AND SEMANTIC INTERPRETATION
============================================================

- The report may be written in any supported language or local dialect,
  including colloquial Arabic, Egyptian Arabic, Swahili, French,
  or informal English.

- Interpret the SEMANTIC MEANING of the report, not only exact keywords
  or formal wording.

- Colloquial wording counts as explicit evidence when its meaning is
  unambiguous.

- Internally understand or translate the user's wording before mapping it
  to the structured fields.

- Do NOT require the user to use formal phrases such as
  "transportation is needed".

Examples of equivalent explicit transportation requests:

"I need a car."
"I need a ride."
"محتاجة عربية"
"محتاج عربية"
"عايزين عربية تنقلنا"
"محتاجين مواصلات"

All of the examples above clearly indicate:

transportation_needed = true
help_needed = true

They do NOT by themselves establish:

hazard_type = flood
hazard_type = earthquake
people_trapped = true
mobility_assistance_needed = true

Do not infer a hazard merely from an assistance request.

============================================================
OUTPUT
============================================================

Return structured JSON matching the required schema.

Every boolean must reflect only what the report supports.

Never invent:
- trapped people,
- structural damage,
- rising water,
- blocked routes,
- disabilities,
- transportation needs,
- infrastructure damage,
- or emergency conditions.
"""


# ============================================================
# BACKEND CONSISTENCY GUARDS
# ============================================================

def _apply_consistency_guards(
    analysis: CommunityReportAnalysis,
) -> CommunityReportAnalysis:
    """
    Apply deterministic backend safety rules after either
    Gemini or fallback analysis.
    """

    # Explicitly trapped people necessarily require help.
    if analysis.people_trapped:
        analysis.help_needed = True

    # Ensure confidence stays inside the contract even if
    # external output is unexpectedly malformed.
    analysis.analysis_confidence = max(
        0.0,
        min(
            float(
                analysis.analysis_confidence
            ),
            1.0,
        ),
    )

    return analysis


# ============================================================
# COMMUNITY REPORT ANALYSIS
# ============================================================

def analyze_community_report(
    report: CommunityReportInput,
) -> tuple[
    CommunityReportAnalysis,
    AnalysisSource,
]:
    """
    Analyze a free-text community report.

    Returns:
        A tuple containing:
        - the structured CommunityReportAnalysis
        - the backend-controlled AnalysisSource

    Preferred path:
        Gemini structured extraction -> AnalysisSource.GEMINI

    Safe fallback path:
        Conservative deterministic extraction
        -> AnalysisSource.DETERMINISTIC_FALLBACK

    IMPORTANT:
    The analysis source describes how the report was
    interpreted. It does NOT verify whether the report
    itself is true.
    """

    # ========================================================
    # NO GEMINI CLIENT
    # ========================================================

    if client is None:

        print(
            "Community report analyzer: "
            "Gemini unavailable. "
            "Using deterministic fallback."
        )

        analysis = _build_deterministic_fallback(
            report
        )

        analysis = _apply_consistency_guards(
            analysis
        )

        return (
            analysis,
            AnalysisSource.DETERMINISTIC_FALLBACK,
        )

    # ========================================================
    # GEMINI ANALYSIS
    # ========================================================

    prompt = _build_prompt(
        report
    )

    try:

        interaction = client.interactions.create(
            model=COMMUNITY_REPORT_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema":
                    CommunityReportAnalysis.model_json_schema(),
            },
        )

        analysis = (
            CommunityReportAnalysis.model_validate_json(
                interaction.output_text
            )
        )

        analysis = _apply_consistency_guards(
            analysis
        )

        return (
            analysis,
            AnalysisSource.GEMINI,
        )

    # ========================================================
    # SAFE FALLBACK ON GEMINI FAILURE
    # ========================================================

    except Exception as error:

        if _is_rate_limit_error(
            error
        ):

            print(
                "Community report analyzer: "
                "Gemini quota/rate limit reached. "
                "Using deterministic fallback immediately."
            )

        else:

            print(
                "Community report analyzer: "
                "Gemini analysis failed. "
                "Using deterministic fallback."
            )

            print(
                f"Analyzer error: {error}"
            )

        analysis = _build_deterministic_fallback(
            report
        )

        analysis = _apply_consistency_guards(
            analysis
        )

        return (
            analysis,
            AnalysisSource.DETERMINISTIC_FALLBACK,
        )