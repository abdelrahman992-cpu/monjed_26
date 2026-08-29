import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Waves,
  Route,
  Siren,
  Car,
  CheckCircle2,
  Loader2,
  MapPin,
  Shield,
  Radio,
  ArrowRight,
} from "lucide-react";
import { analyzeCommunityReport, submitCommunityReport, ApiError } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import TextField from "../components/ui/TextField.jsx";
import RiskBadge from "../components/ui/RiskBadge.jsx";

const TYPES = [
  {
    key: "WATER RISING",
    icon: Waves,
    hint: "Cross-checks the flood engine. Repeated reports in one zone raise confidence.",
  },
  {
    key: "ROAD BLOCKED",
    icon: Route,
    hint: "Feasibility flag — responders annotate verify-route if this clusters under an alert.",
  },
  {
    key: "NEED HELP",
    icon: Siren,
    hint: "Opens an assistance path. Prefer the Request help page if people need a volunteer.",
  },
  {
    key: "NO TRANSPORT",
    icon: Car,
    hint: "Separate from mobility. Matches volunteers who registered a vehicle.",
  },
  {
    key: "I AM SAFE",
    icon: CheckCircle2,
    hint: "Closes the loop for responders. Never used to silently cancel an alert.",
  },
];

function toggleType(current, key) {
  if (current.includes(key)) {
    const next = current.filter((t) => t !== key);
    return next.length ? next : current;
  }
  return [...current, key];
}

export default function ReportPage() {
  const { session } = useAuth();
  const [types, setTypes] = useState(["WATER RISING"]);
  const [location, setLocation] = useState(() => {
    if (!session) return "";
    const bits = [session.zone, session.country].filter(Boolean);
    return bits.join(", ");
  });
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [saved, setSaved] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setAnalysis(null);
    setSaved(null);
    setLoading(true);

    const typeLabel = types.join(", ");
    const report_text = notes.trim()
      ? `${typeLabel}. ${notes.trim()}`
      : `${typeLabel} reported at this location.`;

    const zone_id = session?.zone_id || session?.countryCode || "KE";

    try {
      const record = await submitCommunityReport({
        report_text,
        zone_id,
        location: location.trim() || zone_id,
        reporter_id: session?.id || null,
      });
      setAnalysis(record.analysis || null);
      setSaved(record);
      setNotes("");
      setLocation("");
      setTypes(["WATER RISING"]);
    } catch (err) {
      try {
        const analyzed = await analyzeCommunityReport({
          report_text,
          zone_id,
          location: location.trim() || zone_id,
          reporter_id: session?.id || null,
        });
        setAnalysis(analyzed);
        setError(
          err instanceof ApiError
            ? `${err.message} (showed analyze-only result)`
            : "Submit failed; showed analyze-only result."
        );
      } catch (err2) {
        setError(err2 instanceof ApiError ? err2.message : "Could not reach report API.");
      }
    } finally {
      setLoading(false);
    }
  }

const activeTypes = TYPES.filter((t) => types.includes(t.key));

  return (
    <div className="mx-auto max-w-6xl px-5 sm:px-8 py-10 pb-16">
      <div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-10 lg:gap-14 items-start">
        <div>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            MEMBER · GROUND TRUTH
          </p>
          <h1 className="mt-3 font-display text-3xl sm:text-4xl font-bold leading-tight">
            File a ground report
          </h1>
          <p className="mt-4 text-base text-slate leading-relaxed max-w-xl">
            Typed reports plot immediately and feed the feasibility layer. Free
            text is slow under stress — pick a category, name the place, add
            notes only if you have time.
          </p>

          <form className="mt-8 space-y-6" onSubmit={onSubmit}>
            <div>
              <p className="font-mono text-[10px] tracking-[0.14em] text-slate mb-3">
                REPORT TYPES · pick one or more
              </p>
              <div className="grid sm:grid-cols-2 gap-2">
                {TYPES.map((t) => {
                  const Icon = t.icon;
                  const on = types.includes(t.key);
                  return (
                    <button
                      key={t.key}
                      type="button"
                      onClick={() => setTypes((prev) => toggleType(prev, t.key))}
                      className={`flex items-start gap-3 rounded-lg border px-3.5 py-3 text-left transition-colors ${
                        on
                          ? "border-amber/50 bg-amber/10"
                          : "border-line bg-panel/40 hover:border-mist/30"
                      }`}
                    >
                      <Icon
                        size={17}
                        className={on ? "text-amber mt-0.5 shrink-0" : "text-slate mt-0.5 shrink-0"}
                      />
                      <span>
                        <span className="font-mono text-[11px] tracking-wide">
                          {t.key}
                        </span>
                        <span className="block text-[11px] text-slate mt-1 leading-snug">
                          {t.hint}
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <TextField
              label="Location"
              icon={MapPin}
              placeholder="Zone, road, estate, or landmark"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
              minLength={2}
            />

            <label className="block">
              <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">
                Notes (optional)
              </span>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                placeholder="What you can see. Do not invent details."
                className="w-full rounded-md border border-line bg-panel px-3 py-2.5 text-sm text-bone placeholder:text-muted focus:outline-none focus:border-amber"
              />
            </label>

            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex justify-center items-center gap-2 rounded-md bg-amber px-8 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright disabled:opacity-60 transition-colors"
            >
              {loading && <Loader2 size={16} className="animate-spin" />}
              Submit report
            </button>
          </form>

          {error && (
            <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          {saved && (
            <div className="mt-6 rounded-xl border border-teal/30 bg-teal/10 p-5">
              <p className="font-mono text-[10px] text-teal tracking-widest">
                SAVED · {saved.id}
              </p>
              <button
                type="button"
                onClick={() => {
                  setSaved(null);
                  setAnalysis(null);
                }}
                className="mt-3 text-sm text-amber hover:underline"
              >
                File another report
              </button>
            </div>
          )}

          {analysis && (
            <div className="mt-6 rounded-xl border border-line bg-panel/50 p-5 space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-mono text-xs text-slate inline-flex items-center gap-1.5">
                  <Radio size={12} className="text-amber" />
                  LIVE ANALYZE
                </span>
                <RiskBadge level={analysis.severity} />
              </div>
              <p className="text-sm">
                Hazard:{" "}
                <span className="font-mono text-amber">
                  {analysis.hazard_type}
                </span>
                {" · "}
                Confidence {(analysis.analysis_confidence * 100).toFixed(0)}%
              </p>
              <div className="grid sm:grid-cols-2 gap-2 text-xs text-slate">
                <p>Rising water: {analysis.rising_water ? "yes" : "no"}</p>
                <p>Blocked road: {analysis.blocked_road ? "yes" : "no"}</p>
                <p>Help needed: {analysis.help_needed ? "yes" : "no"}</p>
                <p>
                  Transport needed:{" "}
                  {analysis.transportation_needed ? "yes" : "no"}
                </p>
                <p>
                  Mobility assistance:{" "}
                  {analysis.mobility_assistance_needed ? "yes" : "no"}
                </p>
              </div>
              {(analysis.extracted_evidence || []).length > 0 && (
                <ul className="text-xs text-mist space-y-1 border-t border-line pt-3">
                  {analysis.extracted_evidence.map((e) => (
                    <li key={e}>— {e}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        <aside className="space-y-5 lg:sticky lg:top-24">
          <div className="rounded-xl border border-line bg-panel/50 p-6">
            <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
              SELECTED {types.length > 1 ? "TYPES" : "TYPE"}
            </p>
            <div className="mt-3 space-y-3">
              {activeTypes.map((t) => {
                const Icon = t.icon;
                return (
                  <div key={t.key} className="flex items-start gap-3">
                    <Icon size={20} className="text-amber mt-0.5 shrink-0" strokeWidth={1.75} />
                    <div>
                      <h2 className="font-display text-lg font-bold">{t.key}</h2>
                      <p className="mt-1 text-sm text-slate leading-relaxed">{t.hint}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-5 pt-4 border-t border-line text-sm text-slate">
              <p className="inline-flex items-start gap-2">
                <Shield size={15} className="text-teal mt-0.5 shrink-0" />
                One report = low confidence. Several similar reports in the same
                zone raise priority.
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-line bg-raised/30 p-6">
            <p className="font-mono text-[10px] tracking-[0.14em] text-slate">
              NEED A PERSON, NOT A REPORT?
            </p>
            <p className="mt-2 text-sm text-mist leading-relaxed">
              If someone cannot move or needs a vehicle, queue a help request.
              Volunteers only see it after they sign in.
            </p>
            <Link
              to="/help"
              className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-amber hover:underline"
            >
              Request help <ArrowRight size={14} />
            </Link>
          </div>

          <div className="rounded-xl border border-line bg-panel/40 p-6">
            <p className="font-mono text-[10px] tracking-[0.14em] text-slate">
              CONFIDENCE RULES
            </p>
            <ul className="mt-3 space-y-2 text-sm text-slate leading-relaxed">
              <li>— Typed categories plot faster than paragraphs.</li>
              <li>— Flood and earthquake risk stay on separate engines.</li>
              <li>— Safe check-ins never cancel an active alert alone.</li>
              <li>— Admin triage: New → Verified → Resolved.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}
