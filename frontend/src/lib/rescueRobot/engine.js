/**
 * MONJED Rescue Robot — mission controller + simulation engine.
 *
 * Architecture:
 *   MONJED UI → MissionController → SimulatedMotors/Sensors/Arm → World
 *                             ↓
 *                      Telemetry + Event log → (optional) API mirror
 *
 * Replace Simulated* with Physical* later; keep this controller.
 */

import { cloneScenario } from "./world.js";
import {
  SimulatedArm,
  SimulatedMotors,
  SimulatedSensors,
  BATTERY_CRITICAL,
  TEMP_CRITICAL,
} from "./simulatedHardware.js";
import {
  nearestMovableDebris,
  nearestVictim,
  planPath,
  wouldCollide,
  dist,
} from "./navigation.js";

const ROBOT_ID = "MONJED-R01";
const OBSTACLE_STOP_M = 1.1;
const INSPECT_RADIUS = 1.8;

function nowIso() {
  return new Date().toISOString();
}

function timeLabel() {
  return new Date().toLocaleTimeString("en-GB", { hour12: false });
}

export function createEngine(initialScenario = "flood") {
  const listeners = new Set();

  let world = cloneScenario(initialScenario);
  const motors = new SimulatedMotors(world.base);
  const sensors = new SimulatedSensors(motors);
  const arm = new SimulatedArm();

  /** @type {object} */
  let state = blankState(world);

  function blankState(w) {
    return {
      robotId: ROBOT_ID,
      online: true,
      status: "IDLE",
      scenarioId: w.id,
      hazard: w.hazard,
      riskLevel: w.riskLevel,
      affectedArea: w.affectedArea,
      mission: null,
      path: [],
      pathIndex: 0,
      paused: false,
      victimAlert: null,
      armHoldingId: null,
      findings: [],
      events: [
        {
          id: crypto.randomUUID(),
          ts: nowIso(),
          label: timeLabel(),
          message: `World loaded: ${w.name}`,
          level: "info",
        },
      ],
      telemetry: null,
      lastTick: performance.now(),
      inspectTimer: 0,
      armPhase: null,
      demoRunning: false,
    };
  }

  function emit() {
    const snapshot = getSnapshot();
    for (const fn of listeners) fn(snapshot);
  }

  function log(message, level = "info") {
    state.events = [
      {
        id: crypto.randomUUID(),
        ts: nowIso(),
        label: timeLabel(),
        message,
        level,
      },
      ...state.events,
    ].slice(0, 120);
  }

  function setStatus(status) {
    if (state.status === status) return;
    state.status = status;
    log(`Status → ${status}`, status === "EMERGENCY" ? "danger" : "info");
  }

  function refreshTelemetry(entities) {
    const frame = sensors.read(entities, { hazard: world.hazard });
    const pose = motors.getPose();
    const joints = arm.getJoints();
    state.telemetry = {
      robotId: ROBOT_ID,
      status: state.status,
      battery: frame.batteryPct,
      temperature: frame.temperatureC,
      gasLevel: frame.gasLevel,
      ultrasonic: frame.ultrasonic,
      speed: frame.imu.moving ? 1.8 : 0,
      position: { x: pose.x, y: pose.z },
      yaw: pose.yaw,
      missionId: state.mission?.id || null,
      imu: frame.imu,
      cameraOnline: frame.cameraOnline,
      arm: {
        busy: arm.isBusy(),
        joints,
        holdingId: arm.holdingId,
      },
      warnings: buildWarnings(frame, state),
    };
    return frame;
  }

  function buildWarnings(frame, st) {
    const w = [];
    if (frame.batteryPct <= BATTERY_CRITICAL) w.push("CRITICAL_BATTERY");
    if (frame.temperatureC >= TEMP_CRITICAL) w.push("CRITICAL_TEMPERATURE");
    else if (frame.temperatureC >= 55) w.push("HIGH_TEMPERATURE");
    if (frame.gasLevel === "HIGH" || frame.gasLevel === "CRITICAL")
      w.push("HIGH_GAS");
    if (frame.ultrasonic.front < OBSTACLE_STOP_M) w.push("OBSTACLE_AHEAD");
    if (st.victimAlert) w.push("VICTIM_DETECTED");
    return w;
  }

  function getSnapshot() {
    return {
      robotId: ROBOT_ID,
      online: state.online,
      status: state.status,
      scenarioId: state.scenarioId,
      hazard: state.hazard,
      riskLevel: state.riskLevel,
      affectedArea: state.affectedArea,
      mission: state.mission ? { ...state.mission } : null,
      path: state.path.map((p) => ({ ...p })),
      pathIndex: state.pathIndex,
      paused: state.paused,
      victimAlert: state.victimAlert ? { ...state.victimAlert } : null,
      findings: [...state.findings],
      events: state.events.map((e) => ({ ...e })),
      telemetry: state.telemetry ? { ...state.telemetry } : null,
      world: {
        id: world.id,
        name: world.name,
        base: { ...world.base },
        targets: world.targets.map((t) => ({ ...t })),
        entities: world.entities.map((e) => ({ ...e })),
        groundSize: world.groundSize,
      },
      pose: motors.getPose(),
      armJoints: arm.getJoints(),
      demoRunning: state.demoRunning,
    };
  }

  function subscribe(fn) {
    listeners.add(fn);
    fn(getSnapshot());
    return () => listeners.delete(fn);
  }

  function loadScenario(id) {
    world = cloneScenario(id);
    motors.teleport(world.base.x, world.base.z, 0);
    sensors.recharge(100);
    arm.execute("RESET_ARM");
    state = blankState(world);
    refreshTelemetry(world.entities);
    log(`Scenario set: ${world.hazard} / ${world.riskLevel}`);
    emit();
  }

  function createMission(spec) {
    const target =
      world.targets.find((t) => t.id === spec.targetId) || world.targets[0];
    const mission = {
      id: `MISSION-${String(Date.now()).slice(-6)}`,
      type: spec.type || "Search & Rescue",
      hazard: world.hazard,
      priority: spec.priority || "HIGH",
      targetId: target.id,
      targetLabel: target.label,
      objective: spec.objective || `Inspect ${target.label}`,
      goal: { x: target.x, z: target.z },
      phase: "created",
      createdAt: nowIso(),
    };
    state.mission = mission;
    state.victimAlert = null;
    state.findings = [];
    state.path = [];
    state.pathIndex = 0;
    state.inspectTimer = 0;
    state.armPhase = null;
    setStatus("IDLE");
    log(
      `Mission created: ${mission.type} → ${mission.targetLabel} (${mission.priority})`
    );
    emit();
    return mission;
  }

  function dispatch() {
    if (!state.mission) {
      createMission({
        type: "Search & Rescue",
        priority: "HIGH",
        targetId: world.targets[0]?.id,
      });
    }
    const pose = motors.getPose();
    state.path = planPath(pose, state.mission.goal, world.entities);
    state.pathIndex = 1;
    state.mission.phase = "dispatched";
    state.paused = false;
    setStatus("NAVIGATING");
    log(`Robot ${ROBOT_ID} dispatched`);
    log("Robot started navigation");
    emit();
  }

  function pause() {
    if (!state.mission) return;
    state.paused = true;
    motors.stop();
    setStatus("PAUSED");
    emit();
  }

  function resume() {
    if (!state.mission || !state.paused) return;
    state.paused = false;
    setStatus(state.pathIndex > 0 ? "NAVIGATING" : "IDLE");
    log("Mission resumed");
    emit();
  }

  function returnToBase() {
    const keepEmergency = state.status === "EMERGENCY";
    if (!state.mission) {
      state.mission = {
        id: `MISSION-RTB`,
        type: "Return",
        hazard: world.hazard,
        priority: "HIGH",
        targetId: "base",
        targetLabel: "Base",
        objective: "Return to safe zone",
        goal: { ...world.base },
        phase: "returning",
        createdAt: nowIso(),
      };
    } else {
      state.mission.goal = { ...world.base };
      state.mission.phase = "returning";
      state.mission.targetLabel = "Base / safe zone";
    }
    beginUnstick("Robot returning to base");
    if (keepEmergency) {
      state.status = "EMERGENCY";
      log("Emergency retreat to base", "danger");
    } else if (
      state.status === "LOW_BATTERY" ||
      sensors.batteryPct <= BATTERY_CRITICAL
    ) {
      setStatus("LOW_BATTERY");
      log("Low-battery return to base", "warn");
    } else {
      setStatus("RETURNING");
    }
    emit();
  }

  /** Back up away from the bumper hit, then replan home. */
  function beginUnstick(message) {
    const pose = motors.getPose();
    const goal = state.mission?.goal || world.base;
    // Instant geometric backoff so Return-to-Base is not stuck forever
    // against a wall/debris (sensors alone can thrash in corners).
    const backX = clampNum(pose.x - Math.sin(pose.yaw) * 2.0, -15, 15);
    const backZ = clampNum(pose.z - Math.cos(pose.yaw) * 2.0, -15, 15);
    const newYaw = pose.yaw + 1.1;
    motors.teleport(backX, backZ, newYaw);

    state._escapeUntil = Date.now() + 600;
    state._ignoreObstaclesUntil = Date.now() + 700;
    state._lastReplan = 0;
    state._stuckSince = null;
    const cleared = motors.getPose();
    state._lastProgress = { x: cleared.x, z: cleared.z, t: Date.now() };
    motors.setVelocity({ linear: 0.4, angular: 0 });
    state.path = planPath(cleared, goal, world.entities);
    state.pathIndex = Math.min(1, Math.max(0, state.path.length - 1));
    state.paused = false;
    if (message) log(message);
    log("Cleared obstacle contact — routing to base");
  }

  function clampNum(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function stop() {
    motors.stop();
    state.paused = true;
    state.path = [];
    setStatus("FAILED");
    if (state.mission) state.mission.phase = "stopped";
    log("STOP commanded — mission halted", "danger");
    emit();
  }

  async function tryArmClearDebris() {
    const pose = motors.getPose();
    const debris = nearestMovableDebris(pose, world.entities, 2.4);
    if (!debris || arm.isBusy()) return false;

    setStatus("ARM_ACTIVE");
    log(`Arm: approaching debris ${debris.id}`);
    await arm.execute("MOVE_ARM");
    await wait(200);
    const pick = await arm.execute("PICK_OBJECT", { objectId: debris.id });
    if (pick.ok) {
      debris.held = true;
      state.armHoldingId = debris.id;
      log("Arm: CLOSE_GRIPPER / PICK_OBJECT");
      // Drop aside
      debris.x = pose.x + Math.sin(pose.yaw + 1.2) * 1.5;
      debris.z = pose.z + Math.cos(pose.yaw + 1.2) * 1.5;
      debris.held = false;
      debris.passable = true;
      await arm.execute("DROP_OBJECT");
      log("Arm: debris cleared from path");
      state.armHoldingId = null;
      // Replan
      if (state.mission) {
        state.path = planPath(pose, state.mission.goal, world.entities);
        state.pathIndex = 1;
        log("Route recalculated after debris clear");
      }
    }
    setStatus(
      state.mission?.phase === "returning" ? "RETURNING" : "NAVIGATING"
    );
    return true;
  }

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function followPath(dt, frame) {
    if (!state.path.length || state.pathIndex >= state.path.length) {
      motors.stop();
      return "arrived";
    }

    const pose = motors.getPose();
    const goal = state.mission?.goal;
    const atBaseGoal =
      state.mission?.phase === "returning" ||
      state.mission?.targetId === "base";
    const arriveR = atBaseGoal ? 1.5 : INSPECT_RADIUS;
    const wallNow = Date.now();

    if (goal && dist(pose.x, pose.z, goal.x, goal.z) < arriveR) {
      motors.stop();
      return "arrived";
    }

    // Progress watchdog: if barely moving toward goal, force another unstick
    if (goal && state.mission?.phase === "returning") {
      const lp = state._lastProgress;
      if (!lp) {
        state._lastProgress = { x: pose.x, z: pose.z, t: wallNow };
      } else if (dist(pose.x, pose.z, lp.x, lp.z) > 1.2) {
        state._lastProgress = { x: pose.x, z: pose.z, t: wallNow };
      } else if (wallNow - lp.t > 3500) {
        beginUnstick("Still blocked — forcing clear and replan");
        return "escaping";
      }
    }

    // Forced reverse after Return-to-Base / unstick
    if (state._escapeUntil && wallNow < state._escapeUntil) {
      const turn =
        frame.ultrasonic.left >= frame.ultrasonic.right ? -0.7 : 0.7;
      motors.setVelocity({ linear: -0.95, angular: turn });
      if (!["EMERGENCY", "LOW_BATTERY"].includes(state.status)) {
        setStatus(
          state.mission?.phase === "returning" ? "RETURNING" : "AVOIDING"
        );
      }
      return "escaping";
    }

    // Just finished escaping — replan from the new clear pose
    if (state._escapeUntil && wallNow >= state._escapeUntil) {
      state._escapeUntil = 0;
      if (goal) {
        state.path = planPath(pose, goal, world.entities);
        state.pathIndex = Math.min(1, Math.max(0, state.path.length - 1));
        state._lastProgress = { x: pose.x, z: pose.z, t: wallNow };
        log("Escape done — new route set");
      }
    }

    const ignoreBumper =
      state._ignoreObstaclesUntil && wallNow < state._ignoreObstaclesUntil;

    const obstacleClose =
      !ignoreBumper &&
      (frame.ultrasonic.front < OBSTACLE_STOP_M ||
        wouldCollide(pose, world.entities));

    // Near the destination, buildings/debris count as "arrived to inspect"
    if (
      obstacleClose &&
      goal &&
      !atBaseGoal &&
      dist(pose.x, pose.z, goal.x, goal.z) < INSPECT_RADIUS + 1.2
    ) {
      motors.stop();
      return "arrived";
    }

    if (obstacleClose) {
      const turn =
        frame.ultrasonic.left >= frame.ultrasonic.right ? -0.85 : 0.85;
      motors.setVelocity({ linear: -0.75, angular: turn });
      setStatus("AVOIDING");
      if (!state._lastReplan || wallNow - state._lastReplan > 1000) {
        state._lastReplan = wallNow;
        log("Obstacle detected", "warn");
        state.path = planPath(pose, state.mission.goal, world.entities);
        state.pathIndex = Math.min(1, Math.max(0, state.path.length - 1));
        log("Route recalculated");
      }
      return "avoiding";
    }

    const waypoint = state.path[state.pathIndex];
    const dx = waypoint.x - pose.x;
    const dz = waypoint.z - pose.z;
    const distW = Math.hypot(dx, dz);
    if (distW < 0.65) {
      state.pathIndex += 1;
      return "waypoint";
    }

    const desiredYaw = Math.atan2(dx, dz);
    let err = desiredYaw - pose.yaw;
    while (err > Math.PI) err -= Math.PI * 2;
    while (err < -Math.PI) err += Math.PI * 2;

    const angular = clamp(err * 1.8, -1, 1);
    const linear = Math.abs(err) < 0.5 ? 0.95 : 0.28;
    motors.setVelocity({ linear, angular });
    if (!["EMERGENCY", "LOW_BATTERY", "VICTIM_DETECTED"].includes(state.status)) {
      setStatus(
        state.mission?.phase === "returning" ? "RETURNING" : "NAVIGATING"
      );
    }
    return "moving";
  }

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function tick(now = performance.now()) {
    const rawDt = (now - state.lastTick) / 1000;
    const dt = Number.isFinite(rawDt)
      ? Math.min(0.05, Math.max(0, rawDt || 0.016))
      : 0.016;
    state.lastTick = now;

    if (!state.online) {
      emit();
      return getSnapshot();
    }

    const active =
      !state.paused &&
      state.mission &&
      !["COMPLETED", "FAILED", "IDLE"].includes(state.status);

    const frame = refreshTelemetry(world.entities);

    // Battery drain
    sensors.drainBattery(dt, active || state.status === "INSPECTING");

    if (
      frame.batteryPct <= BATTERY_CRITICAL &&
      state.mission?.phase !== "returning" &&
      !["RETURNING", "COMPLETED", "LOW_BATTERY", "EMERGENCY", "FAILED"].includes(
        state.status
      )
    ) {
      log("Battery critical — auto return to base", "danger");
      returnToBase();
      setStatus("LOW_BATTERY");
    }

    // Fire emergency
    if (
      world.id === "fire" &&
      (frame.temperatureC >= TEMP_CRITICAL || frame.gasLevel === "CRITICAL") &&
      state.mission?.phase !== "returning" &&
      !["EMERGENCY", "RETURNING", "COMPLETED", "FAILED"].includes(state.status)
    ) {
      setStatus("EMERGENCY");
      log(
        `Emergency: temperature ${frame.temperatureC}°C / gas ${frame.gasLevel}`,
        "danger"
      );
      log("Emergency status transmitted to MONJED", "danger");
      returnToBase();
    }

    if (state.paused || !state.mission) {
      motors.stop();
      sensors.setMotionFlag(false);
      motors.step(dt, true);
      emit();
      return getSnapshot();
    }

    // Victim detection while operating
    if (!state.victimAlert && ["NAVIGATING", "INSPECTING", "AVOIDING", "ARM_ACTIVE"].includes(state.status)) {
      const hit = nearestVictim(motors.getPose(), world.entities, 3.0);
      if (hit) {
        state.victimAlert = {
          location: hit.entity.label || world.affectedArea,
          confidence: Math.max(70, hit.confidence),
          x: hit.entity.x,
          z: hit.entity.z,
          at: nowIso(),
        };
        state.findings.push({
          type: "victim",
          ...state.victimAlert,
        });
        setStatus("VICTIM_DETECTED");
        log("⚠ Possible victim detected", "alert");
        log(
          `Victim coordinates transmitted to MONJED (${hit.entity.x.toFixed(1)}, ${hit.entity.z.toFixed(1)})`,
          "alert"
        );
      }
    }

    // Earthquake: clear debris if blocked nearby
    if (
      world.id === "earthquake" &&
      state.status === "AVOIDING" &&
      !arm.isBusy() &&
      !state.armPhase
    ) {
      const debris = nearestMovableDebris(motors.getPose(), world.entities, 2.2);
      if (debris) {
        state.armPhase = "clearing";
        tryArmClearDebris().finally(() => {
          state.armPhase = null;
        });
      }
    }

    if (["COMPLETED", "FAILED", "EMERGENCY"].includes(state.status) && state.status !== "EMERGENCY") {
      motors.stop();
      emit();
      return getSnapshot();
    }

    // Mission phases
    const phase = state.mission.phase;

    if (phase === "dispatched" || phase === "en_route") {
      state.mission.phase = "en_route";
      const nav = followPath(dt, frame);
      // Only block forward push into obstacles; reverse/turn always allowed
      const blockForward =
        nav === "avoiding" && frame.ultrasonic.front < 0.6;
      const moved = motors.step(dt, blockForward);
      sensors.setMotionFlag(moved);

      const atGoal =
        nav === "arrived" ||
        dist(
          motors.getPose().x,
          motors.getPose().z,
          state.mission.goal.x,
          state.mission.goal.z
        ) < INSPECT_RADIUS;

      if (atGoal) {
        motors.stop();
        state.mission.phase = "inspecting";
        state.inspectTimer = 0;
        setStatus("INSPECTING");
        log(`Robot reached ${state.mission.targetLabel}`);
        log(`Temperature sensor reading: ${frame.temperatureC}°C`);
        log(`Gas level: ${frame.gasLevel}`);
      }
    } else if (phase === "returning") {
      const nav = followPath(dt, frame);
      const blockForward =
        nav === "avoiding" && frame.ultrasonic.front < 0.6;
      const moved = motors.step(dt, blockForward);
      sensors.setMotionFlag(moved);
      if (
        nav === "arrived" ||
        dist(
          motors.getPose().x,
          motors.getPose().z,
          world.base.x,
          world.base.z
        ) < 1.5
      ) {
        motors.stop();
        setStatus("COMPLETED");
        state.mission.phase = "completed";
        log("Robot reached base");
        log("Mission completed");
        state.demoRunning = false;
      }
    } else if (phase === "inspecting") {
      motors.stop();
      sensors.setMotionFlag(false);
      state.inspectTimer += dt;
      if (state.inspectTimer > 2.8) {
        log("Inspection completed");
        state.findings.push({
          type: "inspection",
          target: state.mission.targetLabel,
          temperature: frame.temperatureC,
          gasLevel: frame.gasLevel,
          at: nowIso(),
        });
        state.mission.phase = "returning";
        state.mission.goal = { ...world.base };
        state.path = planPath(motors.getPose(), world.base, world.entities);
        state.pathIndex = 1;
        setStatus("RETURNING");
        log("Robot returning to base");
      }
    }

    // Keep held debris attached visually
    if (arm.holdingId) {
      const e = world.entities.find((x) => x.id === arm.holdingId);
      if (e) {
        const pose = motors.getPose();
        e.x = pose.x + Math.sin(pose.yaw) * 0.9;
        e.z = pose.z + Math.cos(pose.yaw) * 0.9;
        e.held = true;
      }
    }

    emit();
    return getSnapshot();
  }

  /** Automated demo: flood → mission → navigate → victim → return */
  function startDemo() {
    loadScenario("flood");
    state.demoRunning = true;
    log("DEMO MODE started", "alert");
    log(`FLOOD DETECTED — risk ${world.riskLevel}`, "alert");
    log(`Affected area: ${world.affectedArea}`);
    createMission({
      type: "Search & Rescue",
      priority: "HIGH",
      targetId: "building-04",
      objective: "Inspect Building 04 / locate victims",
    });
    dispatch();
    emit();
  }

  // Initial telemetry
  refreshTelemetry(world.entities);

  return {
    subscribe,
    getSnapshot,
    loadScenario,
    createMission,
    dispatch,
    pause,
    resume,
    returnToBase,
    stop,
    tick,
    startDemo,
    getWorld: () => world,
    robotId: ROBOT_ID,
  };
}
