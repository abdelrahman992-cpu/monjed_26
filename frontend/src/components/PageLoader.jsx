import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const NavLoadContext = createContext(null);

const DEFAULT_MS = 1100;

export function NavLoadProvider({ children }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [label, setLabel] = useState("Connecting…");

  const go = useCallback(
    (to, { replace = false, label: nextLabel = "Connecting…", delay = DEFAULT_MS } = {}) => {
      setLabel(nextLabel);
      setLoading(true);
      window.setTimeout(() => {
        navigate(to, { replace });
        window.setTimeout(() => setLoading(false), 180);
      }, delay);
    },
    [navigate]
  );

  const value = useMemo(
    () => ({
      loading,
      label,
      go,
      start(nextLabel = "Connecting…") {
        setLabel(nextLabel);
        setLoading(true);
      },
      stop() {
        setLoading(false);
      },
    }),
    [loading, label, go]
  );

  return (
    <NavLoadContext.Provider value={value}>
      {children}
      {loading ? <PageLoader label={label} /> : null}
    </NavLoadContext.Provider>
  );
}

export function useNavLoad() {
  const ctx = useContext(NavLoadContext);
  if (!ctx) throw new Error("useNavLoad must be used within NavLoadProvider");
  return ctx;
}

export function PageLoader({ label = "Connecting…" }) {
  return (
    <div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center gap-5 bg-night/92 backdrop-blur-sm"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="relative h-12 w-12">
        <div className="absolute inset-0 rounded-full border border-line" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-amber animate-[spin_2.4s_linear_infinite]" />
      </div>
      <p className="font-mono text-[11px] tracking-[0.2em] text-slate uppercase">
        {label}
      </p>
    </div>
  );
}
