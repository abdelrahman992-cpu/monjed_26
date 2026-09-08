import { useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, Phone, ArrowRight, CheckCircle2 } from "lucide-react";
import { createAssistanceRequest, ApiError, toE164 } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import TextField from "../components/ui/TextField.jsx";

const NEEDS = [
  { id: "other", label: "Need help", api: "other" },
  { id: "transportation", label: "No transport", api: "transportation" },
  { id: "mobility_assistance", label: "Mobility assistance", api: "mobility_assistance" },
];

/** Most specific type wins for volunteer matching when several are selected. */
const NEED_PRIORITY = ["mobility_assistance", "transportation", "other"];

function toggleItem(current, id) {
  if (current.includes(id)) {
    const next = current.filter((x) => x !== id);
    return next.length ? next : current;
  }
  return [...current, id];
}

function primaryRequestType(selectedIds) {
  const apis = selectedIds
    .map((id) => NEEDS.find((n) => n.id === id)?.api)
    .filter(Boolean);
  for (const api of NEED_PRIORITY) {
    if (apis.includes(api)) return api;
  }
  return "other";
}

function selectedNeedLabels(selectedIds) {
  return selectedIds
    .map((id) => NEEDS.find((n) => n.id === id)?.label)
    .filter(Boolean);
}

const ACCESSIBILITY_OPTIONS = [
  { id: "mobility", label: "Mobility", hint: "Wheelchair, walker, or difficulty moving" },
  { id: "visual", label: "Visual", hint: "Blind or low vision" },
  { id: "hearing", label: "Hearing", hint: "Deaf or hard of hearing" },
  { id: "cognitive", label: "Cognitive", hint: "Clear plain-language instructions" },
];

export default function HelpPage() {
  const { session } = useAuth();
  const [needs, setNeeds] = useState(["other"]);
  const [accessibilityNeeds, setAccessibilityNeeds] = useState(
    () => session?.accessibility_needs || []
  );
  const [location, setLocation] = useState(() => {
    if (!session) return "";
    return [session.zone, session.country].filter(Boolean).join(", ");
  });
  const [phone, setPhone] = useState(session?.phone || "");
  const [details, setDetails] = useState("");
  const [people, setPeople] = useState("1");
  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  const [geoBusy, setGeoBusy] = useState(false);
  const [saved, setSaved] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function captureGps() {
    if (!navigator.geolocation) {
      setError("Geolocation is not available in this browser.");
      return;
    }
    setGeoBusy(true);
    setError("");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(Number(pos.coords.latitude.toFixed(6)));
        setLongitude(Number(pos.coords.longitude.toFixed(6)));
        setGeoBusy(false);
      },
      () => {
        setError("Could not read GPS. Allow location access or enter coordinates.");
        setGeoBusy(false);
      },
      { enableHighAccuracy: true, timeout: 12000 }
    );
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const zone_id = session?.zone_id || session?.countryCode || "KE";
    const labels = selectedNeedLabels(needs);
    const needsSummary = labels.join(", ");
    const request_type = primaryRequestType(needs);
    const phoneRaw = phone.trim();
    const requester_phone = toE164(phoneRaw) || (phoneRaw.length >= 7 ? phoneRaw : null);
    if (!requester_phone) {
      setError("Enter a valid phone number with country code (e.g. +2547…).");
      setBusy(false);
      return;
    }
    const detailText = details.trim();
    try {
      const record = await createAssistanceRequest({
        zone_id,
        location: location.trim() || zone_id,
        hazard: "flood",
        request_type,
        priority: "high",
        requester_phone,
        description: detailText
          ? `${needsSummary}. ${detailText}`
          : `${needsSummary}. People: ${people}.`,
        accessibility_needs: accessibilityNeeds,
        ...(latitude != null && longitude != null
          ? { latitude, longitude }
          : {}),
      });
      setSaved(record);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create help request.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-5 sm:px-8 py-10 pb-16">
      <h1 className="font-display text-3xl sm:text-4xl font-bold leading-tight">
        Request help
      </h1>
      <p className="mt-3 text-sm text-slate">
        Signed in as {session?.name}. Request is stored on the MONJED assistance API
        until ops matches a volunteer.
      </p>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {saved ? (
        <div className="mt-8 rounded-xl border border-teal/30 bg-teal/10 p-6 sm:p-8">
          <div className="flex items-center gap-2 text-teal">
            <CheckCircle2 size={20} />
            <p className="font-mono text-[10px] tracking-widest">
              QUEUED · {saved.request_id} · {saved.status}
            </p>
          </div>
          <p className="mt-4 text-sm text-mist">{saved.description}</p>
          <p className="mt-2 text-xs text-slate">{saved.location} · zone {saved.zone_id}</p>
          {saved.latitude != null && saved.longitude != null && (
            <p className="mt-1 font-mono text-[10px] text-slate">
              GPS {saved.latitude}, {saved.longitude}
            </p>
          )}
          {Array.isArray(saved.accessibility_needs) && saved.accessibility_needs.length > 0 && (
            <p className="mt-2 text-xs text-slate font-mono">
              Accessibility: {saved.accessibility_needs.join(", ")}
            </p>
          )}
          <div className="mt-6 flex flex-wrap gap-4">
            <Link to="/map" className="inline-flex items-center gap-1.5 text-sm text-amber hover:underline">
              Back to map <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="mt-8 space-y-5">
          <div>
            <p className="font-mono text-[10px] tracking-[0.14em] text-slate mb-3">
              WHAT DO YOU NEED? · pick one or more
            </p>
            <div className="flex flex-wrap gap-2">
              {NEEDS.map((n) => {
                const on = needs.includes(n.id);
                return (
                  <button
                    key={n.id}
                    type="button"
                    onClick={() => setNeeds((prev) => toggleItem(prev, n.id))}
                    className={`rounded-md border px-3 py-2 text-sm transition-colors ${
                      on ? "border-amber/50 bg-amber/10" : "border-line hover:border-mist/30"
                    }`}
                  >
                    {n.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <p className="font-mono text-[10px] tracking-[0.14em] text-slate mb-1">
              DISABILITIES / ACCESSIBILITY · optional, pick any that apply
            </p>
            <p className="text-xs text-muted mb-3">
              Helps responders prepare the right support. Saved with your request for admin and volunteers.
            </p>
            <div className="grid sm:grid-cols-2 gap-2">
              {ACCESSIBILITY_OPTIONS.map((opt) => {
                const on = accessibilityNeeds.includes(opt.id);
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() =>
                      setAccessibilityNeeds((prev) => toggleItem(prev, opt.id))
                    }
                    className={`rounded-lg border px-3.5 py-3 text-left transition-colors ${
                      on
                        ? "border-teal/50 bg-teal/10"
                        : "border-line bg-panel/40 hover:border-mist/30"
                    }`}
                  >
                    <span className="font-mono text-[11px] tracking-wide">{opt.label}</span>
                    <span className="block text-[11px] text-slate mt-1 leading-snug">
                      {opt.hint}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <TextField
            label="Where are you"
            icon={MapPin}
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            minLength={2}
          />
          <div className="rounded-lg border border-line bg-panel/40 p-3 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <p className="font-mono text-[10px] tracking-[0.14em] text-slate">
                GPS FOR ROBOT DISPATCH
              </p>
              <button
                type="button"
                onClick={captureGps}
                disabled={geoBusy}
                className="rounded-md border border-line px-2.5 py-1 text-[11px] text-mist hover:text-bone disabled:opacity-50"
              >
                {geoBusy ? "Reading…" : "Use my location"}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <label className="block text-xs text-mist">
                Latitude
                <input
                  type="number"
                  step="any"
                  className="mt-1 w-full rounded-md border border-line bg-night px-2 py-1.5 text-sm text-bone"
                  value={latitude ?? ""}
                  onChange={(e) =>
                    setLatitude(
                      e.target.value === "" ? null : Number(e.target.value)
                    )
                  }
                  placeholder="-1.2921"
                />
              </label>
              <label className="block text-xs text-mist">
                Longitude
                <input
                  type="number"
                  step="any"
                  className="mt-1 w-full rounded-md border border-line bg-night px-2 py-1.5 text-sm text-bone"
                  value={longitude ?? ""}
                  onChange={(e) =>
                    setLongitude(
                      e.target.value === "" ? null : Number(e.target.value)
                    )
                  }
                  placeholder="36.8219"
                />
              </label>
            </div>
            <p className="text-[11px] text-slate">
              Optional but recommended — helps ops dispatch response units to your exact location.
            </p>
          </div>
          <TextField
            label="How many people"
            type="number"
            min="1"
            max="50"
            value={people}
            onChange={(e) => setPeople(e.target.value)}
            required
          />
          <TextField
            label="Phone"
            icon={Phone}
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            minLength={7}
          />
          <label className="block">
            <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">Details</span>
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-line bg-panel px-3 py-2 text-sm"
              placeholder="What do you need?"
            />
          </label>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-md bg-amber py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
          >
            {busy ? "Sending…" : "Submit help request"}
          </button>
        </form>
      )}
    </div>
  );
}
