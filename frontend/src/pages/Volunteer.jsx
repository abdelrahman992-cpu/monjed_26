import { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Phone, MapPin, Mail } from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import { ApiError } from "../lib/api.js";
import { useNavLoad } from "../components/PageLoader.jsx";
import TextField from "../components/ui/TextField.jsx";
import PasswordField from "../components/ui/PasswordField.jsx";
import { ZONES } from "../data/zones.js";

const SKILLS = [
  "First aid",
  "Driving",
  "Boat / water rescue",
  "Translation",
  "Logistics",
  "Shelter setup",
];

const VEHICLES = [
  { value: "none", label: "No vehicle" },
  { value: "motorcycle", label: "Motorcycle" },
  { value: "car", label: "Car" },
  { value: "van", label: "Van / pickup" },
  { value: "boat", label: "Boat" },
];

export default function VolunteerAuthPage() {
  const {
    isVolunteer,
    isAdmin,
    signupVolunteer,
    loginAsVolunteer,
    loginAsAdmin,
  } = useAuth();
  const { go } = useNavLoad();
  const location = useLocation();
  const redirected = useRef(false);
  const [mode, setMode] = useState(
    location.state?.mode === "staff" ? "staff" : "login"
  );
  const [error, setError] = useState("");
  const [skills, setSkills] = useState(["Driving"]);
  const [vehicle, setVehicle] = useState("car");
  const [zoneId, setZoneId] = useState("KE");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (redirected.current) return;
    if (isVolunteer) {
      redirected.current = true;
      go("/volunteer/dashboard", { replace: true, label: "Opening dashboard…" });
    } else if (isAdmin) {
      redirected.current = true;
      go("/admin", { replace: true, label: "Opening operations…" });
    }
  }, [isVolunteer, isAdmin, go]);

  async function onLogin(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const data = new FormData(e.target);
    const identifier = String(data.get("identifier") || "").trim();
    const password = String(data.get("password") || "");
    try {
      if (mode === "staff") {
        await loginAsAdmin(identifier, password);
        go("/admin", { label: "Opening operations…" });
        return;
      }
      await loginAsVolunteer(identifier, password);
      go(location.state?.from || "/volunteer/dashboard", {
        label: "Opening dashboard…",
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err.message || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function onSignup(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const data = new FormData(e.target);
    const zone = ZONES.find((z) => z.code === zoneId);
    try {
      await signupVolunteer({
        name: String(data.get("name") || "").trim(),
        email: String(data.get("email") || "").trim(),
        phone: String(data.get("phone") || "").trim(),
        password: String(data.get("password") || ""),
        country: zone?.name || zoneId,
        zone_id: zoneId,
        zone: String(data.get("zone") || "").trim(),
        vehicleType: vehicle,
        capacity: Number(data.get("capacity") || 0),
        skills,
      });
      go("/volunteer/dashboard", { label: "Opening dashboard…" });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err.message || "Signup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-5 sm:px-8 py-12">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        {mode === "staff" ? "OPERATIONS ACCESS" : "VOLUNTEER ACCESS"}
      </p>
      <h1 className="mt-3 font-display text-3xl font-bold">
        {mode === "signup"
          ? "Become a volunteer"
          : mode === "staff"
            ? "Staff log in"
            : "Log in"}
      </h1>
      <p className="mt-3 text-sm text-slate leading-relaxed">
        {mode === "signup"
          ? "Create a volunteer account on the MONJED API. Matching happens on your private dashboard."
          : mode === "staff"
            ? "Sign in with an admin account email or phone and password."
            : "Log in with the email or phone you registered as a volunteer."}
      </p>
      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {mode === "signup" ? (
        <>
          <form className="mt-6 space-y-4" onSubmit={onSignup}>
            <TextField name="name" label="Full name" required minLength={2} />
            <TextField
              name="email"
              label="Email"
              icon={Mail}
              type="email"
              required
              placeholder="you@example.com"
            />
            <TextField
              name="phone"
              label="Phone"
              icon={Phone}
              type="tel"
              required
              placeholder="+2547XXXXXXXX"
            />
            <label className="block">
              <span className="block text-xs font-mono text-slate mb-1.5">
                Country / zone
              </span>
              <select
                value={zoneId}
                onChange={(e) => setZoneId(e.target.value)}
                className="w-full rounded-md border border-line bg-panel py-2.5 px-3 text-sm"
              >
                {ZONES.map((z) => (
                  <option key={z.code} value={z.code}>
                    {z.name}
                  </option>
                ))}
              </select>
            </label>
            <TextField name="zone" label="Town / area" icon={MapPin} />
            <label className="block">
              <span className="block text-xs font-mono text-slate mb-1.5">
                Vehicle
              </span>
              <select
                value={vehicle}
                onChange={(e) => setVehicle(e.target.value)}
                className="w-full rounded-md border border-line bg-panel py-2.5 px-3 text-sm"
              >
                {VEHICLES.map((v) => (
                  <option key={v.value} value={v.value}>
                    {v.label}
                  </option>
                ))}
              </select>
            </label>
            {vehicle !== "none" && (
              <TextField
                name="capacity"
                label="Capacity"
                type="number"
                min="1"
                defaultValue="3"
              />
            )}
            <div className="flex flex-wrap gap-2">
              {SKILLS.map((s) => {
                const on = skills.includes(s);
                return (
                  <button
                    key={s}
                    type="button"
                    onClick={() =>
                      setSkills((p) =>
                        on ? p.filter((x) => x !== s) : [...p, s]
                      )
                    }
                    className={`rounded-md border px-2.5 py-1 text-xs ${
                      on ? "border-amber/60 bg-amber/10" : "border-line text-slate"
                    }`}
                  >
                    {s}
                  </button>
                );
              })}
            </div>
            <PasswordField
              name="password"
              label="Password"
              required
              minLength={8}
              placeholder="At least 8 characters"
            />
            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-md bg-amber py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
            >
              {busy ? "Creating…" : "Create volunteer account"}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-slate">
            Already registered?{" "}
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError("");
              }}
              className="text-amber hover:underline font-medium"
            >
              Log in
            </button>
          </p>
        </>
      ) : (
        <>
          <form className="mt-6 space-y-4" onSubmit={onLogin}>
            <TextField
              name="identifier"
              label="Email or phone"
              icon={Mail}
              required
              minLength={3}
              placeholder="you@example.com or +2547…"
            />
            <PasswordField name="password" label="Password" required minLength={1} />
            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-md bg-amber py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright disabled:opacity-60"
            >
              {busy ? "Signing in…" : "Log in"}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-slate space-x-1">
            {mode === "staff" ? (
              <button
                type="button"
                onClick={() => {
                  setMode("login");
                  setError("");
                }}
                className="text-amber hover:underline font-medium"
              >
                Volunteer login
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => {
                    setMode("signup");
                    setError("");
                  }}
                  className="text-amber hover:underline font-medium"
                >
                  Register as a volunteer
                </button>
                <span>·</span>
                <button
                  type="button"
                  onClick={() => {
                    setMode("staff");
                    setError("");
                  }}
                  className="text-amber hover:underline font-medium"
                >
                  Staff login
                </button>
              </>
            )}
          </p>
        </>
      )}
    </div>
  );
}
