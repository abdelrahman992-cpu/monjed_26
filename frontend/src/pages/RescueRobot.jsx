import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Radio } from "lucide-react";
import MonjedLogo from "../components/MonjedLogo.jsx";
import ThemeToggle from "../components/ThemeToggle.jsx";
import RescueScene from "../components/rescueRobot/RescueScene.jsx";
import CommandCenter from "../components/rescueRobot/CommandCenter.jsx";
import { createEngine } from "../lib/rescueRobot/engine.js";
import {
  mirrorRescueTelemetry,
  createRescueMissionRemote,
} from "../lib/api.js";

/**
 * MONJED AI Rescue Robot Simulation — digital twin command center.
 */
export default function RescueRobotPage() {
  const engineRef = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const [missionForm, setMissionForm] = useState({
    scenarioId: "flood",
    type: "Search & Rescue",
    priority: "HIGH",
    targetId: "building-04",
    objective: "Inspect affected area / locate victims",
  });
  const lastMirror = useRef(0);

  useEffect(() => {
    const engine = createEngine("flood");
    engineRef.current = engine;
    const unsub = engine.subscribe(setSnapshot);

    let raf = 0;
    const loop = (t) => {
      engine.tick(t);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      unsub();
      engineRef.current = null;
    };
  }, []);

  // Mirror telemetry to MONJED API (best-effort; sim stays local if API down)
  useEffect(() => {
    if (!snapshot?.telemetry) return;
    const now = Date.now();
    if (now - lastMirror.current < 1200) return;
    lastMirror.current = now;
    mirrorRescueTelemetry({
      ...snapshot.telemetry,
      events: snapshot.events?.slice(0, 5),
      findings: snapshot.findings,
      hazard: snapshot.hazard,
      riskLevel: snapshot.riskLevel,
    }).catch(() => {});
  }, [snapshot]);

  const eng = () => engineRef.current;

  const onCreateMission = async () => {
    const mission = eng()?.createMission({
      type: missionForm.type,
      priority: missionForm.priority,
      targetId: missionForm.targetId,
      objective: missionForm.objective,
    });
    if (mission) {
      createRescueMissionRemote({
        mission_id: mission.id,
        mission_type: mission.type,
        hazard: mission.hazard,
        priority: mission.priority,
        target_label: mission.targetLabel,
        objective: mission.objective,
        robot_id: "MONJED-R01",
      }).catch(() => {});
    }
  };

  return (
    <div className="min-h-screen bg-night text-bone">
      <header className="border-b border-line bg-panel/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-center gap-3">
            <Link
              to="/admin"
              className="inline-flex items-center gap-1.5 text-sm text-slate hover:text-bone"
            >
              <ArrowLeft size={16} /> Admin
            </Link>
            <MonjedLogo className="h-7" />
            <div>
              <p className="font-mono text-[10px] tracking-[0.18em] text-amber uppercase">
                AI rescue robot
              </p>
              <h1 className="font-display text-lg font-bold leading-tight">
                Digital twin command center
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-teal/30 px-2.5 py-1 font-mono text-[10px] text-teal">
              <Radio size={11} />
              {snapshot?.online ? "ROBOT ONLINE" : "OFFLINE"} ·{" "}
              {snapshot?.status || "…"}
            </span>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1600px] gap-4 p-4 lg:grid-cols-[1fr_340px]">
        <div className="flex min-h-[70vh] flex-col gap-3">
          <div className="flex-1">
            <RescueScene snapshot={snapshot} />
          </div>
          <p className="text-xs text-slate">
            Simulated hardware drivers (motors, sensors, arm) feed a real mission
            controller. Same telemetry contract can later come from ESP32 /
            Arduino.
          </p>
        </div>

        <aside className="lg:max-h-[calc(100vh-5.5rem)] lg:overflow-hidden">
          <CommandCenter
            snapshot={snapshot}
            missionForm={missionForm}
            setMissionForm={setMissionForm}
            onCreateMission={onCreateMission}
            onDispatch={() => {
              onCreateMission();
              setTimeout(() => eng()?.dispatch(), 50);
            }}
            onPause={() => eng()?.pause()}
            onResume={() => eng()?.resume()}
            onReturn={() => eng()?.returnToBase()}
            onStop={() => eng()?.stop()}
            onScenario={(id) => {
              eng()?.loadScenario(id);
              setMissionForm((f) => ({
                ...f,
                scenarioId: id,
                targetId: "",
              }));
            }}
            onDemo={() => eng()?.startDemo()}
          />
        </aside>
      </main>
    </div>
  );
}
