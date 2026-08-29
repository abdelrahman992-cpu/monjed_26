import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  Waves,
  Mountain,
  MapPin,
  ChevronDown,
  Loader2,
  RefreshCw,
} from "lucide-react";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import FloodAssessPanel from "../components/FloodAssessPanel.jsx";
import RiskMap, { riskColor } from "../components/RiskMap.jsx";
import { ZONES, mapLevel } from "../data/zones.js";
import {
  assessFloodRisk,
  assessEarthquakeRisk,
  ApiError,
} from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";

function emptyCountry(zone) {
  return {
    ...zone,
    flood: "low",
    quake: "low",
    floodScore: 0,
    quakeScore: 0,
    floodReasons: ["Waiting for API…"],
    quakeReasons: ["Waiting for API…"],
    updated: null,
    source: "pending",
  };
}

async function assessZone(zone) {
  const floodObs = zone.floodObs || {
    rainfall_1h_mm: 5,
    rainfall_24h_mm: 20,
    previous_rainfall_24h_mm: 15,
  };
  const quakeObs = zone.quakeObs || {
    magnitude: 3,
    depth_km: 20,
    distance_km: 150,
  };

  const [flood, quake] = await Promise.all([
    assessFloodRisk({
      zone_id: zone.zone_id || zone.code,
      rainfall_1h_mm: floodObs.rainfall_1h_mm,
      rainfall_24h_mm: floodObs.rainfall_24h_mm,
      previous_rainfall_24h_mm: floodObs.previous_rainfall_24h_mm ?? null,
      data_age_minutes: 30,
    }),
    assessEarthquakeRisk({
      zone_id: zone.zone_id || zone.code,
      magnitude: quakeObs.magnitude,
      depth_km: quakeObs.depth_km,
      distance_km: quakeObs.distance_km,
      data_age_minutes: 60,
      source_verified: true,
    }),
  ]);

  return {
    ...zone,
    flood: mapLevel(flood.risk_level),
    quake: mapLevel(quake.risk_level),
    floodScore: flood.risk_score,
    quakeScore: quake.risk_score,
    floodReasons: flood.reasons?.length
      ? flood.reasons
      : [`Engine level: ${flood.risk_level}`],
    quakeReasons: quake.reasons?.length
      ? quake.reasons
      : [`Engine level: ${quake.risk_level}`],
    floodApiLevel: flood.risk_level,
    quakeApiLevel: quake.risk_level,
    updated: flood.evaluated_at || quake.evaluated_at || new Date().toISOString(),
    source: "api",
  };
}

function countryForSession(session, countries) {
  if (!countries.length) return emptyCountry(ZONES[0]);
  const byCode = session?.countryCode
    ? countries.find((c) => c.code === session.countryCode)
    : null;
  if (byCode) return byCode;
  const byName = session?.country
    ? countries.find(
        (c) => c.name.toLowerCase() === String(session.country).toLowerCase()
      )
    : null;
  return byName || countries[0];
}

export default function MapPage() {
  const { session } = useAuth();
  const [countries, setCountries] = useState(() => ZONES.map(emptyCountry));
  const [loadState, setLoadState] = useState("loading");
  const [loadError, setLoadError] = useState("");
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("All");
  const [selected, setSelected] = useState(() => emptyCountry(ZONES[0]));
  const [metric, setMetric] = useState("flood");
  const [listOpen, setListOpen] = useState(false);
  const [focusedHome, setFocusedHome] = useState(true);

  const loadMapRisk = useCallback(async () => {
    setLoadState("loading");
    setLoadError("");
    try {
      const results = await Promise.all(
        ZONES.map(async (zone) => {
          try {
            return await assessZone(zone);
          } catch (err) {
            return {
              ...emptyCountry(zone),
              floodReasons: [
                err instanceof ApiError
                  ? err.message
                  : "Flood API unavailable for this zone",
              ],
              quakeReasons: ["Earthquake API unavailable for this zone"],
              source: "error",
              updated: new Date().toISOString(),
            };
          }
        })
      );
      setCountries(results);
      setLoadState(
        results.every((r) => r.source === "error") ? "error" : "ok"
      );
      if (results.every((r) => r.source === "error")) {
        setLoadError(
          results[0]?.floodReasons?.[0] ||
            "Could not load risk from POST /risk/flood and /risk/earthquake."
        );
      }
    } catch (err) {
      setLoadState("error");
      setLoadError(
        err instanceof ApiError
          ? err.message
          : "Could not reach the risk API."
      );
    }
  }, []);

  useEffect(() => {
    loadMapRisk();
  }, [loadMapRisk]);

  const homeCountry = useMemo(
    () => countryForSession(session, countries),
    [session, countries]
  );

  useEffect(() => {
    setSelected(homeCountry);
    setFocusedHome(true);
  }, [homeCountry]);

  function selectCountry(c) {
    setSelected(c);
    setFocusedHome(c.code === homeCountry.code);
  }

  const regions = useMemo(
    () => ["All", ...Array.from(new Set(ZONES.map((c) => c.region)))],
    []
  );

  const filtered = countries.filter((c) => {
    const q = query.toLowerCase();
    const matchesQ =
      !q ||
      c.name.toLowerCase().includes(q) ||
      c.code.toLowerCase().includes(q);
    const matchesR = region === "All" || c.region === region;
    return matchesQ && matchesR;
  });

  const highCount = countries.filter((c) => {
    const level = c[metric];
    return level === "high" || level === "critical";
  }).length;

  return (
    <div className="mx-auto max-w-7xl px-5 sm:px-8 py-10">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        YOUR AREA · LIVE MAP · POST /risk/flood · /risk/earthquake
      </p>
      <h1 className="mt-3 font-display text-3xl font-bold">
        Risk around {homeCountry.name}
      </h1>
      <p className="mt-2 max-w-2xl text-sm text-slate leading-relaxed">
        Country colors come from the MONJED risk engine for each zone. Flood and
        earthquake stay separate.
      </p>
      {focusedHome && (
        <p className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-teal/30 bg-teal/10 px-3 py-1.5 font-mono text-[10px] text-teal tracking-wide">
          <MapPin size={11} /> SHOWING YOUR LOCATION FIRST
        </p>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] ${
            loadState === "ok"
              ? "border-teal/40 text-teal"
              : loadState === "error"
                ? "border-crimson/40 text-crimson"
                : "border-line text-slate"
          }`}
        >
          {loadState === "loading" ? (
            <Loader2 size={11} className="animate-spin" />
          ) : null}
          {loadState === "ok"
            ? `API LIVE · ${highCount} high ${metric}`
            : loadState === "error"
              ? "API ERROR"
              : "SCORING ZONES…"}
        </span>
        <button
          type="button"
          onClick={loadMapRisk}
          disabled={loadState === "loading"}
          className="inline-flex items-center gap-1.5 rounded-full border border-line px-2.5 py-1 font-mono text-[10px] text-slate hover:text-bone disabled:opacity-50"
        >
          <RefreshCw size={11} /> Refresh from API
        </button>
      </div>
      {loadError && (
        <p className="mt-3 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {loadError}
        </p>
      )}

      <div className="mt-8 grid lg:grid-cols-[1.4fr_1fr] gap-8">
        <div className="space-y-4">
          <div className="rounded-xl border border-line bg-panel/50 p-4 sm:p-5">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
              <p className="font-mono text-[10px] tracking-[0.16em] text-mist inline-flex items-center gap-1.5">
                <MapPin size={12} />
                {metric === "flood" ? "FLOOD RISK" : "EARTHQUAKE RISK"} · MAP
              </p>
              <div className="flex gap-1.5">
                {[
                  { key: "flood", label: "Flood", Icon: Waves },
                  { key: "quake", label: "Quake", Icon: Mountain },
                ].map(({ key, label, Icon }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setMetric(key)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded-lg border ${
                      metric === key
                        ? "bg-amber text-ink border-amber font-bold"
                        : "bg-panel text-slate border-line"
                    }`}
                  >
                    <Icon size={13} />
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <RiskMap
              countries={countries}
              selected={selected}
              onSelect={selectCountry}
              metric={metric}
            />

            <div className="mt-3 flex flex-wrap items-center gap-4 font-mono text-[10px] text-slate">
              {[
                { level: "high", label: "High" },
                { level: "medium", label: "Medium" },
                { level: "low", label: "Low" },
              ].map((l) => (
                <span key={l.level} className="inline-flex items-center gap-1.5">
                  <span
                    className="h-2.5 w-2.5 rounded-full inline-block"
                    style={{ background: riskColor(l.level) }}
                  />
                  {l.label}
                </span>
              ))}
              <button
                type="button"
                onClick={() => selectCountry(homeCountry)}
                className="ml-auto text-amber hover:underline"
              >
                Back to {homeCountry.name}
              </button>
            </div>
          </div>

          <div className="rounded-xl border border-line bg-panel/40 overflow-hidden">
            <button
              type="button"
              onClick={() => setListOpen((v) => !v)}
              className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-raised/40 transition-colors"
              aria-expanded={listOpen}
            >
              <div>
                <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
                  EXPLORE OTHER AREAS
                </p>
                <p className="mt-0.5 text-sm text-mist">
                  {selected.name} selected · {countries.length} zones from API
                </p>
              </div>
              <ChevronDown
                size={18}
                className={`text-slate shrink-0 transition-transform ${
                  listOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {listOpen && (
              <div className="border-t border-line px-3 pb-3 pt-2 space-y-2">
                <div className="flex flex-col sm:flex-row gap-2">
                  <div className="relative flex-1">
                    <Search
                      size={14}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate"
                    />
                    <input
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Filter by name or code…"
                      className="w-full bg-panel border border-line rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-amber"
                    />
                  </div>
                  <select
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    className="rounded-md border border-line bg-panel px-3 py-2 text-sm text-bone focus:outline-none focus:border-amber"
                  >
                    {regions.map((r) => (
                      <option key={r} value={r}>
                        {r === "All" ? "All regions" : r}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="max-h-56 overflow-y-auto rounded-md border border-line divide-y divide-line">
                  {filtered.length === 0 ? (
                    <p className="px-3 py-4 text-sm text-slate text-center">
                      No countries match that filter.
                    </p>
                  ) : (
                    filtered.map((c) => {
                      const on = selected.code === c.code;
                      return (
                        <button
                          key={c.code}
                          type="button"
                          onClick={() => selectCountry(c)}
                          className={`w-full flex items-center gap-3 px-3 py-2.5 text-left text-sm transition-colors ${
                            on
                              ? "bg-amber/10"
                              : "bg-panel/30 hover:bg-raised/50"
                          }`}
                        >
                          <span className="font-mono text-[10px] text-slate w-7 shrink-0">
                            {c.code}
                          </span>
                          <span className="flex-1 font-medium truncate">
                            {c.name}
                            {c.code === homeCountry.code ? (
                              <span className="ml-2 font-mono text-[9px] text-teal">
                                YOUR AREA
                              </span>
                            ) : null}
                          </span>
                          <RiskBadge level={c.floodApiLevel || c.flood} />
                          <RiskBadge level={c.quakeApiLevel || c.quake} />
                        </button>
                      );
                    })
                  )}
                </div>
                <p className="px-1 font-mono text-[9px] text-muted tracking-wide">
                  FLOOD · QUAKE · FROM RISK ENGINE
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-line bg-panel/50 p-6">
            <p className="font-mono text-xs text-amber">
              {selected.code} ·{" "}
              {selected.updated
                ? `API ${new Date(selected.updated).toUTCString()}`
                : "LOADING"}
            </p>
            <h2 className="mt-1 font-display text-2xl font-bold">
              {selected.name}
            </h2>
            <div className="mt-6 space-y-5">
              <div>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-xs text-slate">
                    FLOOD · {selected.floodScore}/100
                  </span>
                  <RiskBadge level={selected.floodApiLevel || selected.flood} />
                </div>
                <ul className="mt-2 text-xs text-slate space-y-1">
                  {(selected.floodReasons || []).map((r) => (
                    <li key={r}>— {r}</li>
                  ))}
                </ul>
              </div>
              <div className="border-t border-line pt-4">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-xs text-slate">
                    EARTHQUAKE · {selected.quakeScore}/100
                  </span>
                  <RiskBadge level={selected.quakeApiLevel || selected.quake} />
                </div>
                <ul className="mt-2 text-xs text-slate space-y-1">
                  {(selected.quakeReasons || []).map((r) => (
                    <li key={r}>— {r}</li>
                  ))}
                </ul>
              </div>
            </div>
            <Link
              to="/help"
              className="mt-6 block text-center rounded-lg bg-amber text-ink font-semibold py-2.5 text-sm"
            >
              Request help in {selected.name}
            </Link>
          </div>
          <FloodAssessPanel />
        </div>
      </div>
    </div>
  );
}
