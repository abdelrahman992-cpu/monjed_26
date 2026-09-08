/**
 * Simulated hardware drivers implementing Motor / Sensor / Arm interfaces.
 * Swap these for Physical* drivers when ESP32/Arduino hardware arrives.
 */

import {
  ArmInterface,
  MotorInterface,
  SensorInterface,
} from "./interfaces.js";

const TEMP_SAFE_MAX = 55;
const TEMP_CRITICAL = 75;
const GAS_HIGH_THRESHOLD = 1.2;
const BATTERY_DRAIN_PER_S = 0.35;
const BATTERY_CRITICAL = 15;

function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}

function dist2(ax, az, bx, bz) {
  const dx = ax - bx;
  const dz = az - bz;
  return Math.hypot(dx, dz);
}

function rayHitDistance(ox, oz, dirX, dirZ, entities, maxRange) {
  let best = maxRange;
  for (const e of entities) {
    if (e.passable || e.held || e.kind === "victim" || e.kind === "safe") continue;
    if (e.kind === "flood" || e.kind === "fire") continue;

    const halfW = (e.w || e.r * 2 || 1) / 2;
    const halfD = (e.d || e.r * 2 || 1) / 2;
    // AABB vs ray (XZ)
    for (let t = 0.15; t <= maxRange; t += 0.15) {
      const px = ox + dirX * t;
      const pz = oz + dirZ * t;
      if (
        Math.abs(px - e.x) <= halfW + 0.25 &&
        Math.abs(pz - e.z) <= halfD + 0.25
      ) {
        best = Math.min(best, t);
        break;
      }
    }
  }
  return Number(best.toFixed(2));
}

export class SimulatedMotors extends MotorInterface {
  constructor(base = { x: -12, z: -10 }) {
    super();
    this.pose = { x: base.x, z: base.z, yaw: 0 };
    this.cmd = { linear: 0, angular: 0 };
    this.maxSpeed = 2.4; // m/s
    this.maxYaw = 1.8; // rad/s
  }

  setVelocity(cmd) {
    this.cmd = {
      linear: clamp(cmd.linear ?? 0, -1, 1),
      angular: clamp(cmd.angular ?? 0, -1, 1),
    };
  }

  getPose() {
    return { ...this.pose };
  }

  stop() {
    this.cmd = { linear: 0, angular: 0 };
  }

  /**
   * Integrate pose for dt seconds.
   * `blocked` only stops forward motion — reverse + turning still work so the
   * robot can escape when pressed against an obstacle (e.g. Return to Base).
   */
  step(dt, blocked = false) {
    let linCmd = this.cmd.linear;
    if (blocked && linCmd > 0) linCmd = 0;
    const lin = linCmd * this.maxSpeed;
    const ang = this.cmd.angular * this.maxYaw;
    this.pose.yaw += ang * dt;
    this.pose.x += Math.sin(this.pose.yaw) * lin * dt;
    this.pose.z += Math.cos(this.pose.yaw) * lin * dt;
    // Keep inside the sim map
    this.pose.x = clamp(this.pose.x, -16, 16);
    this.pose.z = clamp(this.pose.z, -16, 16);
    return Math.abs(lin) > 0.05 || Math.abs(ang) > 0.05;
  }

  teleport(x, z, yaw = 0) {
    this.pose = { x, z, yaw };
    this.stop();
  }
}

export class SimulatedSensors extends SensorInterface {
  constructor(motors) {
    super();
    this.motors = motors;
    this.batteryPct = 100;
    this._moving = false;
    this._lastPose = motors.getPose();
    this.tempOverride = null;
    this.gasOverride = null;
  }

  setMotionFlag(moving) {
    this._moving = moving;
  }

  drainBattery(dt, active = true) {
    if (!active) return;
    this.batteryPct = clamp(
      this.batteryPct - BATTERY_DRAIN_PER_S * dt,
      0,
      100
    );
  }

  recharge(to = 100) {
    this.batteryPct = clamp(to, 0, 100);
  }

  /**
   * @param {import('./world.js').WorldEntity[]} entities
   * @param {object} [env]
   */
  read(entities = [], env = {}) {
    const pose = this.motors.getPose();
    const yaw = pose.yaw;
    const forward = { x: Math.sin(yaw), z: Math.cos(yaw) };
    const left = { x: Math.sin(yaw - Math.PI / 2), z: Math.cos(yaw - Math.PI / 2) };
    const right = { x: Math.sin(yaw + Math.PI / 2), z: Math.cos(yaw + Math.PI / 2) };

    const ultrasonic = {
      front: rayHitDistance(pose.x, pose.z, forward.x, forward.z, entities, 6),
      left: rayHitDistance(pose.x, pose.z, left.x, left.z, entities, 6),
      right: rayHitDistance(pose.x, pose.z, right.x, right.z, entities, 6),
    };

    let temperatureC = 28 + Math.sin(Date.now() / 4000) * 1.5;
    let gasScore = 0;

    for (const e of entities) {
      if (e.kind === "fire" || e.kind === "flood") {
        const d = dist2(pose.x, pose.z, e.x, e.z);
        const r = e.r || 2;
        if (d < r + 1.5) {
          const proximity = clamp(1 - d / (r + 1.5), 0, 1);
          if (e.kind === "fire") {
            temperatureC += (e.tempBoost || 40) * proximity;
            gasScore += (e.gasBoost || 1) * proximity;
          } else if (e.kind === "flood") {
            temperatureC -= 2 * proximity;
          }
        }
      }
    }

    if (this.tempOverride != null) temperatureC = this.tempOverride;
    if (this.gasOverride != null) gasScore = this.gasOverride;

    let gasLevel = "NORMAL";
    if (gasScore >= 2 || temperatureC >= TEMP_CRITICAL) gasLevel = "CRITICAL";
    else if (gasScore >= GAS_HIGH_THRESHOLD || temperatureC >= TEMP_SAFE_MAX)
      gasLevel = "HIGH";
    else if (gasScore >= 0.5 || temperatureC >= 40) gasLevel = "ELEVATED";

    const dx = pose.x - this._lastPose.x;
    const dz = pose.z - this._lastPose.z;
    const moving = this._moving || Math.hypot(dx, dz) > 0.01;
    this._lastPose = { ...pose };

    return {
      ultrasonic,
      temperatureC: Number(temperatureC.toFixed(1)),
      gasLevel,
      imu: {
        roll: Number((Math.sin(Date.now() / 700) * 0.03).toFixed(3)),
        pitch: Number((Math.cos(Date.now() / 900) * 0.02).toFixed(3)),
        yaw: Number(pose.yaw.toFixed(3)),
        moving,
      },
      batteryPct: Number(this.batteryPct.toFixed(1)),
      gps: { x: Number(pose.x.toFixed(2)), z: Number(pose.z.toFixed(2)) },
      cameraOnline: this.batteryPct > 5,
      thresholds: {
        tempSafeMax: TEMP_SAFE_MAX,
        tempCritical: TEMP_CRITICAL,
        batteryCritical: BATTERY_CRITICAL,
      },
      envHint: env.hazard || null,
    };
  }
}

export class SimulatedArm extends ArmInterface {
  constructor() {
    super();
    this.joints = {
      base: 0,
      shoulder: 0.4,
      elbow: -0.7,
      wrist: 0.2,
      gripper: 0,
    };
    this.busyUntil = 0;
    this.holdingId = null;
  }

  isBusy() {
    return Date.now() < this.busyUntil;
  }

  getJoints() {
    return { ...this.joints };
  }

  async execute(command, params = {}) {
    if (this.isBusy()) {
      return { ok: false, reason: "arm_busy" };
    }

    const hold = (ms) => {
      this.busyUntil = Date.now() + ms;
    };

    switch (command) {
      case "OPEN_GRIPPER":
        this.joints.gripper = 0;
        hold(400);
        return { ok: true };
      case "CLOSE_GRIPPER":
        this.joints.gripper = 1;
        hold(400);
        return { ok: true };
      case "RESET_ARM":
        this.joints = {
          base: 0,
          shoulder: 0.4,
          elbow: -0.7,
          wrist: 0.2,
          gripper: 0,
        };
        this.holdingId = null;
        hold(600);
        return { ok: true };
      case "MOVE_ARM":
        this.joints = {
          ...this.joints,
          base: params.base ?? this.joints.base,
          shoulder: params.shoulder ?? 0.9,
          elbow: params.elbow ?? -1.1,
          wrist: params.wrist ?? 0.3,
        };
        hold(800);
        return { ok: true };
      case "PICK_OBJECT":
        this.joints = {
          ...this.joints,
          shoulder: 1.0,
          elbow: -1.2,
          wrist: 0.4,
          gripper: 1,
        };
        this.holdingId = params.objectId || null;
        hold(1200);
        return { ok: true, holdingId: this.holdingId };
      case "DROP_OBJECT": {
        const dropped = this.holdingId;
        this.joints.gripper = 0;
        this.holdingId = null;
        hold(700);
        return { ok: true, droppedId: dropped };
      }
      default:
        return { ok: false, reason: "unknown_command" };
    }
  }
}

export { TEMP_SAFE_MAX, TEMP_CRITICAL, BATTERY_CRITICAL };
