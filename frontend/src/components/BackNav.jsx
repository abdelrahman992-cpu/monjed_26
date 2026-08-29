import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";

/** When signed in: go back one history step. When not: go to landing. */
export default function BackNav({ className = "" }) {
  const navigate = useNavigate();
  const { session, isSignedIn } = useAuth();

  function onBack() {
    if (!isSignedIn) {
      navigate("/");
      return;
    }
    // Prefer one step back; fall back to role home if there is no history.
    if (window.history.length > 1) {
      navigate(-1);
      return;
    }
    if (session?.role === "admin") navigate("/admin");
    else if (session?.role === "volunteer") navigate("/volunteer/dashboard");
    else navigate("/map");
  }

  return (
    <button
      type="button"
      onClick={onBack}
      className={`inline-flex items-center gap-1.5 text-sm text-slate hover:text-amber transition-colors ${className}`}
    >
      <ArrowLeft size={15} strokeWidth={1.75} />
      Back
    </button>
  );
}
