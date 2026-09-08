"""
MONJED Rescue Robot API — mission + telemetry mirror for the 3D digital twin.

Prefix: /rescue-robot
"""

from fastapi import APIRouter, HTTPException

from app.schemas.rescue_robot import (
    RescueMissionCreate,
    RescueMissionRecord,
    RescueTelemetryIn,
    RescueTelemetryRecord,
)
from app.services import rescue_robot_store as store

router = APIRouter(prefix="/rescue-robot", tags=["rescue-robot"])


@router.get("/health")
def health():
    return {"ok": True, "service": "rescue-robot", "mode": "digital-twin"}


@router.post("/missions", response_model=RescueMissionRecord)
def create_mission(payload: RescueMissionCreate):
    return store.create_mission(payload)


@router.get("/missions", response_model=list[RescueMissionRecord])
def list_missions():
    return store.list_missions()


@router.get("/missions/{mission_id}", response_model=RescueMissionRecord)
def get_mission(mission_id: str):
    rec = store.get_mission(mission_id)
    if rec is None:
        raise HTTPException(404, f"Mission not found: {mission_id}")
    return rec


@router.post("/telemetry", response_model=RescueTelemetryRecord)
def post_telemetry(payload: RescueTelemetryIn):
    """Ingest live frame from sim (today) or ESP32 gateway (later)."""
    return store.ingest_telemetry(payload)


@router.get("/telemetry/latest")
def get_latest_telemetry():
    rec = store.latest_telemetry()
    if rec is None:
        return {"robotId": "MONJED-R01", "status": "IDLE", "message": "no telemetry yet"}
    return rec


@router.get("/events")
def get_events(limit: int = 50):
    return {"events": store.recent_events(limit)}
