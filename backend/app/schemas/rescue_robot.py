from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


HazardType = Literal["FLOOD", "EARTHQUAKE", "FIRE"]
Priority = Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]


class RescueMissionCreate(BaseModel):
    mission_id: str | None = None
    mission_type: str = "Search & Rescue"
    hazard: str = "FLOOD"
    priority: Priority = "HIGH"
    target_label: str = "Building 04"
    objective: str = "Inspect affected area"
    robot_id: str = "MONJED-R01"


class RescueMissionRecord(BaseModel):
    mission_id: str
    mission_type: str
    hazard: str
    priority: str
    target_label: str
    objective: str
    robot_id: str
    status: str = "created"
    created_at: datetime
    updated_at: datetime
    findings: list[dict[str, Any]] = Field(default_factory=list)


class RescueTelemetryIn(BaseModel):
    """Stable contract — same shape from sim or future ESP32 gateway."""

    robotId: str = "MONJED-R01"
    status: str
    battery: float
    temperature: float
    gasLevel: str
    position: dict[str, float]
    missionId: str | None = None
    ultrasonic: dict[str, float] | None = None
    speed: float | None = None
    yaw: float | None = None
    imu: dict[str, Any] | None = None
    cameraOnline: bool | None = None
    arm: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    events: list[dict[str, Any]] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    hazard: str | None = None
    riskLevel: str | None = None


class RescueTelemetryRecord(RescueTelemetryIn):
    received_at: datetime
