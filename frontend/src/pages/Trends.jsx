import { useEffect, useId, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Waves,
  Mountain,
  Droplets,
  Split,
  TrendingUp,
  ArrowRight,
  Activity,
} from "lucide-react";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import { KENYA_TRENDS } from "../data/mockRisk.js";
import { dashboardRisks } from "../lib/api.js";

function levelFromScore(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

const HOVER_COLOR = "#22c55e";
const SAMPLE_BANNER =
  "Showing sample trends — connect Mongo / run pipeline for live /dashboard/risks";

function buildTrendsFromSnapshots(snapshots) {
  if (!Array.isArray(snapshots) || snapshots.length === 0) return [];

  const byDay = new Map();

  for (const snap of snapshots) {
    const raw =
      snap?.created_at || snap?.evaluated_at || snap?.timestamp || null;
    if (!raw) continue;
    const d = new Date(raw);
    if (Number.isNaN(d.getTime())) continue;
    const key = d.toISOString().slice(0, 10);
    if (!byDay.has(key)) {
      byDay.set(key, {
        day: key,
        label: d.toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
        }),
        floodScore: 0,
        quakeScore: 0,
        rainfall: 0,
        _hasFlood: false,
        _hasQuake: false,
      });
    }
    const row = byDay.get(key);
    const score = Number(snap.risk_score);
    if (!Number.isFinite(score)) continue;
    const hazard = String(snap.hazard || "").toLowerCase();
    if (hazard.includes("flood")) {
      row.floodScore = Math.max(row.floodScore, score);
      row._hasFlood = true;
      const rain =
        snap.rainfall_24h_mm ??
        snap.rainfall ??
        snap.inputs?.rainfall_24h_mm;
      if (rain != null && Number.isFinite(Number(rain))) {
        row.rainfall = Math.max(row.rainfall, Number(rain));
      }
    } else if (hazard.includes("earthquake") || hazard.includes("quake")) {
      row.quakeScore = Math.max(row.quakeScore, score);
      row._hasQuake = true;
    }
  }

  let series = [...byDay.values()]
    .map(({ _hasFlood, _hasQuake, ...rest }) => rest)
    .sort((a, b) => String(a.day).localeCompare(String(b.day)));

  // Fallback: chronological last-N flood vs quake if date grouping is sparse
  if (series.length < 2) {
    const floods = snapshots
      .filter((s) => String(s.hazard || "").toLowerCase().includes("flood"))
      .slice(0, 30)
      .reverse();
    const quakes = snapshots
      .filter((s) => {
        const h = String(s.hazard || "").toLowerCase();
        return h.includes("earthquake") || h.includes("quake");
      })
      .slice(0, 30)
      .reverse();
    const n = Math.max(floods.length, quakes.length, 1);
    series = Array.from({ length: n }, (_, i) => {
      const f = floods[i];
      const q = quakes[i];
      const raw = f?.created_at || q?.created_at || null;
      const d = raw ? new Date(raw) : new Date();
      return {
        day: i + 1,
        label: Number.isNaN(d.getTime())
          ? `#${i + 1}`
          : d.toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
            }),
        floodScore: Number(f?.risk_score) || 0,
        quakeScore: Number(q?.risk_score) || 0,
        rainfall: Number(f?.rainfall_24h_mm ?? f?.rainfall) || 0,
      };
    });
  }

  return series;
}

function ScoreRing({ score, label, color, Icon }) {
  const r = 38;
  const c = 2 * Math.PI * r;
  const offset = c - (Math.min(100, score) / 100) * c;
  return (
    <div className="flex items-center gap-4">
      <div className="relative h-24 w-24 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke="currentColor"
            strokeWidth="7"
            className="text-line"
          />
          <circle
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="7"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
            className="transition-[stroke-dashoffset] duration-700 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon size={14} style={{ color }} strokeWidth={1.75} />
          <span className="mt-0.5 font-display text-xl font-bold tabular-nums">
            {Math.round(score)}
          </span>
        </div>
      </div>
      <div>
        <p className="font-mono text-[10px] tracking-[0.14em] text-slate">
          {label}
        </p>
        <div className="mt-1.5">
          <RiskBadge level={levelFromScore(score)} />
        </div>
      </div>
    </div>
  );
}

function ChartFrame({
  series,
  lines,
  yMax,
  yTicks,
  selectedDay,
  onSelect,
  height = 220,
  showThresholds = false,
}) {
  const uid = useId().replace(/:/g, "");
  const [hoverIdx, setHoverIdx] = useState(null);
  const W = 640;
  const H = height;
  const pad = { t: 12, r: 14, b: 28, l: 36 };
  const innerW = W - pad.l - pad.r;
  const innerH = H - pad.t - pad.b;
  const n = series.length;
  const xAt = (i) => pad.l + (i / Math.max(1, n - 1)) * innerW;
  const yAt = (v) => pad.t + innerH - (v / yMax) * innerH;
  const selectedIdx = series.findIndex((d) => d.day === selectedDay);
  const colW = innerW / Math.max(1, n);

  function pathFor(key) {
    return series
      .map((d, i) => `${i === 0 ? "M" : "L"} ${xAt(i)} ${yAt(d[key])}`)
      .join(" ");
  }

  function areaFor(key) {
    const line = pathFor(key);
    return `${line} L ${xAt(n - 1)} ${yAt(0)} L ${xAt(0)} ${yAt(0)} Z`;
  }

  const labelIdx = [0, Math.floor((n - 1) / 3), Math.floor(((n - 1) * 2) / 3), n - 1].filter(
    (i, idx, arr) => i >= 0 && i < n && arr.indexOf(i) === idx
  );
  const hoverData = hoverIdx != null ? series[hoverIdx] : null;

  return (
    <div className="w-full">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img">
        <defs>
          {lines.map((line) => (
            <linearGradient
              key={`g-${line.key}`}
              id={`${uid}-${line.key}`}
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor={line.color} stopOpacity="0.24" />
              <stop offset="100%" stopColor={line.color} stopOpacity="0" />
            </linearGradient>
          ))}
        </defs>

        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              x1={pad.l}
              x2={W - pad.r}
              y1={yAt(tick)}
              y2={yAt(tick)}
              stroke="currentColor"
              className="text-line"
              strokeWidth="1"
            />
            <text
              x={pad.l - 6}
              y={yAt(tick) + 3}
              textAnchor="end"
              className="fill-slate"
              style={{ fontSize: 9, fontFamily: "IBM Plex Mono, monospace" }}
            >
              {tick}
            </text>
          </g>
        ))}

        {showThresholds &&
          [
            { v: 40, label: "MED" },
            { v: 70, label: "HIGH" },
          ].map((t) => (
            <g key={t.v}>
              <line
                x1={pad.l}
                x2={W - pad.r}
                y1={yAt(t.v)}
                y2={yAt(t.v)}
                stroke="currentColor"
                className="text-muted"
                strokeWidth="1"
                strokeDasharray="4 5"
              />
              <text
                x={W - pad.r}
                y={yAt(t.v) - 3}
                textAnchor="end"
                className="fill-muted"
                style={{ fontSize: 8, fontFamily: "IBM Plex Mono, monospace" }}
              >
                {t.label}
              </text>
            </g>
          ))}

        {hoverIdx != null && (
          <line
            x1={xAt(hoverIdx)}
            x2={xAt(hoverIdx)}
            y1={pad.t}
            y2={pad.t + innerH}
            stroke={HOVER_COLOR}
            strokeOpacity="0.55"
            strokeWidth="1.25"
            strokeDasharray="2 3"
          />
        )}

        {lines.map((line) => (
          <g key={line.key}>
            <path d={areaFor(line.key)} fill={`url(#${uid}-${line.key})`} />
            <path
              d={pathFor(line.key)}
              fill="none"
              stroke={line.color}
              strokeWidth="2.1"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </g>
        ))}

        {labelIdx.map((i) => (
          <text
            key={`${series[i].day}-${i}`}
            x={xAt(i)}
            y={H - 8}
            textAnchor="middle"
            className="fill-slate"
            style={{ fontSize: 9, fontFamily: "IBM Plex Mono, monospace" }}
          >
            {series[i].label}
          </text>
        ))}

        {series.map((d, i) => (
          <rect
            key={`${d.day}-${i}`}
            x={xAt(i) - colW / 2}
            y={pad.t}
            width={colW}
            height={innerH}
            fill="transparent"
            className="cursor-pointer"
            onClick={() => onSelect(d.day)}
            onMouseEnter={() => setHoverIdx(i)}
            onMouseLeave={() => setHoverIdx(null)}
          >
            <title>
              {d.label}
              {lines
                .map((l) => ` · ${l.name} ${Number(d[l.key]).toFixed(1)}`)
                .join("")}
            </title>
          </rect>
        ))}

        {hoverIdx != null &&
          hoverData &&
          lines.map((line) => (
            <circle
              key={`h-${line.key}`}
              cx={xAt(hoverIdx)}
              cy={yAt(hoverData[line.key])}
              r="4"
              fill={line.color}
              stroke={HOVER_COLOR}
              strokeWidth="1.5"
            />
          ))}

        {selectedIdx >= 0 &&
          lines.map((line) => (
            <circle
              key={`s-${line.key}`}
              cx={xAt(selectedIdx)}
              cy={yAt(series[selectedIdx][line.key])}
              r="4"
              fill={line.color}
              stroke="currentColor"
              className="text-panel"
              strokeWidth="2"
            />
          ))}
      </svg>
    </div>
  );
}

export default function TrendsPage() {
  const [series, setSeries] = useState(KENYA_TRENDS);
  const [usingSample, setUsingSample] = useState(true);
  const [selectedDay, setSelectedDay] = useState(
    KENYA_TRENDS[KENYA_TRENDS.length - 1].day
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const snaps = await dashboardRisks({ limit: 100 });
        if (cancelled) return;
        const live = buildTrendsFromSnapshots(snaps);
        if (live.length > 0) {
          setSeries(live);
          setUsingSample(false);
          setSelectedDay(live[live.length - 1].day);
        } else {
          setSeries(KENYA_TRENDS);
          setUsingSample(true);
          setSelectedDay(KENYA_TRENDS[KENYA_TRENDS.length - 1].day);
        }
      } catch {
        if (cancelled) return;
        setSeries(KENYA_TRENDS);
        setUsingSample(true);
        setSelectedDay(KENYA_TRENDS[KENYA_TRENDS.length - 1].day);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const selected = useMemo(
    () => series.find((d) => d.day === selectedDay) ?? series.at(-1),
    [selectedDay, series]
  );

  const first = series[0];
  const last = series[series.length - 1];
  const rainValues = series.map((d) => Number(d.rainfall) || 0);
  const maxRainRaw = Math.max(1, ...rainValues);
  const maxRain = Math.ceil(maxRainRaw / 5) * 5 || 5;

  const crossedMedium = series.find((d) => d.floodScore >= 40);
  const crossedHigh = series.find((d) => d.floodScore >= 70);
  const floodDelta = (last?.floodScore || 0) - (first?.floodScore || 0);
  const rainDelta = (last?.rainfall || 0) - (first?.rainfall || 0);
  const quakeDelta = (last?.quakeScore || 0) - (first?.quakeScore || 0);
  const avgFlood =
    series.reduce((s, d) => s + d.floodScore, 0) / Math.max(1, series.length);
  const daysHigh = series.filter((d) => d.floodScore >= 70).length;
  const windowLabel = usingSample
    ? "30 DAYS"
    : `${series.length} SNAPSHOT${series.length === 1 ? "" : "S"}`;

  const moments = [
    crossedMedium && {
      day: crossedMedium.label,
      t: "Flood crossed MEDIUM",
      d: `Score ${Math.round(crossedMedium.floodScore)} with rainfall at ${crossedMedium.rainfall} mm.`,
    },
    crossedHigh && {
      day: crossedHigh.label,
      t: "Flood crossed HIGH",
      d: `Engine at ${Math.round(crossedHigh.floodScore)}. Quake stayed on its own axis.`,
    },
    last && {
      day: last.label,
      t: usingSample ? "Today — still two axes" : "Latest snapshot",
      d: `Flood ${Math.round(last.floodScore)} · Quake ${Math.round(last.quakeScore)}. Never blended.`,
    },
  ].filter(Boolean);

  return (
    <div className="mx-auto max-w-6xl px-5 sm:px-8 py-10 pb-16">
      {usingSample && (
        <p className="mb-5 rounded-md border border-amber/40 bg-amber/10 px-3 py-2 text-sm text-amber">
          {SAMPLE_BANNER}
        </p>
      )}

      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl">
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            PUBLIC · TRENDS · KENYA · {windowLabel}
          </p>
          <h1 className="mt-3 font-display text-3xl sm:text-4xl font-bold leading-tight">
            Two hazards. Two timelines. Never one blended line.
          </h1>
          <p className="mt-3 text-base text-slate leading-relaxed">
            Flood climbs with rainfall over the window. Earthquake stays on its
            own axis. Click any day on either chart to inspect it — scores are
            never averaged.
          </p>
        </div>
        <Link
          to="/map"
          className="inline-flex items-center gap-1.5 rounded-md border border-line px-4 py-2 text-sm font-semibold hover:border-amber/40 transition-colors"
        >
          Open risk map <ArrowRight size={14} />
        </Link>
      </div>

      <section className="mt-8 rounded-xl border border-line bg-panel/50 p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div>
            <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
              SELECTED DAY
            </p>
            <h2 className="mt-0.5 font-display text-xl font-bold">
              {selected?.label}
            </h2>
          </div>
          <p className="inline-flex items-center gap-1.5 text-xs text-slate">
            <Split size={13} className="text-amber" />
            Scores never averaged
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 lg:gap-10">
          <ScoreRing
            score={selected?.floodScore || 0}
            label="FLOOD SCORE"
            color="#1d4ed8"
            Icon={Waves}
          />
          <ScoreRing
            score={selected?.quakeScore || 0}
            label="EARTHQUAKE SCORE"
            color="#e11d48"
            Icon={Mountain}
          />
        </div>

        <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-line pt-5">
          <div>
            <p className="font-mono text-[10px] text-slate">RAINFALL</p>
            <p className="mt-1 font-display text-lg font-bold tabular-nums">
              {selected?.rainfall ?? 0}
              <span className="text-sm text-slate font-sans ml-1">mm</span>
            </p>
          </div>
          <div>
            <p className="font-mono text-[10px] text-slate">FLOOD Δ</p>
            <p className="mt-1 font-display text-lg font-bold tabular-nums text-amber inline-flex items-center gap-1">
              <TrendingUp size={14} /> {floodDelta >= 0 ? "+" : ""}
              {floodDelta.toFixed(0)}
            </p>
          </div>
          <div>
            <p className="font-mono text-[10px] text-slate">RAIN Δ</p>
            <p className="mt-1 font-display text-lg font-bold tabular-nums text-teal">
              {rainDelta >= 0 ? "+" : ""}
              {rainDelta.toFixed(1)} mm
            </p>
          </div>
          <div>
            <p className="font-mono text-[10px] text-slate">QUAKE Δ</p>
            <p className="mt-1 font-display text-lg font-bold tabular-nums text-crimson">
              {quakeDelta >= 0 ? "+" : ""}
              {quakeDelta.toFixed(1)}
            </p>
          </div>
        </div>
      </section>

      <section className="mt-5 grid lg:grid-cols-2 gap-5">
        <div className="rounded-xl border border-line bg-panel/50 p-4 sm:p-5">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <p className="font-mono text-[10px] tracking-[0.14em] text-mist">
              HAZARD SCORES · 0–100
            </p>
            <div className="flex gap-3 font-mono text-[9px] text-slate">
              <span className="inline-flex items-center gap-1.5">
                <span
                  className="h-0.5 w-3 rounded-full"
                  style={{ background: "#1d4ed8" }}
                />
                FLOOD
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span
                  className="h-0.5 w-3 rounded-full"
                  style={{ background: "#e11d48" }}
                />
                QUAKE
              </span>
            </div>
          </div>
          <ChartFrame
            series={series}
            yMax={100}
            yTicks={[0, 50, 100]}
            selectedDay={selectedDay}
            onSelect={setSelectedDay}
            showThresholds
            height={210}
            lines={[
              { key: "floodScore", name: "Flood", color: "#1d4ed8" },
              { key: "quakeScore", name: "Quake", color: "#e11d48" },
            ]}
          />
        </div>

        <div className="rounded-xl border border-line bg-panel/50 p-4 sm:p-5">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <p className="font-mono text-[10px] tracking-[0.14em] text-mist inline-flex items-center gap-1.5">
              <Droplets size={12} className="text-teal" />
              RAINFALL · MM
            </p>
            <span className="font-mono text-[9px] text-slate">
              Peak {Math.max(...rainValues).toFixed(1)} mm
            </span>
          </div>
          <ChartFrame
            series={series}
            yMax={maxRain}
            yTicks={[0, maxRain / 2, maxRain].map((v) => Number(v.toFixed(0)))}
            selectedDay={selectedDay}
            onSelect={setSelectedDay}
            height={210}
            lines={[{ key: "rainfall", name: "Rain", color: "#0d9488" }]}
          />
        </div>
      </section>

      <section className="mt-8 grid lg:grid-cols-[1fr_1.1fr] gap-5">
        <div className="rounded-xl border border-line bg-panel/40 p-5 sm:p-6">
          <p className="font-mono text-[10px] tracking-[0.14em] text-amber inline-flex items-center gap-1.5">
            <Activity size={12} />
            WINDOW READOUT
          </p>
          <h2 className="mt-2 font-display text-xl font-bold">
            What the window shows
          </h2>
          <ul className="mt-4 space-y-3 text-sm text-slate leading-relaxed">
            <li>
              — Average flood score across the window:{" "}
              <span className="text-bone font-medium">
                {avgFlood.toFixed(0)}
              </span>
            </li>
            <li>
              — Days at HIGH flood (≥70):{" "}
              <span className="text-bone font-medium">{daysHigh}</span> of{" "}
              {series.length}
            </li>
            <li>
              — Earthquake stays on its own axis — proof the engines do not
              dilute each other.
            </li>
            <li>
              — Rainfall change of{" "}
              <span className="text-bone font-medium">
                {rainDelta >= 0 ? "+" : ""}
                {rainDelta.toFixed(1)} mm
              </span>{" "}
              tracks the flood climb, not the quake line.
            </li>
          </ul>
          <p className="mt-5 text-xs text-muted leading-relaxed">
            {usingSample
              ? "Series is a Kenya sample for the MVP demo. Live flood scoring for today's inputs is on the risk map panel."
              : "Series built from Mongo risk_snapshots via GET /dashboard/risks."}
          </p>
        </div>

        <div className="rounded-xl border border-line bg-panel/40 p-5 sm:p-6">
          <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
            WHAT CHANGED
          </p>
          <h2 className="mt-2 font-display text-xl font-bold">
            Threshold moments
          </h2>
          <div className="mt-5 space-y-4">
            {moments.map((m, i) => (
              <div
                key={m.t}
                className="flex gap-4 border-l-2 border-line pl-4 hover:border-amber/50 transition-colors"
              >
                <div>
                  <p className="font-mono text-[10px] text-slate">
                    {String(i + 1).padStart(2, "0")} · {m.day}
                  </p>
                  <h3 className="mt-1 font-display text-base font-bold">
                    {m.t}
                  </h3>
                  <p className="mt-1 text-sm text-slate leading-relaxed">{m.d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
