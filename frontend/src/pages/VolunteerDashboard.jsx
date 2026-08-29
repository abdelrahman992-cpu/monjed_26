import { useCallback, useEffect, useMemo, useState } from "react";
import {
  MapPin,
  Phone,
  Clock,
  CheckCircle2,
  CircleDot,
  Inbox,
  Activity,
  ArrowRight,
  MessageSquare,
  LayoutDashboard,
  Settings2,
  Copy,
  Check,
} from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import {
  healthCheck,
  listVolunteerInbox,
  resolveAssistanceRequest,
  ApiError,
} from "../lib/api.js";
import DashboardShell from "../components/DashboardShell.jsx";
import {
  BarChart,
  DonutChart,
  Legend,
  SparkBars,
} from "../components/dashboard/MiniCharts.jsx";

function StatusPill({ status }) {
  const styles = {
    assigned: "border-teal/40 text-teal bg-teal/10",
    in_progress: "border-amber/40 text-amber bg-amber/10",
    resolved: "border-line text-slate bg-raised/40",
    pending: "border-mist/30 text-mist bg-panel",
  };
  return (
    <span
      className={`inline-flex rounded-full border px-2 py-0.5 font-mono text-[10px] tracking-wide uppercase ${
        styles[status] || "border-amber/40 text-amber bg-amber/10"
      }`}
    >
      {status}
    </span>
  );
}

function phoneFromDescription(description) {
  const m = String(description || "").match(/Phone:\s*([+\d][\d\s-]{6,})/i);
  return m ? m[1].trim() : "";
}

function resolveRequesterPhone(request) {
  return request?.requester_phone || phoneFromDescription(request?.description);
}

function normalizePhone(raw) {
  const cleaned = String(raw || "").trim();
  if (!cleaned || /^n\/a$/i.test(cleaned)) return null;
  const digits = cleaned.replace(/\D/g, "");
  if (digits.length < 7) return null;
  const tel = cleaned.startsWith("+") ? cleaned.replace(/\s/g, "") : `+${digits}`;
  return { display: tel, tel, wa: digits };
}

function ContactActions({ phone, name }) {
  const [copied, setCopied] = useState(false);
  const n = normalizePhone(phone);

  if (!n) {
    return (
      <p className="text-xs text-slate rounded-md border border-line bg-raised/40 px-3 py-2">
        No phone number on this request. Check the notes or ask ops for a callback
        number.
      </p>
    );
  }

  const message = encodeURIComponent(
    `Hello, this is a MONJED volunteer following up on your help request${
      name ? ` near ${name}` : ""
    }.`
  );

  async function copyPhone() {
    try {
      await navigator.clipboard.writeText(n.display);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 rounded-lg border border-line bg-night/30 px-3 py-2.5">
        <Phone size={15} className="text-amber shrink-0" />
        <span className="font-mono text-sm text-bone">{n.display}</span>
        <button
          type="button"
          onClick={copyPhone}
          className="ml-auto inline-flex items-center gap-1 rounded-md border border-line px-2.5 py-1 text-xs font-mono text-slate hover:border-amber/40 hover:text-amber transition-colors"
        >
          {copied ? <Check size={12} className="text-teal" /> : <Copy size={12} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <a
          href={`tel:${n.tel}`}
          className="inline-flex items-center gap-1.5 rounded-md bg-amber px-3.5 py-2 text-sm font-semibold text-ink hover:bg-amber-bright transition-colors"
        >
          <Phone size={14} /> Call
        </a>
        <a
          href={`https://wa.me/${n.wa}?text=${message}`}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 rounded-md border border-teal/40 bg-teal/10 px-3.5 py-2 text-sm font-semibold text-teal hover:bg-teal/20 transition-colors"
        >
          <MessageSquare size={14} /> WhatsApp
        </a>
        <a
          href={`sms:${n.tel}?body=${message}`}
          className="inline-flex items-center gap-1.5 rounded-md border border-line px-3.5 py-2 text-sm font-semibold hover:border-amber/40 transition-colors"
        >
          SMS
        </a>
      </div>
    </div>
  );
}

function dayKey(iso) {
  try {
    return new Date(iso).toISOString().slice(0, 10);
  } catch {
    return "";
  }
}

function isActiveStatus(status) {
  return status === "assigned" || status === "in_progress";
}

export default function VolunteerDashboardPage() {
  const { session, setAvailability } = useAuth();
  const [section, setSection] = useState("overview");
  const [filter, setFilter] = useState("active");
  const [apiStatus, setApiStatus] = useState("checking");
  const [requests, setRequests] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [busyId, setBusyId] = useState("");

  const volunteerId = session?.volunteer_id || session?.id;

  const refresh = useCallback(async () => {
    setLoadError("");
    if (!volunteerId) {
      setRequests([]);
      setApiStatus("down");
      setLoadError("No volunteer profile linked to this account.");
      return;
    }
    try {
      const [ok, inbox] = await Promise.all([
        healthCheck().then(() => true).catch(() => false),
        listVolunteerInbox(volunteerId),
      ]);
      setApiStatus(ok ? "ok" : "down");
      setRequests(Array.isArray(inbox) ? inbox : []);
    } catch (err) {
      setApiStatus("down");
      setLoadError(
        err instanceof ApiError ? err.message : "Could not load assignments."
      );
      setRequests([]);
    }
  }, [volunteerId]);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 15000);
    return () => clearInterval(id);
  }, [refresh]);

  const mine = useMemo(() => requests, [requests]);

  const assigned = mine.filter((r) => isActiveStatus(r.status));
  const completed = mine.filter((r) => r.status === "resolved");
  const visible = filter === "completed" ? completed : assigned;

  const needBreakdown = useMemo(() => {
    const map = {};
    mine.forEach((r) => {
      const k = r.request_type || "other";
      map[k] = (map[k] || 0) + 1;
    });
    const colors = ["#1d4ed8", "#0d9488", "#e11d48", "#64748b", "#3b82f6"];
    return Object.entries(map).map(([label, value], i) => ({
      label,
      value,
      color: colors[i % colors.length],
    }));
  }, [mine]);

  const activityBars = useMemo(() => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      const label = d.toLocaleDateString(undefined, { weekday: "short" });
      const count = mine.filter((r) => dayKey(r.created_at) === key).length;
      days.push({ label, value: count, color: "var(--color-amber)" });
    }
    return days;
  }, [mine]);

  const spark = useMemo(
    () => activityBars.map((d) => d.value),
    [activityBars]
  );

  async function complete(id) {
    setBusyId(id);
    setLoadError("");
    try {
      await resolveAssistanceRequest(id);
      await refresh();
    } catch (err) {
      setLoadError(
        err instanceof ApiError ? err.message : "Could not complete request."
      );
    } finally {
      setBusyId("");
    }
  }

  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    {
      id: "inbox",
      label: "My inbox",
      icon: Inbox,
      count: assigned.length,
    },
    { id: "settings", label: "Availability", icon: Settings2 },
  ];

  const apiBadge = (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] tracking-wide ${
        apiStatus === "ok"
          ? "border-teal/40 text-teal"
          : apiStatus === "down"
            ? "border-crimson/40 text-crimson"
            : "border-line text-slate"
      }`}
    >
      <Activity size={11} />
      API{" "}
      {apiStatus === "ok" ? "LIVE" : apiStatus === "down" ? "OFFLINE" : "…"}
    </span>
  );

  return (
    <DashboardShell
      title={
        section === "overview"
          ? "Overview"
          : section === "inbox"
            ? "My inbox"
            : "Availability"
      }
      subtitle={`${session.name} · ${session.zone || session.zone_id || "Zone"}, ${
        session.country || "—"
      } · Assignments from the assistance API`}
      navItems={navItems}
      activeId={section}
      onNavigate={setSection}
      badge={apiBadge}
    >
      {loadError && (
        <p className="mb-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {loadError}
        </p>
      )}

      {section === "overview" && (
        <div className="space-y-6">
          <div className="grid sm:grid-cols-3 gap-3">
            {[
              {
                label: "ACTIVE",
                value: assigned.length,
                hint: "Assigned — contact & respond",
                spark,
                color: "var(--color-amber)",
              },
              {
                label: "COMPLETED",
                value: completed.length,
                hint: "Resolved on the API",
                spark: spark.map((v) => Math.max(0, completed.length ? v : 0)),
                color: "var(--color-teal)",
              },
              {
                label: "AVAILABILITY",
                value: session.available ? "ON" : "OFF",
                hint: "Ops use this when assigning",
              },
            ].map((s) => (
              <div
                key={s.label}
                className="rounded-xl border border-line bg-panel/60 px-4 py-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-mono text-[10px] text-slate tracking-wide">
                      {s.label}
                    </p>
                    <p className="mt-1 font-display text-2xl font-bold tabular-nums">
                      {s.value}
                    </p>
                  </div>
                  {s.spark && <SparkBars values={s.spark} color={s.color} />}
                </div>
                <p className="mt-1 text-[11px] text-muted">{s.hint}</p>
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-2 gap-5">
            <div className="rounded-xl border border-line bg-panel/50 p-5">
              <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
                7-DAY ASSIGNMENT ACTIVITY
              </p>
              <p className="mt-1 text-sm text-slate">
                How many of your assignments were created each day.
              </p>
              <div className="mt-4">
                <BarChart rows={activityBars} height={150} />
              </div>
            </div>

            <div className="rounded-xl border border-line bg-panel/50 p-5 flex flex-col sm:flex-row gap-6 items-center sm:items-start">
              <div>
                <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
                  NEED MIX
                </p>
                <p className="mt-1 text-sm text-slate mb-4">
                  Breakdown of request types across your history.
                </p>
                <DonutChart
                  segments={
                    needBreakdown.length
                      ? needBreakdown
                      : [{ label: "None", value: 1, color: "#cfd8e6" }]
                  }
                  centerValue={mine.length}
                  centerLabel="total"
                />
              </div>
              <div className="flex-1 w-full min-w-0">
                <Legend
                  items={
                    needBreakdown.length
                      ? needBreakdown
                      : [{ label: "No assignments yet", value: 0, color: "#cfd8e6" }]
                  }
                />
                <button
                  type="button"
                  onClick={() => setSection("inbox")}
                  className="mt-6 inline-flex items-center gap-1.5 text-sm text-amber hover:underline"
                >
                  Open inbox <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>

          {assigned.length > 0 && (
            <div className="rounded-xl border border-teal/30 bg-teal/5 p-5">
              <p className="font-mono text-[10px] tracking-[0.14em] text-teal">
                NEEDS ATTENTION
              </p>
              <ul className="mt-3 space-y-2">
                {assigned.slice(0, 3).map((r) => (
                  <li
                    key={r.request_id}
                    className="flex flex-wrap items-center justify-between gap-2 text-sm"
                  >
                    <span className="font-medium">
                      {r.request_type} · {r.location}
                    </span>
                    <button
                      type="button"
                      onClick={() => setSection("inbox")}
                      className="text-xs text-amber hover:underline"
                    >
                      Respond
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {section === "inbox" && (
        <div>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <p className="text-sm text-slate max-w-xl">
              You only see requests assigned to you on the MONJED assistance API.
            </p>
            <div className="flex gap-1.5">
              {[
                { key: "active", label: "Active" },
                { key: "completed", label: "Done" },
              ].map((f) => (
                <button
                  key={f.key}
                  type="button"
                  onClick={() => setFilter(f.key)}
                  className={`px-3 py-1.5 text-xs font-mono rounded-md border ${
                    filter === f.key
                      ? "bg-amber text-ink border-amber font-bold"
                      : "border-line text-slate bg-panel"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {visible.length === 0 && (
              <div className="rounded-xl border border-dashed border-line p-8 text-center">
                <CircleDot size={22} className="mx-auto text-slate" />
                <p className="mt-3 text-sm text-slate max-w-md mx-auto">
                  {filter === "completed"
                    ? "No completed assignments yet."
                    : "Nothing assigned to you right now. Stay available — operations will match from the admin console."}
                </p>
              </div>
            )}

            {visible.map((r) => {
              const active = isActiveStatus(r.status);
              const phone = resolveRequesterPhone(r);
              return (
                <article
                  key={r.request_id}
                  className={`rounded-xl border p-5 ${
                    active
                      ? "border-teal/40 bg-teal/5"
                      : "border-line bg-panel/30"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-[11px] text-amber tracking-wide">
                          {r.request_type}
                        </span>
                        <StatusPill status={r.status} />
                      </div>
                      <h3 className="mt-2 font-display text-lg font-bold flex items-center gap-2">
                        <MapPin size={16} className="text-slate shrink-0" />
                        {r.location}
                      </h3>
                    </div>
                    <p className="font-mono text-[10px] text-muted inline-flex items-center gap-1">
                      <Clock size={10} />
                      {r.created_at
                        ? new Date(r.created_at).toLocaleString()
                        : "—"}
                    </p>
                  </div>

                  <p className="mt-3 text-sm text-mist leading-relaxed">
                    {r.description}
                  </p>

                  {active && (
                    <div className="mt-5 pt-4 border-t border-line space-y-3">
                      <p className="font-mono text-[10px] tracking-[0.14em] text-slate">
                        CONTACT THE REQUESTER
                      </p>
                      <ContactActions phone={phone} name={r.location} />
                    </div>
                  )}

                  {active && (
                    <div className="mt-4">
                      <button
                        type="button"
                        disabled={busyId === r.request_id}
                        onClick={() => complete(r.request_id)}
                        className="rounded-md border border-teal/40 px-4 py-2 text-sm font-semibold text-teal hover:bg-teal/10 transition-colors inline-flex items-center gap-1.5 disabled:opacity-60"
                      >
                        <CheckCircle2 size={15} />{" "}
                        {busyId === r.request_id
                          ? "Resolving…"
                          : "Mark completed"}
                      </button>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      )}

      {section === "settings" && (
        <div className="rounded-xl border border-line bg-panel/50 p-6 max-w-md">
          <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
            MATCHING
          </p>
          <p className="mt-2 text-sm text-slate leading-relaxed">
            When you are available, operations can assign help requests to your
            private inbox via the assistance API.
          </p>
          <label className="mt-5 inline-flex items-center gap-3 text-sm border border-line rounded-lg px-4 py-3 bg-night/30 cursor-pointer w-full">
            <input
              type="checkbox"
              checked={!!session.available}
              onChange={(e) => setAvailability(e.target.checked)}
              className="accent-amber size-4"
            />
            <span>
              <span className="font-semibold block">Available for matching</span>
              <span className="text-xs text-slate">
                Currently {session.available ? "ON" : "OFF"}
              </span>
            </span>
          </label>
        </div>
      )}
    </DashboardShell>
  );
}
