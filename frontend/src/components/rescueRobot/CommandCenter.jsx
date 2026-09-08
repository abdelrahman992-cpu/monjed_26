import { listScenarios } from "../../lib/rescueRobot/world.js";

const MISSION_TYPES = ["Search & Rescue", "Hazard Inspect", "Supply Check"];
const PRIORITIES = ["LOW", "MODERATE", "HIGH", "CRITICAL"];

/**
 * MONJED command-center side panels: hazard, mission, telemetry, events, controls.
 */
export default function CommandCenter({
  snapshot,
  missionForm,
  setMissionForm,
  onCreateMission,
  onDispatch,
  onPause,
  onResume,
  onReturn,
  onStop,
  onScenario,
  onDemo,
}) {
  const t = snapshot?.telemetry;
  const scenarios = listScenarios();
  const targets =
    snapshot?.world?.targets ||
    scenarios.find((s) => s.id === missionForm.scenarioId)?.targets ||
    [];

  return (
    <div className="flex h-full flex-col gap-3 overflow-y-auto">
      {/* Hazard */}
      <Panel title="Hazard / risk">
        <Row label="Hazard" value={snapshot?.hazard || "—"} accent />
        <Row label="Risk" value={snapshot?.riskLevel || "—"} danger={snapshot?.riskLevel === "CRITICAL" || snapshot?.riskLevel === "HIGH"} />
        <Row label="Area" value={snapshot?.affectedArea || "—"} />
        <label className="mt-2 block">
          <span className="font-mono text-[10px] uppercase tracking-wide text-slate">
            Scenario
          </span>
          <select
            className="mt-1 w-full rounded-md border border-line bg-night px-2 py-1.5 text-sm text-bone"
            value={missionForm.scenarioId}
            onChange={(e) => {
              const id = e.target.value;
              setMissionForm((f) => ({ ...f, scenarioId: id, targetId: "" }));
              onScenario(id);
            }}
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.hazard} — {s.name}
              </option>
            ))}
          </select>
        </label>
      </Panel>

      {/* Robot */}
      <Panel title="Robot">
        <Row label="Unit" value={snapshot?.robotId || "MONJED-R01"} />
        <Row label="Status" value={snapshot?.status || "—"} accent />
        <Row
          label="Battery"
          value={t ? `${Math.round(t.battery)}%` : "—"}
          danger={t && t.battery < 20}
        />
        <Row
          label="Location"
          value={
            t
              ? `${t.position.x.toFixed(1)}, ${t.position.y.toFixed(1)}`
              : "—"
          }
        />
        <Row
          label="Mission"
          value={snapshot?.mission?.objective || "None"}
        />
      </Panel>

      {/* Telemetry */}
      <Panel title="Live telemetry">
        {t ? (
          <div className="grid grid-cols-2 gap-2">
            <Stat label="Temp" value={`${t.temperature}°C`} warn={t.temperature >= 55} />
            <Stat label="Gas" value={t.gasLevel} warn={t.gasLevel !== "NORMAL"} />
            <Stat label="Front" value={`${t.ultrasonic.front} m`} warn={t.ultrasonic.front < 1.2} />
            <Stat label="Left" value={`${t.ultrasonic.left} m`} />
            <Stat label="Right" value={`${t.ultrasonic.right} m`} />
            <Stat label="Speed" value={`${Number(t.speed).toFixed(1)} m/s`} />
            <Stat
              label="Arm"
              value={t.arm?.busy ? "ACTIVE" : t.arm?.holdingId ? "HOLDING" : "IDLE"}
            />
            <Stat label="Cam" value={t.cameraOnline ? "ONLINE" : "OFF"} />
          </div>
        ) : (
          <p className="text-xs text-slate">Waiting for sensor frame…</p>
        )}
        {t?.warnings?.length > 0 && (
          <ul className="mt-2 space-y-1">
            {t.warnings.map((w) => (
              <li
                key={w}
                className="rounded border border-crimson/30 bg-crimson/10 px-2 py-1 font-mono text-[10px] text-crimson"
              >
                {w}
              </li>
            ))}
          </ul>
        )}
      </Panel>

      {/* Mission create */}
      <Panel title="Create robot mission">
        <Field label="Mission type">
          <select
            className="field"
            value={missionForm.type}
            onChange={(e) =>
              setMissionForm((f) => ({ ...f, type: e.target.value }))
            }
          >
            {MISSION_TYPES.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </Field>
        <Field label="Priority">
          <select
            className="field"
            value={missionForm.priority}
            onChange={(e) =>
              setMissionForm((f) => ({ ...f, priority: e.target.value }))
            }
          >
            {PRIORITIES.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </Field>
        <Field label="Target">
          <select
            className="field"
            value={missionForm.targetId || targets[0]?.id || ""}
            onChange={(e) =>
              setMissionForm((f) => ({ ...f, targetId: e.target.value }))
            }
          >
            {targets.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Objective">
          <input
            className="field"
            value={missionForm.objective}
            onChange={(e) =>
              setMissionForm((f) => ({ ...f, objective: e.target.value }))
            }
            placeholder="Inspect affected area"
          />
        </Field>
        <div className="mt-2 flex flex-wrap gap-2">
          <Btn onClick={onCreateMission}>Create mission</Btn>
          <Btn primary onClick={onDispatch}>
            Dispatch robot
          </Btn>
        </div>
      </Panel>

      {/* Controls */}
      <Panel title="Mission controls">
        <div className="flex flex-wrap gap-2">
          <Btn onClick={onPause}>Pause</Btn>
          <Btn onClick={onResume}>Resume</Btn>
          <Btn onClick={onReturn}>Return to base</Btn>
          <Btn danger onClick={onStop}>
            Stop
          </Btn>
          <Btn primary onClick={onDemo}>
            Demo mode
          </Btn>
        </div>
      </Panel>

      {/* Victim alert */}
      {snapshot?.victimAlert && (
        <Panel title="⚠ Possible victim detected" alert>
          <Row label="Location" value={snapshot.victimAlert.location} />
          <Row
            label="Confidence"
            value={`${snapshot.victimAlert.confidence}%`}
          />
          <Row
            label="Coords"
            value={`${snapshot.victimAlert.x.toFixed(1)}, ${snapshot.victimAlert.z.toFixed(1)}`}
          />
          <p className="mt-2 text-xs text-mist">
            Robot action: coordinates transmitted to MONJED
          </p>
        </Panel>
      )}

      {/* Event log */}
      <Panel title="Live event log">
        <ul className="max-h-48 space-y-1.5 overflow-y-auto font-mono text-[11px]">
          {(snapshot?.events || []).map((e) => (
            <li
              key={e.id}
              className={
                e.level === "danger" || e.level === "alert"
                  ? "text-crimson"
                  : e.level === "warn"
                    ? "text-amber"
                    : "text-mist"
              }
            >
              <span className="text-slate">{e.label}</span> {e.message}
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

function Panel({ title, children, alert }) {
  return (
    <section
      className={`rounded-lg border px-3 py-3 ${
        alert
          ? "border-crimson/40 bg-crimson/10"
          : "border-line bg-panel/50"
      }`}
    >
      <p className="mb-2 font-mono text-[10px] tracking-[0.16em] text-slate uppercase">
        {title}
      </p>
      {children}
    </section>
  );
}

function Row({ label, value, accent, danger }) {
  return (
    <div className="flex items-start justify-between gap-2 text-sm">
      <span className="text-slate">{label}</span>
      <span
        className={`text-right font-medium ${
          danger ? "text-crimson" : accent ? "text-teal" : "text-bone"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

function Stat({ label, value, warn }) {
  return (
    <div className="rounded-md border border-line bg-night/40 px-2 py-1.5">
      <p className="font-mono text-[9px] uppercase tracking-wide text-slate">
        {label}
      </p>
      <p className={`text-sm font-medium ${warn ? "text-crimson" : "text-bone"}`}>
        {value}
      </p>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="mt-2 block">
      <span className="font-mono text-[10px] uppercase tracking-wide text-slate">
        {label}
      </span>
      <div className="mt-1 [&_.field]:w-full [&_.field]:rounded-md [&_.field]:border [&_.field]:border-line [&_.field]:bg-night [&_.field]:px-2 [&_.field]:py-1.5 [&_.field]:text-sm [&_.field]:text-bone">
        {children}
      </div>
    </label>
  );
}

function Btn({ children, onClick, primary, danger }) {
  const tone = danger
    ? "border-crimson/40 text-crimson hover:bg-crimson/10"
    : primary
      ? "border-teal/40 bg-teal/15 text-teal hover:bg-teal/25"
      : "border-line text-mist hover:text-bone hover:bg-raised/40";
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-md border px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-wide transition ${tone}`}
    >
      {children}
    </button>
  );
}
