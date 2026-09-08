import { useEffect, useRef } from "react";
import * as THREE from "three";

/**
 * MONJED rescue-robot 3D viewport (Three.js digital twin).
 * Custom orbit (no examples/jsm) so a partial three install still works.
 */
export default function RescueScene({ snapshot }) {
  const mountRef = useRef(null);
  const apiRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b1220);
    scene.fog = new THREE.Fog(0x0b1220, 28, 55);

    const camera = new THREE.PerspectiveCamera(
      42,
      mount.clientWidth / Math.max(mount.clientHeight, 1),
      0.1,
      120
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.shadowMap.enabled = true;
    mount.appendChild(renderer.domElement);

    scene.add(new THREE.HemisphereLight(0x94a3b8, 0x1e293b, 0.45));
    const sun = new THREE.DirectionalLight(0xffffff, 1.1);
    sun.position.set(12, 22, 10);
    sun.castShadow = true;
    scene.add(sun);
    scene.add(new THREE.AmbientLight(0xffffff, 0.25));

    const worldGroup = new THREE.Group();
    scene.add(worldGroup);
    const robotGroup = buildRobot();
    scene.add(robotGroup);
    const pathLine = new THREE.Line(
      new THREE.BufferGeometry(),
      new THREE.LineBasicMaterial({ color: 0x60a5fa })
    );
    scene.add(pathLine);

    const orbit = {
      target: new THREE.Vector3(0, 0, 0),
      spherical: new THREE.Spherical(28, 0.95, 0.7),
      dragging: false,
      lastX: 0,
      lastY: 0,
    };
    const updateCamera = () => {
      camera.position.setFromSpherical(orbit.spherical).add(orbit.target);
      camera.lookAt(orbit.target);
    };
    updateCamera();

    const onPointerDown = (e) => {
      orbit.dragging = true;
      orbit.lastX = e.clientX;
      orbit.lastY = e.clientY;
    };
    const onPointerUp = () => {
      orbit.dragging = false;
    };
    const onPointerMove = (e) => {
      if (!orbit.dragging) return;
      const dx = e.clientX - orbit.lastX;
      const dy = e.clientY - orbit.lastY;
      orbit.lastX = e.clientX;
      orbit.lastY = e.clientY;
      orbit.spherical.theta -= dx * 0.005;
      orbit.spherical.phi = Math.min(
        Math.max(0.2, orbit.spherical.phi + dy * 0.005),
        Math.PI / 2.05
      );
      updateCamera();
    };
    const onWheel = (e) => {
      e.preventDefault();
      orbit.spherical.radius = Math.min(
        42,
        Math.max(8, orbit.spherical.radius + e.deltaY * 0.02)
      );
      updateCamera();
    };
    renderer.domElement.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointermove", onPointerMove);
    renderer.domElement.addEventListener("wheel", onWheel, { passive: false });

    let raf = 0;
    let disposed = false;
    const onResize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / Math.max(h, 1);
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", onResize);

    const tick = () => {
      if (disposed) return;
      const st = apiRef.current?.status;
      if (
        ["NAVIGATING", "RETURNING", "AVOIDING", "MOVING", "LOW_BATTERY"].includes(
          st
        )
      ) {
        robotGroup.userData.wheels?.forEach((w) => {
          w.rotation.x += 0.12;
        });
      }
      renderer.render(scene, camera);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    apiRef.current = {
      worldGroup,
      robotGroup,
      pathLine,
      status: "IDLE",
      lastWorldId: null,
    };

    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointermove", onPointerMove);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.domElement.removeEventListener("wheel", onWheel);
      renderer.dispose();
      if (renderer.domElement.parentNode === mount) {
        mount.removeChild(renderer.domElement);
      }
      apiRef.current = null;
    };
  }, []);

  useEffect(() => {
    const api = apiRef.current;
    if (!api || !snapshot) return;
    api.status = snapshot.status;

    if (api.lastWorldId !== snapshot.world?.id) {
      clearGroup(api.worldGroup);
      buildWorld(api.worldGroup, snapshot.world);
      api.lastWorldId = snapshot.world?.id;
    } else {
      syncDynamicEntities(api.worldGroup, snapshot.world?.entities || []);
    }

    const pose = snapshot.pose;
    if (pose) {
      api.robotGroup.position.set(pose.x, 0.35, pose.z);
      api.robotGroup.rotation.y = pose.yaw;
    }

    const j = snapshot.armJoints;
    if (j && api.robotGroup.userData.arm) {
      const { base, shoulder, elbow, wrist, gripL, gripR } =
        api.robotGroup.userData.arm;
      base.rotation.y = j.base || 0;
      shoulder.rotation.z = j.shoulder || 0;
      elbow.rotation.z = j.elbow || 0;
      wrist.rotation.z = j.wrist || 0;
      const g = j.gripper || 0;
      gripL.position.x = -(0.08 + g * 0.06);
      gripR.position.x = 0.08 + g * 0.06;
    }

    const bat = snapshot.telemetry?.battery ?? 100;
    if (api.robotGroup.userData.batteryMesh) {
      api.robotGroup.userData.batteryMesh.scale.x = Math.max(0.05, bat / 100);
      api.robotGroup.userData.batteryMesh.material.color.set(
        bat < 20 ? 0xe11d48 : bat < 40 ? 0xf59e0b : 0x14b8a6
      );
    }

    if (api.robotGroup.userData.beacon) {
      const c = statusColor(snapshot.status);
      api.robotGroup.userData.beacon.material.color.set(c);
      api.robotGroup.userData.beacon.material.emissive.set(c);
    }

    const path = snapshot.path || [];
    if (path.length >= 2) {
      const pts = path.map((p) => new THREE.Vector3(p.x, 0.1, p.z));
      api.pathLine.geometry.dispose();
      api.pathLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);
      api.pathLine.visible = true;
    } else {
      api.pathLine.visible = false;
    }
  }, [snapshot]);

  return (
    <div className="relative h-full min-h-[360px] w-full overflow-hidden rounded-lg border border-line bg-[#0b1220]">
      <div ref={mountRef} className="absolute inset-0" />
      <div className="pointer-events-none absolute left-3 top-3 rounded border border-line/60 bg-night/70 px-2.5 py-1.5 backdrop-blur-sm">
        <p className="font-mono text-[10px] tracking-[0.16em] text-slate uppercase">
          Digital twin · {snapshot?.hazard || "—"}
        </p>
        <p className="text-xs text-bone">
          {snapshot?.world?.name || "Loading environment…"}
        </p>
      </div>
    </div>
  );
}

function clearGroup(group) {
  while (group.children.length) {
    const child = group.children[0];
    group.remove(child);
    child.traverse?.((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose());
        else o.material.dispose();
      }
    });
  }
}

function buildWorld(group, world) {
  if (!world) return;
  const groundSize = world.groundSize || 36;
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(groundSize, groundSize),
    new THREE.MeshStandardMaterial({ color: 0x3d4f3f, roughness: 0.95 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  group.add(ground);

  const roadMat = new THREE.MeshStandardMaterial({ color: 0x4b5563 });
  const roadV = new THREE.Mesh(
    new THREE.PlaneGeometry(3.2, groundSize * 0.7),
    roadMat
  );
  roadV.rotation.x = -Math.PI / 2;
  roadV.position.y = 0.02;
  group.add(roadV);
  const roadH = new THREE.Mesh(
    new THREE.PlaneGeometry(groundSize * 0.7, 3.2),
    roadMat.clone()
  );
  roadH.rotation.x = -Math.PI / 2;
  roadH.position.y = 0.021;
  group.add(roadH);

  for (const e of world.entities || []) {
    const mesh = entityMesh(e);
    if (mesh) {
      mesh.userData.entityId = e.id;
      group.add(mesh);
    }
  }
}

function syncDynamicEntities(group, entities) {
  const byId = Object.fromEntries(entities.map((e) => [e.id, e]));
  group.children.forEach((child) => {
    const id = child.userData.entityId;
    if (!id) return;
    const e = byId[id];
    if (!e) return;
    if (e.kind === "debris" || e.kind === "obstacle") {
      child.visible = !e.held;
      child.position.x = e.x;
      child.position.z = e.z;
    }
  });
}

function entityMesh(e) {
  if (e.kind === "building" || e.kind === "house") {
    const h = e.h || 3;
    const g = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(e.w || 3, h, e.d || 3),
      new THREE.MeshStandardMaterial({
        color: e.kind === "house" ? 0xb08968 : 0x94a3b8,
        roughness: 0.85,
      })
    );
    body.castShadow = true;
    g.add(body);
    const roof = new THREE.Mesh(
      new THREE.BoxGeometry((e.w || 3) * 1.05, 0.2, (e.d || 3) * 1.05),
      new THREE.MeshStandardMaterial({ color: 0x78716c })
    );
    roof.position.y = h / 2 + 0.08;
    g.add(roof);
    g.position.set(e.x, h / 2, e.z);
    return g;
  }
  if (e.kind === "wall") {
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(e.w || 4, e.h || 1, e.d || 0.3),
      new THREE.MeshStandardMaterial({ color: 0xa8a29e })
    );
    m.position.set(e.x, (e.h || 1) / 2, e.z);
    m.castShadow = true;
    return m;
  }
  if (e.kind === "tree") {
    const g = new THREE.Group();
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(0.12, 0.16, 1.2, 8),
      new THREE.MeshStandardMaterial({ color: 0x7c4a2d })
    );
    trunk.position.y = 0.6;
    g.add(trunk);
    const leaves = new THREE.Mesh(
      new THREE.ConeGeometry(e.r || 0.6, e.h || 2.5, 8),
      new THREE.MeshStandardMaterial({ color: 0x166534 })
    );
    leaves.position.y = 1.6;
    g.add(leaves);
    g.position.set(e.x, 0, e.z);
    return g;
  }
  if (e.kind === "flood") {
    const m = new THREE.Mesh(
      new THREE.CircleGeometry(e.r || 3, 32),
      new THREE.MeshStandardMaterial({
        color: 0x1d4ed8,
        transparent: true,
        opacity: 0.45,
        roughness: 0.2,
        metalness: 0.3,
      })
    );
    m.rotation.x = -Math.PI / 2;
    m.position.set(e.x, 0.05, e.z);
    return m;
  }
  if (e.kind === "fire") {
    const g = new THREE.Group();
    const zone = new THREE.Mesh(
      new THREE.CircleGeometry(e.r || 2, 28),
      new THREE.MeshStandardMaterial({
        color: 0xea580c,
        transparent: true,
        opacity: 0.35,
        emissive: 0xf97316,
        emissiveIntensity: 0.4,
      })
    );
    zone.rotation.x = -Math.PI / 2;
    zone.position.y = 0.06;
    g.add(zone);
    const flame = new THREE.Mesh(
      new THREE.ConeGeometry(0.6, 2.2, 6),
      new THREE.MeshStandardMaterial({
        color: 0xef4444,
        emissive: 0xf97316,
        emissiveIntensity: 0.9,
        transparent: true,
        opacity: 0.75,
      })
    );
    flame.position.y = 1.2;
    g.add(flame);
    g.position.set(e.x, 0, e.z);
    return g;
  }
  if (e.kind === "debris" || e.kind === "obstacle") {
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(e.w || 1, e.h || 0.8, e.d || 1),
      new THREE.MeshStandardMaterial({
        color: e.movable ? 0xa16207 : 0x57534e,
        roughness: 0.9,
      })
    );
    m.position.set(e.x, (e.h || 0.8) / 2, e.z);
    m.castShadow = true;
    m.visible = !e.held;
    return m;
  }
  if (e.kind === "victim") {
    const g = new THREE.Group();
    g.add(
      new THREE.Mesh(
        new THREE.SphereGeometry(0.35, 16, 16),
        new THREE.MeshStandardMaterial({
          color: 0xf43f5e,
          emissive: 0xfb7185,
          emissiveIntensity: 0.55,
        })
      )
    );
    const pin = new THREE.Mesh(
      new THREE.CylinderGeometry(0.02, 0.02, 0.8, 6),
      new THREE.MeshStandardMaterial({ color: 0xfda4af })
    );
    pin.position.y = 0.7;
    g.add(pin);
    g.position.set(e.x, 0.2, e.z);
    return g;
  }
  if (e.kind === "safe") {
    const m = new THREE.Mesh(
      new THREE.CircleGeometry(e.r || 2, 28),
      new THREE.MeshStandardMaterial({
        color: 0x0d9488,
        transparent: true,
        opacity: 0.35,
        emissive: 0x14b8a6,
        emissiveIntensity: 0.25,
      })
    );
    m.rotation.x = -Math.PI / 2;
    m.position.set(e.x, 0.04, e.z);
    return m;
  }
  return null;
}

function buildRobot() {
  const g = new THREE.Group();
  const chassis = new THREE.Mesh(
    new THREE.BoxGeometry(1.1, 0.35, 1.4),
    new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      metalness: 0.4,
      roughness: 0.45,
    })
  );
  chassis.position.y = 0.15;
  chassis.castShadow = true;
  g.add(chassis);

  const deck = new THREE.Mesh(
    new THREE.BoxGeometry(0.95, 0.12, 1.15),
    new THREE.MeshStandardMaterial({ color: 0x334155 })
  );
  deck.position.y = 0.38;
  g.add(deck);

  const beacon = new THREE.Mesh(
    new THREE.SphereGeometry(0.1, 16, 16),
    new THREE.MeshStandardMaterial({
      color: 0x22c55e,
      emissive: 0x22c55e,
      emissiveIntensity: 0.8,
    })
  );
  beacon.position.set(0, 0.62, -0.35);
  g.add(beacon);

  const mast = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.04, 0.5, 8),
    new THREE.MeshStandardMaterial({ color: 0x64748b })
  );
  mast.position.set(0, 0.7, 0.35);
  g.add(mast);
  const cam = new THREE.Mesh(
    new THREE.BoxGeometry(0.28, 0.16, 0.18),
    new THREE.MeshStandardMaterial({ color: 0x0f172a })
  );
  cam.position.set(0, 0.95, 0.4);
  g.add(cam);

  const us = new THREE.Mesh(
    new THREE.BoxGeometry(0.35, 0.12, 0.1),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b })
  );
  us.position.set(0, 0.35, 0.72);
  g.add(us);

  const wheels = [];
  for (const [x, z] of [
    [-0.62, 0.35],
    [0.62, 0.35],
    [-0.62, -0.35],
    [0.62, -0.35],
  ]) {
    const w = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.28, 0.18, 14),
      new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.9 })
    );
    w.rotation.z = Math.PI / 2;
    w.position.set(x, 0.05, z);
    g.add(w);
    wheels.push(w);
  }

  const base = new THREE.Group();
  base.position.set(0, 0.45, -0.15);
  const baseMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08, 0.1, 0.25, 10),
    new THREE.MeshStandardMaterial({ color: 0x94a3b8 })
  );
  baseMesh.position.y = 0.15;
  base.add(baseMesh);

  const shoulder = new THREE.Group();
  shoulder.position.set(0, 0.28, 0);
  const upper = new THREE.Mesh(
    new THREE.BoxGeometry(0.12, 0.7, 0.12),
    new THREE.MeshStandardMaterial({ color: 0xcbd5e1 })
  );
  upper.position.y = 0.35;
  shoulder.add(upper);

  const elbow = new THREE.Group();
  elbow.position.set(0, 0.7, 0);
  const fore = new THREE.Mesh(
    new THREE.BoxGeometry(0.1, 0.55, 0.1),
    new THREE.MeshStandardMaterial({ color: 0xe2e8f0 })
  );
  fore.position.y = 0.28;
  elbow.add(fore);

  const wrist = new THREE.Group();
  wrist.position.set(0, 0.55, 0);
  const wristMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.18, 0.12, 0.12),
    new THREE.MeshStandardMaterial({ color: 0x64748b })
  );
  wristMesh.position.y = 0.08;
  wrist.add(wristMesh);
  const gripL = new THREE.Mesh(
    new THREE.BoxGeometry(0.04, 0.22, 0.06),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8 })
  );
  gripL.position.set(-0.08, 0.2, 0);
  wrist.add(gripL);
  const gripR = gripL.clone();
  gripR.position.x = 0.08;
  wrist.add(gripR);

  elbow.add(wrist);
  shoulder.add(elbow);
  base.add(shoulder);
  g.add(base);

  const batteryMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.7, 0.06, 0.08),
    new THREE.MeshStandardMaterial({ color: 0x14b8a6 })
  );
  batteryMesh.position.set(0, 0.2, -0.55);
  g.add(batteryMesh);

  g.userData = {
    wheels,
    beacon,
    batteryMesh,
    arm: { base, shoulder, elbow, wrist, gripL, gripR },
  };
  return g;
}

function statusColor(status) {
  switch (status) {
    case "EMERGENCY":
    case "FAILED":
      return 0xe11d48;
    case "VICTIM_DETECTED":
      return 0xf59e0b;
    case "COMPLETED":
      return 0x14b8a6;
    case "ARM_ACTIVE":
    case "INSPECTING":
      return 0x38bdf8;
    case "AVOIDING":
    case "LOW_BATTERY":
      return 0xf97316;
    case "NAVIGATING":
    case "RETURNING":
    case "MOVING":
      return 0x3b82f6;
    case "PAUSED":
      return 0x94a3b8;
    default:
      return 0x22c55e;
  }
}
