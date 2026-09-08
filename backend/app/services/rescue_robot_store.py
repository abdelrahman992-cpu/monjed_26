"""
In-memory + optional Mongo mirror for rescue-robot digital twin.

Keeps MONJED informed of missions / telemetry without coupling the
real-time 3D tick loop to the database.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.rescue_robot import (
    RescueMissionCreate,
    RescueMissionRecord,
    RescueTelemetryIn,
    RescueTelemetryRecord,
)

_missions: dict[str, RescueMissionRecord] = {}
_latest_telemetry: RescueTelemetryRecord | None = None
_event_log: list[dict] = []


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_mission(payload: RescueMissionCreate) -> RescueMissionRecord:
    now = _now()
    mid = payload.mission_id or f"MISSION-{uuid4().hex[:6].upper()}"
    rec = RescueMissionRecord(
        mission_id=mid,
        mission_type=payload.mission_type,
        hazard=payload.hazard,
        priority=payload.priority,
        target_label=payload.target_label,
        objective=payload.objective,
        robot_id=payload.robot_id,
        status="created",
        created_at=now,
        updated_at=now,
    )
    _missions[mid] = rec
    _event_log.insert(
        0,
        {
            "ts": now.isoformat(),
            "message": f"Mission {mid} created ({payload.hazard})",
        },
    )
    _event_log[:] = _event_log[:200]
    return rec


def list_missions() -> list[RescueMissionRecord]:
    return sorted(
        _missions.values(),
        key=lambda m: m.created_at,
        reverse=True,
    )


def get_mission(mission_id: str) -> RescueMissionRecord | None:
    return _missions.get(mission_id)


def update_mission_status(
    mission_id: str, status: str, findings: list | None = None
) -> RescueMissionRecord:
    rec = _missions.get(mission_id)
    if rec is None:
        raise KeyError(mission_id)
    data = rec.model_dump()
    data["status"] = status
    data["updated_at"] = _now()
    if findings is not None:
        data["findings"] = findings
    updated = RescueMissionRecord(**data)
    _missions[mission_id] = updated
    return updated


def ingest_telemetry(payload: RescueTelemetryIn) -> RescueTelemetryRecord:
    global _latest_telemetry
    rec = RescueTelemetryRecord(
        **payload.model_dump(),
        received_at=_now(),
    )
    _latest_telemetry = rec

    if payload.missionId and payload.missionId in _missions:
        st = payload.status
        mapped = "active"
        if st == "COMPLETED":
            mapped = "completed"
        elif st in ("FAILED", "EMERGENCY"):
            mapped = st.lower()
        elif st == "PAUSED":
            mapped = "paused"
        update_mission_status(
            payload.missionId,
            mapped,
            findings=payload.findings or None,
        )

    for ev in payload.events or []:
        _event_log.insert(
            0,
            {
                "ts": ev.get("ts") or _now().isoformat(),
                "message": ev.get("message") or str(ev),
                "level": ev.get("level"),
            },
        )
    _event_log[:] = _event_log[:200]
    return rec


def latest_telemetry() -> RescueTelemetryRecord | None:
    return _latest_telemetry


def recent_events(limit: int = 50) -> list[dict]:
    return _event_log[:limit]
