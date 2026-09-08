/**
 * Hardware abstraction contracts for MONJED rescue robot.
 *
 * Simulated* classes implement these today.
 * Later: Physical* drivers (ESP32 / Arduino / ROS 2) swap in
 * without changing MissionController or the MONJED command UI.
 */

/** @typedef {'IDLE'|'ONLINE'|'OFFLINE'|'MOVING'|'NAVIGATING'|'AVOIDING'|'INSPECTING'|'ARM_ACTIVE'|'VICTIM_DETECTED'|'RETURNING'|'COMPLETED'|'PAUSED'|'EMERGENCY'|'FAILED'|'LOW_BATTERY'} RobotStatus */

/**
 * @typedef {object} MotorCommand
 * @property {number} linear  -1..1 forward/back
 * @property {number} angular -1..1 yaw rate
 */

/**
 * @typedef {object} Pose2D
 * @property {number} x
 * @property {number} z  world depth axis (Three.js)
 * @property {number} yaw radians
 */

/**
 * @typedef {object} UltrasonicReading
 * @property {number} front
 * @property {number} left
 * @property {number} right
 */

/**
 * @typedef {object} SensorFrame
 * @property {UltrasonicReading} ultrasonic
 * @property {number} temperatureC
 * @property {'NORMAL'|'ELEVATED'|'HIGH'|'CRITICAL'} gasLevel
 * @property {{ roll: number, pitch: number, yaw: number, moving: boolean }} imu
 * @property {number} batteryPct
 * @property {{ x: number, z: number }} gps
 * @property {boolean} cameraOnline
 */

/**
 * @typedef {object} ArmJoints
 * @property {number} base
 * @property {number} shoulder
 * @property {number} elbow
 * @property {number} wrist
 * @property {number} gripper 0 open .. 1 closed
 */

export const ARM_COMMANDS = Object.freeze([
  "MOVE_ARM",
  "OPEN_GRIPPER",
  "CLOSE_GRIPPER",
  "PICK_OBJECT",
  "DROP_OBJECT",
  "RESET_ARM",
]);

/**
 * Motor interface — differential-drive base.
 * @interface
 */
export class MotorInterface {
  /** @param {MotorCommand} _cmd */
  setVelocity(_cmd) {
    throw new Error("MotorInterface.setVelocity not implemented");
  }
  /** @returns {Pose2D} */
  getPose() {
    throw new Error("MotorInterface.getPose not implemented");
  }
  stop() {
    throw new Error("MotorInterface.stop not implemented");
  }
}

/**
 * Sensor interface — ultrasonic, temp, gas, IMU, battery, GPS, camera.
 * @interface
 */
export class SensorInterface {
  /** @returns {SensorFrame} */
  read() {
    throw new Error("SensorInterface.read not implemented");
  }
}

/**
 * Robotic arm interface.
 * @interface
 */
export class ArmInterface {
  /** @param {string} _command @param {object} [_params] */
  async execute(_command, _params = {}) {
    throw new Error("ArmInterface.execute not implemented");
  }
  /** @returns {ArmJoints} */
  getJoints() {
    throw new Error("ArmInterface.getJoints not implemented");
  }
  /** @returns {boolean} */
  isBusy() {
    throw new Error("ArmInterface.isBusy not implemented");
  }
}

/**
 * Telemetry publisher — sim posts here; later hardware gateway posts same shape.
 * @interface
 */
export class TelemetryInterface {
  /** @param {object} _frame */
  publish(_frame) {
    throw new Error("TelemetryInterface.publish not implemented");
  }
}

/**
 * Mission interface — create / control lifecycle.
 * @interface
 */
export class MissionInterface {
  create(_spec) {
    throw new Error("MissionInterface.create not implemented");
  }
  dispatch(_missionId) {
    throw new Error("MissionInterface.dispatch not implemented");
  }
  pause() {
    throw new Error("MissionInterface.pause not implemented");
  }
  resume() {
    throw new Error("MissionInterface.resume not implemented");
  }
  returnToBase() {
    throw new Error("MissionInterface.returnToBase not implemented");
  }
  stop() {
    throw new Error("MissionInterface.stop not implemented");
  }
}
