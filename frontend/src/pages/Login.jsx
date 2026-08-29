import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Phone, MapPin, UserRound, Mail } from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import { useNavLoad } from "../components/PageLoader.jsx";
import TextField from "../components/ui/TextField.jsx";
import PasswordField from "../components/ui/PasswordField.jsx";
import { ZONES } from "../data/zones.js";
import { ApiError } from "../lib/api.js";

export default function LoginPage() {
  const { isSignedIn, session, loginAsUser, signupUser } = useAuth();
  const { go } = useNavLoad();
  const location = useLocation();
  const redirected = useRef(false);
  const [mode, setMode] = useState("login");
  const [error, setError] = useState("");
  const [countryCode, setCountryCode] = useState("KE");
  const [busy, setBusy] = useState(false);

  const afterLogin = location.state?.from || "/map";

  useEffect(() => {
    if (redirected.current || !isSignedIn) return;
    redirected.current = true;
    if (session?.role === "admin") {
      go("/admin", { replace: true, label: "Opening operations…" });
    } else if (session?.role === "volunteer") {
      go("/volunteer/dashboard", { replace: true, label: "Opening dashboard…" });
    } else {
      go(afterLogin, { replace: true, label: "Opening your map…" });
    }
  }, [isSignedIn, session, go, afterLogin]);

  async function onLogin(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const data = new FormData(e.target);
    try {
      await loginAsUser(
        String(data.get("identifier") || "").trim(),
        String(data.get("password") || "")
      );
      go(afterLogin, { label: "Opening your map…" });
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
    const country = ZONES.find((c) => c.code === countryCode);
    try {
      await signupUser({
        name: String(data.get("name") || "").trim(),
        email: String(data.get("email") || "").trim(),
        phone: String(data.get("phone") || "").trim(),
        password: String(data.get("password") || ""),
        country: country?.name || countryCode,
        countryCode,
        zone: String(data.get("zone") || "").trim(),
        notification_consent: true,
      });
      go(afterLogin, { label: "Opening your map…" });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err.message || "Signup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-5 sm:px-8 py-10 pb-16">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        SIGN IN · ALERTS READY
      </p>
      <h1 className="mt-3 font-display text-3xl font-bold">
        {mode === "login" ? "Log in" : "Create your account"}
      </h1>
      <p className="mt-3 text-sm text-slate leading-relaxed">
        {mode === "login"
          ? "Log in with the email or phone you registered with to open the map, report, and request help."
          : "Register with email and country so we can show risk for your area — and send alerts when you opt in."}
      </p>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {mode === "login" ? (
        <>
          <form onSubmit={onLogin} className="mt-6 space-y-4">
            <TextField
              label="Email or phone"
              name="identifier"
              icon={Mail}
              required
              minLength={3}
              placeholder="you@example.com or +2547…"
            />
            <PasswordField label="Password" name="password" required minLength={8} />
            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-md bg-amber px-4 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright transition-colors disabled:opacity-60"
            >
              {busy ? "Signing in…" : "Log in"}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-slate">
            New here?{" "}
            <button
              type="button"
              onClick={() => {
                setMode("signup");
                setError("");
              }}
              className="text-amber hover:underline focus:outline-none font-medium"
            >
              Create an account
            </button>
          </p>
        </>
      ) : (
        <>
          <form onSubmit={onSignup} className="mt-6 space-y-4">
            <TextField
              label="Full name"
              name="name"
              icon={UserRound}
              required
              minLength={2}
            />
            <TextField
              label="Email"
              name="email"
              icon={Mail}
              type="email"
              required
              placeholder="you@example.com"
            />
            <TextField
              label="Phone (optional, for SMS alerts)"
              name="phone"
              icon={Phone}
              type="tel"
              placeholder="+254712345678"
            />
            <label className="block">
              <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">
                Country (your home area)
              </span>
              <select
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value)}
                className="w-full rounded-md border border-line bg-panel px-3 py-2.5 text-sm focus:outline-none focus:border-amber"
                required
              >
                {ZONES.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <TextField
              label="Town / zone (optional)"
              name="zone"
              icon={MapPin}
              placeholder="e.g. Kisumu, Mathare"
            />
            <PasswordField
              label="Password"
              name="password"
              required
              minLength={8}
              placeholder="At least 8 characters"
            />
            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-md bg-amber px-4 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright transition-colors disabled:opacity-60"
            >
              {busy ? "Creating…" : "Create account"}
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
              className="text-amber hover:underline focus:outline-none font-medium"
            >
              Log in
            </button>
          </p>
        </>
      )}

      <p className="mt-8 text-xs text-slate leading-relaxed">
        Volunteer or operations staff?{" "}
        <Link to="/volunteer" className="text-amber hover:underline">
          Use the volunteer / ops sign-in
        </Link>
        .
      </p>
    </div>
  );
}
