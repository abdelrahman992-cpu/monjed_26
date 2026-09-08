import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Phone, MapPin, UserRound, Mail, KeyRound } from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import { useNavLoad } from "../components/PageLoader.jsx";
import TextField from "../components/ui/TextField.jsx";
import PasswordField from "../components/ui/PasswordField.jsx";
import { ZONES } from "../data/zones.js";
import { ApiError, verifyOtp } from "../lib/api.js";

function homeForRole(role, fallback = "/map") {
  if (role === "admin") return "/admin";
  if (role === "volunteer") return "/volunteer/dashboard";
  return fallback;
}

export default function LoginPage() {
  const { isSignedIn, session, loginAsUser, signupUser, setSession } =
    useAuth();
  const { go } = useNavLoad();
  const location = useLocation();
  const redirected = useRef(false);
  const [mode, setMode] = useState("login");
  const [error, setError] = useState("");
  const [countryCode, setCountryCode] = useState("KE");
  const [busy, setBusy] = useState(false);
  const [pendingOtpUser, setPendingOtpUser] = useState(null);
  const [otpCode, setOtpCode] = useState("");
  const [otpIntent, setOtpIntent] = useState("user"); // user | signup

  const afterLogin = location.state?.from || "/map";

  useEffect(() => {
    if (redirected.current || !isSignedIn) return;
    redirected.current = true;
    const dest = homeForRole(session?.role, afterLogin);
    go(dest, {
      replace: true,
      label:
        dest === "/admin"
          ? "Opening operations…"
          : dest === "/volunteer/dashboard"
            ? "Opening dashboard…"
            : "Opening your map…",
    });
  }, [isSignedIn, session, go, afterLogin]);

  async function onLogin(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const data = new FormData(e.target);
    try {
      const res = await loginAsUser(
        String(data.get("identifier") || "").trim(),
        String(data.get("password") || "")
      );
      if (res?.requires_otp) {
        setPendingOtpUser({
          userId: res.user_id || res.user?.user_id,
          email: res.email || String(data.get("identifier") || "").trim(),
        });
        setOtpIntent("user");
        setMode("verify_otp");
        return;
      }
      const dest = homeForRole(res?.role, afterLogin);
      go(dest, {
        label:
          dest === "/admin"
            ? "Opening operations…"
            : dest === "/volunteer/dashboard"
              ? "Opening dashboard…"
              : "Opening your map…",
      });
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : err.message || "Login failed"
      );
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
      const res = await signupUser({
        name: String(data.get("name") || "").trim(),
        email: String(data.get("email") || "").trim(),
        phone: String(data.get("phone") || "").trim(),
        password: String(data.get("password") || ""),
        country: country?.name || countryCode,
        countryCode,
        zone: String(data.get("zone") || "").trim(),
        notification_consent: true,
      });
      if (res?.requires_otp) {
        setPendingOtpUser({
          userId: res.user_id || res.user?.user_id,
          email: res.email || String(data.get("email") || "").trim(),
        });
        setOtpIntent("signup");
        setMode("verify_otp");
        return;
      }
      go(afterLogin, { label: "Opening your map…" });
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : err.message || "Signup failed"
      );
    } finally {
      setBusy(false);
    }
  }

  async function onVerifyOtp(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await verifyOtp({
        user_id: pendingOtpUser?.userId,
        code: otpCode.trim(),
      });
      if (setSession) setSession(res);
      const role = res?.user?.role;
      const dest = homeForRole(role, afterLogin);
      go(dest, {
        label:
          dest === "/admin"
            ? "Opening operations…"
            : dest === "/volunteer/dashboard"
              ? "Opening dashboard…"
              : "Opening your map…",
      });
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err.message || "Invalid OTP code"
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-5 sm:px-8 py-10 pb-16">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        {mode === "verify_otp" ? "VERIFICATION REQUIRED" : "SIGN IN · ALERTS READY"}
      </p>
      <h1 className="mt-3 font-display text-3xl font-bold">
        {mode === "login"
          ? "Log in"
          : mode === "verify_otp"
            ? "Verify email OTP"
            : "Create your account"}
      </h1>
      <p className="mt-3 text-sm text-slate leading-relaxed">
        {mode === "login"
          ? "Log in with the email or phone you registered with to open the map, report, and request help."
          : mode === "verify_otp"
            ? `Enter the 6-digit code sent to ${pendingOtpUser?.email || "your email"} or check server logs.`
            : "Register with email and country so we can show risk for your area — and send alerts when you opt in."}
      </p>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {mode === "verify_otp" ? (
        <>
          <form onSubmit={onVerifyOtp} className="mt-6 space-y-4">
            <TextField
              name="otp_code"
              label="6-Digit Verification Code"
              icon={KeyRound}
              required
              maxLength={6}
              placeholder="e.g. 849201"
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
            />
            <button
              type="submit"
              disabled={busy || otpCode.trim().length < 6}
              className="w-full rounded-md bg-amber px-4 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright transition-colors disabled:opacity-60"
            >
              {busy ? "Verifying…" : "Confirm & continue"}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-slate">
            <button
              type="button"
              onClick={() => {
                setMode(otpIntent === "signup" ? "signup" : "login");
                setOtpCode("");
                setError("");
              }}
              className="text-amber hover:underline focus:outline-none font-medium"
            >
              {otpIntent === "signup" ? "Back to sign up" : "Back to login"}
            </button>
          </p>
        </>
      ) : mode === "login" ? (
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
