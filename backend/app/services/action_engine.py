from app.schemas.risk import RiskLevel


FLOOD_ACTIONS = {
    "low": {
        "current": (
            "Monitor local conditions and official updates."
        ),
        "backup": (
            "Keep emergency contacts and essential supplies available."
        ),
    },

    "moderate": {
        "current": (
            "Avoid low-lying areas and monitor local flood updates."
        ),
        "backup": (
            "Prepare to move to a safer location if conditions worsen."
        ),
    },

    "high": {
        "current": (
            "Avoid flooded roads and move toward a safer area "
            "if local authorities advise evacuation."
        ),
        "backup": (
            "If movement becomes unsafe, move to higher ground "
            "and request assistance."
        ),
    },

    "critical": {
        "current": (
            "Follow official evacuation instructions immediately "
            "and avoid floodwater."
        ),
        "backup": (
            "If evacuation is impossible, move to the safest "
            "elevated location available and request emergency assistance."
        ),
    },
}

EARTHQUAKE_ACTIONS = {
    "low": {
        "current": (
            "Monitor official earthquake updates."
        ),
        "backup": (
            "Check your surroundings for any visible damage."
        ),
    },

    "moderate": {
        "current": (
            "Stay alert for aftershocks and avoid visibly damaged structures."
        ),
        "backup": (
            "Move to a safer open area if your building appears unsafe."
        ),
    },

    "high": {
        "current": (
            "Stay away from damaged buildings and prepare for possible aftershocks."
        ),
        "backup": (
            "Move to a safe open area and request assistance if needed."
        ),
    },

    "critical": {
        "current": (
            "Follow official emergency instructions and avoid severely damaged structures."
        ),
        "backup": (
            "If your location is unsafe, move to the safest accessible open area "
            "and request emergency assistance."
        ),
    },
}


def get_earthquake_actions(
    level: RiskLevel
) -> dict[str, str]:

    return EARTHQUAKE_ACTIONS[level]

def get_flood_actions(level: RiskLevel) -> dict[str, str]:
    return FLOOD_ACTIONS[level]