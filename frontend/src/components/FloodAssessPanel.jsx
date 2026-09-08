import { useState } from "react";
import { Waves, Loader2 } from "lucide-react";
import { assessFloodRisk, pipelineFlood, ApiError } from "../lib/api.js";
import TextField from "./ui/TextField.jsx";
import RiskBadge from "./ui/RiskBadge.jsx";
import { useAuth } from "../lib/auth.jsx";

function rainfallPayload(zoneId, rain1h, rain24h, prev24h, dataAge) {
  return {
    zone_id: zoneId.trim() || "KE",
    rainfall_1h_mm: Number(rain1h),
    rainfall_24h_mm: Number(rain24h),
    previous_rainfall_24h_mm: prev24h === "" ? null : Number(prev24h),
    data_age_minutes: Number(dataAge) || 0,
  };
}

export default function FloodAssessPanel({
  defaultZoneId,
  allowPipeline = false,
}) {
  const { session } = useAuth();
  const [zoneId, setZoneId] = useState(
    defaultZoneId || session?.zone_id || session?.countryCode || "KE"
  );
  const [rain1h, setRain1h] = useState("12");
  const [rain24h, setRain24h] = useState("62");
  const [prev24h, setPrev24h] = useState("40");
  const [dataAge, setDataAge] = useState("15");
  const [loading, setLoading] = useState(false);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [pipelineResult, setPipelineResult] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const data = await assessFloodRisk(
        rainfallPayload(zoneId, rain1h, rain24h, prev24h, dataAge)
      );
      setResult(data);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not score flood risk. Check that the API is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function onPipeline() {
    setError("");
    setPipelineResult(null);
    setPipelineLoading(true);
    try {
      const data = await pipelineFlood(
        rainfallPayload(zoneId, rain1h, rain24h, prev24h, dataAge)
      );
      setPipelineResult(data);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Pipeline failed. Check that the API is running."
      );
    } finally {
      setPipelineLoading(false);
    }
  }

  const riskLevel =
    pipelineResult?.risk?.risk_level || pipelineResult?.risk_level;
  const currentAction =
    pipelineResult?.decision?.current_action ||
    pipelineResult?.ai_alert?.final_decision?.current_action;

  return (
    <section className="rounded-xl border border-line bg-panel p-6 shadow-sm">
      <div className="flex items-center justify-between gap-3 border-b border-line pb-4">
        <div>
          <p className="font-mono text-[10px] tracking-[0.16em] text-amber">
            LIVE FLOOD RISK ENGINE
          </p>
          <h2 className="mt-1 font-display text-lg font-bold text-bone flex items-center gap-2">
            <Waves size={18} className="text-amber" />
            Assess flood risk
          </h2>
        </div>
      </div>
      <p className="mt-3 text-xs text-slate leading-relaxed">
        Rule-based flood engine only — never blended with earthquake. Send
        rainfall for a zone to assess risk level, score, confidence, and reasons.
        {allowPipeline
          ? " Operations can also run the full alert pipeline for active notifications."
          : ""}
      </p>

      <form className="mt-5 space-y-4" onSubmit={onSubmit}>
        <TextField
          label="Zone ID"
          value={zoneId}
          onChange={(e) => setZoneId(e.target.value)}
          placeholder="KE"
          required
        />
        <TextField
          label="Rainfall last 1 hour (mm)"
          type="number"
          min="0"
          step="0.1"
          value={rain1h}
          onChange={(e) => setRain1h(e.target.value)}
          required
        />
        <TextField
          label="Rainfall last 24 hours (mm)"
          type="number"
          min="0"
          step="0.1"
          value={rain24h}
          onChange={(e) => setRain24h(e.target.value)}
          required
        />
        <TextField
          label="Previous 24h rainfall (mm, optional)"
          type="number"
          min="0"
          step="0.1"
          value={prev24h}
          onChange={(e) => setPrev24h(e.target.value)}
        />
        <TextField
          label="Data age (minutes)"
          type="number"
          min="0"
          value={dataAge}
          onChange={(e) => setDataAge(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading || pipelineLoading}
          className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-amber py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright disabled:opacity-60 transition-colors"
        >
          {loading && <Loader2 size={16} className="animate-spin" />}
          {loading ? "Scoring…" : "Run flood engine"}
        </button>
        {allowPipeline && (
          <button
            type="button"
            disabled={loading || pipelineLoading}
            onClick={onPipeline}
            className="w-full inline-flex items-center justify-center gap-2 rounded-md border border-amber/40 py-2.5 text-sm font-semibold text-amber hover:bg-amber/10 disabled:opacity-60 transition-colors"
          >
            {pipelineLoading && <Loader2 size={16} className="animate-spin" />}
            {pipelineLoading
              ? "Running pipeline…"
              : "Run full alert pipeline"}
          </button>
        )}
      </form>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-5 rounded-lg border border-line bg-raised/60 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-slate">SCORE</span>
            <span className="font-display text-2xl font-bold text-bone">
              {result.risk_score}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-slate">LEVEL</span>
            <RiskBadge level={result.risk_level} />
          </div>
          {result.confidence != null && (
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-slate">CONFIDENCE</span>
              <span className="font-mono text-sm">
                {(Number(result.confidence) * 100).toFixed(0)}%
              </span>
            </div>
          )}
          <ul className="space-y-1.5 pt-2 border-t border-line">
            {(result.reasons || []).map((reason) => (
              <li key={reason} className="text-xs text-slate leading-relaxed">
                — {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {allowPipeline && pipelineResult && (
        <div className="mt-5 rounded-lg border border-amber/30 bg-amber/5 p-4 space-y-4">
          <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
            ALERT PIPELINE RESULT
          </p>

          {riskLevel && (
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-slate">RISK LEVEL</span>
              <RiskBadge level={riskLevel} />
            </div>
          )}

          {pipelineResult?.risk?.risk_score != null && (
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-slate">SCORE</span>
              <span className="font-display text-xl font-bold text-bone">
                {pipelineResult.risk.risk_score}
              </span>
            </div>
          )}

          {currentAction && (
            <div>
              <span className="font-mono text-xs text-slate">
                RECOMMENDED ACTION
              </span>
              <p className="mt-1 text-sm text-bone leading-relaxed">
                {currentAction}
              </p>
            </div>
          )}
        </div>
      )}
    </section>
  );
}