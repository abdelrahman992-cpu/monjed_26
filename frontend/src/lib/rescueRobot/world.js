/**
 * Scenario world definitions for the MONJED 3D rescue sim.
 * Coordinates are metres on an XZ ground plane. Origin = map centre.
 */

/** @typedef {'flood'|'earthquake'|'fire'} ScenarioId */

/**
 * @typedef {object} WorldEntity
 * @property {string} id
 * @property {'building'|'house'|'tree'|'wall'|'debris'|'flood'|'fire'|'victim'|'safe'|'obstacle'} kind
 * @property {number} x
 * @property {number} z
 * @property {number} [w]
 * @property {number} [h]
 * @property {number} [d]
 * @property {number} [r] radius for circular hazards
 * @property {boolean} [passable]
 * @property {boolean} [movable] debris the arm can clear
 * @property {boolean} [held]
 * @property {string} [label]
 * @property {number} [tempBoost]
 * @property {number} [gasBoost]
 */

/**
 * @typedef {object} ScenarioWorld
 * @property {ScenarioId} id
 * @property {string} name
 * @property {string} hazard
 * @property {'LOW'|'MODERATE'|'HIGH'|'CRITICAL'} riskLevel
 * @property {string} affectedArea
 * @property {{ x: number, z: number }} base
 * @property {{ id: string, label: string, x: number, z: number }[]} targets
 * @property {WorldEntity[]} entities
 * @property {number} groundSize
 */

const SHARED_URBAN = [
  { id: "b1", kind: "building", x: -8, z: -6, w: 4, h: 4, d: 3.5, label: "Building 01" },
  { id: "b2", kind: "building", x: 7, z: -7, w: 5, h: 5, d: 4, label: "Building 02" },
  { id: "b3", kind: "house", x: -10, z: 5, w: 3, h: 2.2, d: 3, label: "House 01" },
  { id: "b4", kind: "house", x: 9, z: 6, w: 3.2, h: 2.4, d: 3.2, label: "House 02" },
  { id: "wall1", kind: "wall", x: -6, z: -2, w: 4, h: 1.2, d: 0.35, passable: false },
  { id: "t1", kind: "tree", x: -4, z: 8, r: 0.6, h: 3 },
  { id: "t2", kind: "tree", x: 3, z: 9, r: 0.55, h: 2.8 },
  { id: "t3", kind: "tree", x: -12, z: -2, r: 0.5, h: 2.5 },
  {
    id: "safe",
    kind: "safe",
    x: -12,
    z: -10,
    r: 2.2,
    label: "Safe zone / Base",
    passable: true,
  },
];

/** @type {Record<ScenarioId, ScenarioWorld>} */
export const SCENARIOS = {
  flood: {
    id: "flood",
    name: "Flooded urban sector",
    hazard: "FLOOD",
    riskLevel: "HIGH",
    affectedArea: "Sector A — riverside community",
    base: { x: -12, z: -10 },
    groundSize: 36,
    targets: [
      { id: "building-04", label: "Building 04", x: 6, z: 4 },
      { id: "sector-a", label: "Sector A centre", x: 2, z: 2 },
      { id: "house-02", label: "House 02", x: 9, z: 6 },
    ],
    entities: [
      ...SHARED_URBAN,
      { id: "b04", kind: "building", x: 6, z: 4, w: 4.5, h: 3.5, d: 4, label: "Building 04" },
      {
        id: "flood1",
        kind: "flood",
        x: 1,
        z: 5,
        r: 3.2,
        passable: false,
        label: "Flooded road",
      },
      {
        id: "flood2",
        kind: "flood",
        x: 5,
        z: -5,
        r: 2.6,
        passable: false,
        label: "Flooded courtyard",
      },
      {
        id: "obs1",
        kind: "obstacle",
        x: -3,
        z: 1,
        w: 1.2,
        h: 0.9,
        d: 1.1,
        passable: false,
        label: "Debris pile",
      },
      {
        id: "obs2",
        kind: "obstacle",
        x: 2,
        z: 8,
        w: 1.2,
        h: 0.8,
        d: 1,
        passable: false,
      },
      {
        id: "v1",
        kind: "victim",
        x: 5.2,
        z: 3.2,
        r: 0.45,
        label: "Possible victim — Building 04",
        passable: true,
      },
    ],
  },

  earthquake: {
    id: "earthquake",
    name: "Earthquake debris field",
    hazard: "EARTHQUAKE",
    riskLevel: "CRITICAL",
    affectedArea: "Sector B — collapsed block",
    base: { x: -12, z: -10 },
    groundSize: 36,
    targets: [
      { id: "building-04", label: "Building 04 (damaged)", x: 5, z: 3 },
      { id: "debris-lane", label: "Debris lane", x: 1, z: 1 },
    ],
    entities: [
      ...SHARED_URBAN.map((e) =>
        e.id === "b2"
          ? { ...e, h: 2.2, label: "Building 02 (damaged)" }
          : e
      ),
      {
        id: "b04",
        kind: "building",
        x: 5,
        z: 3,
        w: 4,
        h: 2.4,
        d: 3.5,
        label: "Building 04 (damaged)",
      },
      {
        id: "debris1",
        kind: "debris",
        x: 0,
        z: 1,
        w: 1.1,
        h: 0.7,
        d: 1.1,
        passable: false,
        movable: true,
        held: false,
        label: "Movable debris",
      },
      {
        id: "debris2",
        kind: "debris",
        x: 3,
        z: 0,
        w: 1.3,
        h: 0.85,
        d: 1,
        passable: false,
        movable: false,
      },
      {
        id: "debris3",
        kind: "obstacle",
        x: -3,
        z: 2,
        w: 1.5,
        h: 1,
        d: 1.2,
        passable: false,
      },
      {
        id: "v1",
        kind: "victim",
        x: 4.5,
        z: 2.4,
        r: 0.45,
        label: "Possible victim under debris",
        passable: true,
      },
    ],
  },

  fire: {
    id: "fire",
    name: "Urban fire / smoke zone",
    hazard: "FIRE",
    riskLevel: "CRITICAL",
    affectedArea: "Sector C — market fire",
    base: { x: -12, z: -10 },
    groundSize: 36,
    targets: [
      { id: "fire-edge", label: "Fire perimeter", x: 3, z: 2 },
      { id: "building-04", label: "Building 04", x: 6, z: 4 },
    ],
    entities: [
      ...SHARED_URBAN,
      { id: "b04", kind: "building", x: 6, z: 4, w: 4.5, h: 3.5, d: 4, label: "Building 04" },
      {
        id: "fire1",
        kind: "fire",
        x: 3,
        z: 2,
        r: 3.5,
        passable: true,
        tempBoost: 55,
        gasBoost: 2,
        label: "Active fire zone",
      },
      {
        id: "fire2",
        kind: "fire",
        x: 6,
        z: 0,
        r: 2.2,
        passable: true,
        tempBoost: 40,
        gasBoost: 1.5,
      },
      {
        id: "obs1",
        kind: "obstacle",
        x: -1,
        z: 1,
        w: 1.2,
        h: 0.9,
        d: 1,
        passable: false,
      },
      {
        id: "v1",
        kind: "victim",
        x: 7,
        z: 4.5,
        r: 0.45,
        label: "Possible victim near Building 04",
        passable: true,
      },
    ],
  },
};

export function cloneScenario(id) {
  const src = SCENARIOS[id] || SCENARIOS.flood;
  return structuredClone(src);
}

export function listScenarios() {
  return Object.values(SCENARIOS).map((s) => ({
    id: s.id,
    name: s.name,
    hazard: s.hazard,
    riskLevel: s.riskLevel,
    affectedArea: s.affectedArea,
    targets: s.targets.map((t) => ({ id: t.id, label: t.label })),
  }));
}
