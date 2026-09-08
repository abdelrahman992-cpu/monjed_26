/**
 * Grid A* navigation with flood/obstacle costs for the rescue robot.
 */

function dist(ax, az, bx, bz) {
  return Math.hypot(ax - bx, az - bz);
}

function cellBlocked(x, z, entities, robotRadius = 0.75) {
  for (const e of entities) {
    if (e.held) continue;
    if (e.kind === "victim" || e.kind === "safe" || e.kind === "fire") continue;
    if (e.passable && e.kind !== "flood") continue;

    if (e.kind === "flood" || (e.r && !e.w)) {
      if (dist(x, z, e.x, e.z) < (e.r || 1) + robotRadius * 0.35) return true;
      continue;
    }

    const hw = (e.w || 1) / 2 + robotRadius * 0.5;
    const hd = (e.d || 1) / 2 + robotRadius * 0.5;
    if (Math.abs(x - e.x) <= hw && Math.abs(z - e.z) <= hd) return true;
  }
  return false;
}

/**
 * A* on a coarse metre grid. Returns waypoints including start-ish → goal.
 */
export function planPath(start, goal, entities, opts = {}) {
  const cell = opts.cell || 1.0;
  const pad = 16;
  const key = (ix, iz) => `${ix},${iz}`;

  const toCell = (x, z) => [
    Math.round(x / cell),
    Math.round(z / cell),
  ];
  const toWorld = (ix, iz) => ({ x: ix * cell, z: iz * cell });

  const [sx, sz] = toCell(start.x, start.z);
  const [gx, gz] = toCell(goal.x, goal.z);

  if (!cellBlocked(goal.x, goal.z, entities, 0.4)) {
    // ok
  }

  const open = new Map();
  const came = new Map();
  const gScore = new Map();
  const fScore = new Map();

  const startK = key(sx, sz);
  open.set(startK, { ix: sx, iz: sz });
  gScore.set(startK, 0);
  fScore.set(startK, dist(sx, sz, gx, gz));

  const dirs = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
    [1, 1],
    [1, -1],
    [-1, 1],
    [-1, -1],
  ];

  let found = null;
  let guard = 0;
  while (open.size && guard++ < 4000) {
    let bestK = null;
    let bestF = Infinity;
    for (const [k, node] of open) {
      const f = fScore.get(k) ?? Infinity;
      if (f < bestF) {
        bestF = f;
        bestK = k;
      }
    }
    if (bestK == null) break;
    const cur = open.get(bestK);
    open.delete(bestK);

    if (cur.ix === gx && cur.iz === gz) {
      found = cur;
      break;
    }

    for (const [dx, dz] of dirs) {
      const nix = cur.ix + dx;
      const niz = cur.iz + dz;
      if (Math.abs(nix) > pad || Math.abs(niz) > pad) continue;
      const w = toWorld(nix, niz);
      // Allow goal cell even if slightly tight
      const isGoal = nix === gx && niz === gz;
      if (!isGoal && cellBlocked(w.x, w.z, entities)) continue;

      const nk = key(nix, niz);
      const stepCost = dx !== 0 && dz !== 0 ? 1.414 : 1;
      const tentative = (gScore.get(bestK) ?? Infinity) + stepCost;
      if (tentative < (gScore.get(nk) ?? Infinity)) {
        came.set(nk, bestK);
        gScore.set(nk, tentative);
        fScore.set(nk, tentative + dist(nix, niz, gx, gz));
        if (!open.has(nk)) open.set(nk, { ix: nix, iz: niz });
      }
    }
  }

  if (!found) {
    // Fallback: greedy sidestep toward goal
    return greedyFallback(start, goal, entities);
  }

  // Reconstruct
  const cells = [];
  let ck = key(found.ix, found.iz);
  while (ck) {
    const [ix, iz] = ck.split(",").map(Number);
    cells.push(toWorld(ix, iz));
    ck = came.get(ck);
  }
  cells.reverse();
  // Start from real pose, end at real goal
  const path = [{ x: start.x, z: start.z }, ...cells.slice(1)];
  path[path.length - 1] = { x: goal.x, z: goal.z };
  return simplify(path, entities);
}

function greedyFallback(start, goal, entities) {
  const path = [{ x: start.x, z: start.z }];
  let cx = start.x;
  let cz = start.z;
  for (let i = 0; i < 60; i++) {
    if (dist(cx, cz, goal.x, goal.z) < 1.2) break;
    const ang = Math.atan2(goal.x - cx, goal.z - cz);
    let placed = false;
    for (const off of [0, 0.7, -0.7, 1.4, -1.4, 2.2, -2.2]) {
      const a = ang + off;
      const nx = cx + Math.sin(a) * 1.2;
      const nz = cz + Math.cos(a) * 1.2;
      if (!cellBlocked(nx, nz, entities)) {
        cx = nx;
        cz = nz;
        path.push({ x: cx, z: cz });
        placed = true;
        break;
      }
    }
    if (!placed) break;
  }
  path.push({ x: goal.x, z: goal.z });
  return path;
}

function simplify(path, entities) {
  if (path.length <= 2) return path;
  const out = [path[0]];
  let i = 0;
  while (i < path.length - 1) {
    let j = path.length - 1;
    for (; j > i + 1; j--) {
      if (lineClear(path[i], path[j], entities)) break;
    }
    out.push(path[j]);
    i = j;
  }
  return out;
}

function lineClear(a, b, entities) {
  const steps = Math.max(2, Math.ceil(dist(a.x, a.z, b.x, b.z) / 0.6));
  for (let i = 1; i < steps; i++) {
    const t = i / steps;
    const x = a.x + (b.x - a.x) * t;
    const z = a.z + (b.z - a.z) * t;
    if (cellBlocked(x, z, entities)) return false;
  }
  return true;
}

export function nearestVictim(pose, entities, range = 3.2) {
  let best = null;
  let bestD = range;
  for (const e of entities) {
    if (e.kind !== "victim") continue;
    const d = dist(pose.x, pose.z, e.x, e.z);
    if (d < bestD) {
      bestD = d;
      best = { entity: e, distance: d, confidence: Math.round(92 - d * 8) };
    }
  }
  return best;
}

export function nearestMovableDebris(pose, entities, range = 2.2) {
  let best = null;
  let bestD = range;
  for (const e of entities) {
    if (e.kind !== "debris" || !e.movable || e.held) continue;
    const d = dist(pose.x, pose.z, e.x, e.z);
    if (d < bestD) {
      bestD = d;
      best = e;
    }
  }
  return best;
}

export function wouldCollide(pose, entities, lookAhead = 0.9) {
  const nx = pose.x + Math.sin(pose.yaw) * lookAhead;
  const nz = pose.z + Math.cos(pose.yaw) * lookAhead;
  return cellBlocked(nx, nz, entities, 0.65);
}

export { cellBlocked as isBlockedCell, dist };
