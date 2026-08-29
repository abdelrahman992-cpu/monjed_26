import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CheckCircle2,
  Clock,
  MapPin,
  MessageSquareWarning,
  Radio,
  Users,
  Activity,
  Loader2,
  Shield,
  Siren,
  LayoutDashboard,
  Inbox,
  Waves,
  FileWarning,
  ArrowRight,
} from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import {
  analyzeCommunityReport,
  healthCheck,
  listAssistanceRequests,
  listCommunityReports,
  listVolunteers as listVolunteersApi,
  listPlatformUsers,
  matchAssistanceRequest,
  resolveCommunityReport,
  verifyCommunityReport,
  ApiError,
} from "../lib/api.js";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import FloodAssessPanel from "../components/FloodAssessPanel.jsx";
import DashboardShell from "../components/DashboardShell.jsx";
import {
  BarChart,
  DonutChart,
  Legend,
  SparkBars,
} from "../components/dashboard/MiniCharts.jsx";

function StatusPill({ status }) {
  const styles = {
    new: "border-amber/40 text-amber bg-amber/10",
    verified: "border-teal/40 text-teal bg-teal/10",
    resolved: "border-line text-slate bg-raised/40",
    pending: "border-amber/40 text-amber bg-amber/10",
    assigned: "border-teal/40 text-teal bg-teal/10",
    in_progress: "border-amber/40 text-amber bg-amber/10",
  };
  return (
    <span
      className={`inline-flex rounded-full border px-2 py-0.5 font-mono text-[10px] tracking-wide uppercase ${
        styles[status] || "border-line text-slate"
      }`}
    >
      {status}
    </span>
  );
}

function dayKey(iso) {
  try {
    return new Date(iso).toISOString().slice(0, 10);
  } catch {
    return "";
  }
}

function mapCommunityReport(r) {
  const analysis = r?.analysis ?? null;
  const hazard = analysis?.hazard_type
    ? String(analysis.hazard_type).replace(/_/g, " ").toUpperCase()
    : "";
  const fromText = String(r?.report_text || "")
    .trim()
    .split(/\s+/)
    .slice(0, 4)
    .join(" ");
  const category =
    hazard || (fromText ? fromText.toUpperCase() : "GROUND REPORT");
  return {
    id: r.report_id,
    category,
    location: r.location || "",
    notes: r.report_text || "",
    status: r.resolved ? "resolved" : r.verified ? "verified" : "new",
    analysis,
    createdAt: r.created_at,
    zone_id: r.zone_id,
    reporter_id: r.reporter_id,
  };
}

export default function AdminPage() {
  const { session } = useAuth();
  const [section, setSection] = useState("overview");
  const [apiStatus, setApiStatus] = useState("checking");
  const [analyzingId, setAnalyzingId] = useState(null);
  const [analyzeError, setAnalyzeError] = useState("");
  const [reports, setReports] = useState([]);
  const [help, setHelp] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [actionBusyId, setActionBusyId] = useState(null);

  const loadLive = useCallback(async () => {
    setLoadError("");
    try {
      const [ok, helpResult, vols, community, platformUsers] = await Promise.all([
        healthCheck()
          .then(() => true)
          .catch(() => false),
        listAssistanceRequests()
          .then((rows) => ({ rows, error: "" }))
          .catch((err) => ({
            rows: [],
            error:
              err instanceof ApiError
                ? `Help queue: ${err.message}`
                : "Help queue: could not load assistance requests.",
          })),
        listVolunteersApi().catch(() => []),
        listCommunityReports().catch(() => null),
        listPlatformUsers().catch(() => []),
      ]);
      setApiStatus(ok ? "ok" : "down");
      setHelp(Array.isArray(helpResult.rows) ? helpResult.rows : []);
      if (helpResult.error) {
        setLoadError(helpResult.error);
      }
      setVolunteers(Array.isArray(vols) ? vols : []);
      setUsers(Array.isArray(platformUsers) ? platformUsers : []);
      if (Array.isArray(community)) {
        setReports(community.map(mapCommunityReport));
      } else if (community == null) {
        setReports([]);
      }
    } catch (err) {
      setApiStatus("down");
      setLoadError(
        err instanceof ApiError ? err.message : "Could not refresh live queues."
      );
    }
  }, []);

  useEffect(() => {
    loadLive();
    const id = setInterval(loadLive, 20000);
    return () => clearInterval(id);
  }, [loadLive]);

  const pending = reports.filter((r) => r.status === "new").length;
  const verified = reports.filter((r) => r.status === "verified").length;
  const resolved = reports.filter((r) => r.status === "resolved").length;
  const roadBlocked = reports.filter(
    (r) =>
      r.category === "ROAD BLOCKED" ||
      r.analysis?.blocked_road === true ||
      /road\s*block/i.test(r.notes || "")
  ).length;
  const helpQueued = help.filter((r) => r.status === "pending").length;
  const helpAssigned = help.filter(
    (r) => r.status === "assigned" || r.status === "in_progress"
  ).length;
  const helpDone = help.filter((r) => r.status === "resolved").length;
  const availableVols = volunteers.filter((v) => v.available).length;
  const smsEligibleUsers = users.filter((u) => u.sms_eligible).length;
  const citizenUsers = users.filter(
    (u) => (u.role || "").toLowerCase() === "citizen"
  ).length;

  const reportStatusSegments = [
    { label: "New", value: pending, color: "#c9852a" },
    { label: "Verified", value: verified, color: "#0d9488" },
    { label: "Resolved", value: resolved, color: "#64748b" },
  ].filter((s) => s.value > 0);

  const helpStatusSegments = [
    { label: "Pending", value: helpQueued, color: "#e11d48" },
    { label: "Active", value: helpAssigned, color: "#0d9488" },
    { label: "Resolved", value: helpDone, color: "#64748b" },
  ].filter((s) => s.value > 0);

  const categoryBars = useMemo(() => {
    const map = {};
    reports.forEach((r) => {
      const k = (r.category || "OTHER").replace(/_/g, " ").slice(0, 14);
      map[k] = (map[k] || 0) + 1;
    });
    return Object.entries(map)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([label, value]) => ({
        label,
        value,
        color: "var(--color-amber)",
      }));
  }, [reports]);

  const weekBars = useMemo(() => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      const label = d.toLocaleDateString(undefined, { weekday: "short" });
      const reportsN = reports.filter((r) => dayKey(r.createdAt) === key).length;
      const helpN = help.filter((r) => dayKey(r.created_at) === key).length;
      days.push({
        label,
        value: reportsN + helpN,
        color: "var(--color-teal)",
      });
    }
    return days;
  }, [reports, help]);

  const attention = useMemo(() => {
    const items = [];
    help
      .filter((r) => r.status === "pending")
      .slice(0, 4)
      .forEach((r) => {
        items.push({
          id: r.request_id,
          kind: "help",
          title: r.request_type?.replace(/_/g, " ") || "Help request",
          meta: r.location,
          when: r.created_at,
        });
      });
    reports
      .filter((r) => r.status === "new")
      .slice(0, 4)
      .forEach((r) => {
        items.push({
          id: r.id,
          kind: "report",
          title: r.category || "Ground report",
          meta: r.location,
          when: r.createdAt,
        });
      });
    return items.slice(0, 6);
  }, [help, reports]);

  async function reanalyze(report) {
    setAnalyzeError("");
    setAnalyzingId(report.id);
    const report_text = report.notes?.trim()
      ? `${report.category}. ${report.notes.trim()}`
      : `${report.category || "Ground report"} reported at this location.`;
    const location = (report.location || "").trim() || "unknown location";
    const zone_id =
      report.zone_id || session?.zone_id || session?.countryCode || "KE";
    try {
      const analysis = await analyzeCommunityReport({
        report_text,
        zone_id,
        location,
        reporter_id: report.reporter_id || session?.id || null,
      });
      setReports((prev) =>
        prev.map((r) =>
          r.id === report.id ? { ...r, analysis, zone_id } : r
        )
      );
    } catch (err) {
      setAnalyzeError(
        err instanceof ApiError
          ? err.message
          : "Analyze API unreachable. Start the FastAPI backend."
      );
    } finally {
      setAnalyzingId(null);
    }
  }

  async function onVerify(report) {
    setLoadError("");
    setActionBusyId(report.id);
    try {
      await verifyCommunityReport(report.id);
      await loadLive();
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Verify failed.");
    } finally {
      setActionBusyId(null);
    }
  }

  async function onResolve(report) {
    setLoadError("");
    setActionBusyId(report.id);
    try {
      await resolveCommunityReport(report.id);
      await loadLive();
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Resolve failed.");
    } finally {
      setActionBusyId(null);
    }
  }

  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    {
      id: "inbox",
      label: "Ops inbox",
      icon: Inbox,
      count: pending + helpQueued,
    },
    {
      id: "reports",
      label: "Ground reports",
      icon: FileWarning,
      count: reports.length,
    },
    {
      id: "help",
      label: "Help queue",
      icon: Radio,
      count: help.length,
    },
    {
      id: "users",
      label: "Users",
      icon: Users,
      count: users.length,
    },
    {
      id: "network",
      label: "Volunteers",
      icon: Shield,
      count: volunteers.length,
    },
    { id: "engine", label: "Flood engine", icon: Waves },
  ];

  const titles = {
    overview: "Overview",
    inbox: "Ops inbox",
    reports: "Ground reports",
    help: "Help queue",
    users: "Platform users",
    network: "Volunteer network",
    engine: "Flood engine",
  };

  const apiBadge = (
    <div className="flex items-center gap-2">
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
        {apiStatus === "ok"
          ? "LIVE"
          : apiStatus === "down"
            ? "OFFLINE"
            : "…"}
      </span>
      <button
        type="button"
        onClick={() => {
          loadLive();
        }}
        className="hidden sm:inline-flex rounded-full border border-line px-2.5 py-1 font-mono text-[10px] text-slate hover:text-bone"
      >
        Refresh
      </button>
    </div>
  );

  return (
    <DashboardShell
      title={titles[section] || "Operations"}
      subtitle={`${session?.title || "Operations"} · ${
        session?.organization || "MONJED"
      } · Live assistance, volunteers & community reports from the API`}
      navItems={navItems}
      activeId={section}
      onNavigate={setSection}
      badge={apiBadge}
    >
      {(analyzeError || loadError) && (
        <p className="mb-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {analyzeError || loadError}
        </p>
      )}

      {section === "overview" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-line bg-gradient-to-br from-panel via-panel to-raised/40 p-5 sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-mono text-[10px] tracking-[0.18em] text-amber">
                  OPERATIONS BRIEFING
                </p>
                <h2 className="mt-1 font-display text-xl sm:text-2xl font-bold tracking-tight">
                  {helpQueued + pending > 0
                    ? `${helpQueued + pending} item${
                        helpQueued + pending === 1 ? "" : "s"
                      } need attention`
                    : "Queues are clear"}
                </h2>
                <p className="mt-2 text-sm text-slate max-w-xl leading-relaxed">
                  Help requests, volunteers, and ground reports load from the
                  live API — verify and resolve write back to community storage.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setSection("inbox")}
                  className="inline-flex items-center gap-1.5 rounded-md bg-amber px-3.5 py-2 text-sm font-semibold text-ink hover:bg-amber-bright"
                >
                  Open inbox <ArrowRight size={14} />
                </button>
                <button
                  type="button"
                  onClick={() => setSection("users")}
                  className="inline-flex items-center gap-1.5 rounded-md border border-line px-3.5 py-2 text-sm hover:border-amber/40"
                >
                  Users
                </button>
                <button
                  type="button"
                  onClick={() => setSection("network")}
                  className="inline-flex items-center gap-1.5 rounded-md border border-line px-3.5 py-2 text-sm hover:border-amber/40"
                >
                  Volunteers
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              {
                label: "HELP PENDING",
                value: helpQueued,
                hint: "Awaiting match",
                tone: "text-amber",
                icon: Radio,
              },
              {
                label: "SIGNED-UP USERS",
                value: users.length,
                hint: `${smsEligibleUsers} SMS-eligible · ${citizenUsers} citizens`,
                tone: "text-bone",
                icon: Users,
              },
              {
                label: "VOLUNTEERS UP",
                value: `${availableVols}/${volunteers.length || 0}`,
                hint: "Available now",
                tone: "text-mist",
                icon: Shield,
              },
              {
                label: "NEW REPORTS",
                value: pending,
                hint: "API triage inbox",
                tone: "text-mist",
                icon: FileWarning,
                spark: weekBars.map((d) => d.value),
              },
            ].map((s) => {
              const Icon = s.icon;
              return (
                <div
                  key={s.label}
                  className="rounded-xl border border-line bg-panel/70 px-4 py-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-mono text-[10px] text-slate tracking-wide inline-flex items-center gap-1.5">
                        <Icon size={11} className="text-amber" />
                        {s.label}
                      </p>
                      <p
                        className={`mt-2 font-display text-3xl font-bold tabular-nums ${s.tone}`}
                      >
                        {s.value}
                      </p>
                      <p className="mt-1 text-[11px] text-muted">{s.hint}</p>
                    </div>
                    {s.spark && (
                      <SparkBars values={s.spark} color="var(--color-amber)" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {roadBlocked >= 2 && (
            <div className="rounded-xl border border-crimson/40 bg-crimson/10 px-4 py-3 text-sm flex items-start gap-2">
              <Siren size={16} className="text-crimson mt-0.5 shrink-0" />
              <p>
                Feasibility flag: multiple <strong>ROAD BLOCKED</strong> reports
                in the queue. Annotate the flood alert — verify route before
                travel. Help active: {helpAssigned}.
              </p>
            </div>
          )}

          <div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-5">
            <div className="rounded-xl border border-line bg-panel/50 p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
                    NEEDS ATTENTION
                  </p>
                  <p className="mt-1 text-sm text-slate">
                    Newest pending help and unverified ground reports.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSection("inbox")}
                  className="text-xs text-amber hover:underline"
                >
                  View all
                </button>
              </div>
              <ul className="mt-4 divide-y divide-line">
                {attention.length === 0 && (
                  <li className="py-8 text-center text-sm text-slate border border-dashed border-line rounded-lg">
                    Nothing waiting — keep the flood engine warm.
                  </li>
                )}
                {attention.map((item) => (
                  <li
                    key={`${item.kind}-${item.id}`}
                    className="py-3 flex flex-wrap items-center justify-between gap-2"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">
                        <span className="font-mono text-[10px] text-amber mr-2 uppercase">
                          {item.kind}
                        </span>
                        {item.title}
                      </p>
                      <p className="text-xs text-slate truncate flex items-center gap-1 mt-0.5">
                        <MapPin size={11} /> {item.meta || "—"}
                      </p>
                    </div>
                    <p className="font-mono text-[10px] text-muted inline-flex items-center gap-1">
                      <Clock size={10} />
                      {item.when ? new Date(item.when).toLocaleString() : "—"}
                    </p>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-xl border border-line bg-panel/50 p-5 flex gap-5 items-start">
              <DonutChart
                segments={
                  helpStatusSegments.length
                    ? helpStatusSegments
                    : [{ label: "Empty", value: 1, color: "#cfd8e6" }]
                }
                centerValue={help.length}
                centerLabel="help"
              />
              <div className="flex-1 min-w-0">
                <p className="font-mono text-[10px] tracking-[0.14em] text-slate mb-3">
                  HELP PIPELINE · API
                </p>
                <Legend
                  items={
                    helpStatusSegments.length
                      ? helpStatusSegments
                      : [
                          {
                            label: "No help requests",
                            value: 0,
                            color: "#cfd8e6",
                          },
                        ]
                  }
                />
                <button
                  type="button"
                  onClick={() => setSection("help")}
                  className="mt-5 inline-flex items-center gap-1.5 text-sm text-amber hover:underline"
                >
                  Open help queue <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-5">
            <div className="rounded-xl border border-line bg-panel/50 p-5">
              <p className="font-mono text-[10px] tracking-[0.14em] text-amber">
                7-DAY INTAKE
              </p>
              <p className="mt-1 text-sm text-slate">
                Combined ground reports + API help requests per day.
              </p>
              <div className="mt-4">
                <BarChart rows={weekBars} height={150} />
              </div>
            </div>

            <div className="rounded-xl border border-line bg-panel/50 p-5 flex gap-5 items-start">
              <DonutChart
                segments={
                  reportStatusSegments.length
                    ? reportStatusSegments
                    : [{ label: "Empty", value: 1, color: "#cfd8e6" }]
                }
                centerValue={reports.length}
                centerLabel="reports"
              />
              <div className="flex-1 min-w-0">
                <p className="font-mono text-[10px] tracking-[0.14em] text-slate mb-3">
                  REPORT PIPELINE · API
                </p>
                <Legend
                  items={
                    reportStatusSegments.length
                      ? reportStatusSegments
                      : [{ label: "No reports", value: 0, color: "#cfd8e6" }]
                  }
                />
                {categoryBars.length > 0 && (
                  <div className="mt-4">
                    <BarChart rows={categoryBars} height={100} />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {section === "inbox" && (
        <div className="space-y-6">
          <p className="text-sm text-slate max-w-2xl">
            Unified attention list — new ground reports and unassigned help.
            Open dedicated queues for full triage and assign.
          </p>
          <div className="grid lg:grid-cols-2 gap-5">
            <div className="space-y-3">
              <h2 className="font-mono text-xs tracking-widest text-slate">
                NEW REPORTS · {pending}
              </h2>
              {reports.filter((r) => r.status === "new").length === 0 && (
                <p className="text-sm text-slate border border-dashed border-line rounded-xl p-6 text-center">
                  No new reports waiting.
                </p>
              )}
              {reports
                .filter((r) => r.status === "new")
                .slice(0, 8)
                .map((report) => (
                  <button
                    key={report.id}
                    type="button"
                    onClick={() => setSection("reports")}
                    className="w-full text-left rounded-xl border border-amber/40 bg-panel/50 p-4 hover:border-amber transition-colors"
                  >
                    <p className="font-display font-bold">{report.category}</p>
                    <p className="text-xs text-slate mt-1 flex items-center gap-1">
                      <MapPin size={11} /> {report.location}
                    </p>
                  </button>
                ))}
            </div>
            <div className="space-y-3">
              <h2 className="font-mono text-xs tracking-widest text-slate">
                HELP NEEDING ASSIGN · {helpQueued}
              </h2>
              {help.filter((h) => h.status === "pending").length === 0 && (
                <p className="text-sm text-slate border border-dashed border-line rounded-xl p-6 text-center">
                  No help waiting for a volunteer.
                </p>
              )}
              {help
                .filter((h) => h.status === "pending")
                .slice(0, 8)
                .map((h) => (
                  <button
                    key={h.request_id}
                    type="button"
                    onClick={() => setSection("help")}
                    className="w-full text-left rounded-xl border border-line bg-panel/50 p-4 hover:border-amber/40 transition-colors"
                  >
                    <p className="font-mono text-[10px] text-amber">
                      {h.request_type}
                    </p>
                    <p className="font-display font-bold mt-1">{h.location}</p>
                    <StatusPill status={h.status} />
                  </button>
                ))}
            </div>
          </div>
        </div>
      )}

      {section === "reports" && (
        <div className="grid lg:grid-cols-[1.4fr_0.9fr] gap-6">
          <div className="space-y-3">
            <h2 className="font-mono text-xs tracking-widest text-slate flex items-center gap-2">
              <Radio size={14} className="text-amber" /> TRIAGE · NEW → VERIFIED
              → RESOLVED
            </h2>
            {reports.length === 0 && (
              <p className="text-sm text-slate border border-dashed border-line rounded-xl p-8 text-center">
                No reports yet. Public submissions from /report appear here via
                the community-reports API.
              </p>
            )}
            {reports.map((report) => (
              <article
                key={report.id}
                className={`rounded-xl border p-5 ${
                  report.status === "new"
                    ? "border-amber/40 bg-panel/50"
                    : "border-line bg-panel/30"
                }`}
              >
                <div className="flex flex-wrap justify-between gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <MessageSquareWarning size={16} className="text-amber" />
                      <span className="font-display font-bold">
                        {report.category}
                      </span>
                      <StatusPill status={report.status} />
                    </div>
                    <p className="mt-1.5 text-sm text-mist flex items-center gap-1">
                      <MapPin size={12} /> {report.location}
                    </p>
                  </div>
                  <span className="font-mono text-[10px] text-slate flex items-center gap-1">
                    <Clock size={10} />
                    {report.createdAt
                      ? new Date(report.createdAt).toLocaleString()
                      : "—"}
                  </span>
                </div>

                {report.notes && (
                  <p className="mt-3 text-sm text-bone bg-raised/60 border border-line rounded-lg p-3 leading-relaxed">
                    {report.notes}
                  </p>
                )}

                {report.analysis && (
                  <div className="mt-3 flex flex-wrap gap-2 items-center text-xs">
                    <RiskBadge level={report.analysis.severity} />
                    <span className="font-mono text-slate">
                      {report.analysis.hazard_type} ·{" "}
                      {(
                        Number(report.analysis.analysis_confidence || 0) * 100
                      ).toFixed(0)}
                      % conf
                    </span>
                    {(report.analysis.extracted_evidence || [])
                      .slice(0, 2)
                      .map((e) => (
                        <span
                          key={e}
                          className="rounded border border-line px-1.5 py-0.5 text-muted"
                        >
                          {e}
                        </span>
                      ))}
                  </div>
                )}

                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={
                      report.status !== "new" || actionBusyId === report.id
                    }
                    onClick={() => onVerify(report)}
                    className="px-3 py-2 text-xs font-mono uppercase rounded-md border border-teal/30 text-teal disabled:opacity-40 hover:bg-teal/10"
                  >
                    <span className="inline-flex items-center gap-1">
                      {actionBusyId === report.id ? (
                        <Loader2 size={13} className="animate-spin" />
                      ) : (
                        <CheckCircle2 size={13} />
                      )}{" "}
                      Verify
                    </span>
                  </button>
                  <button
                    type="button"
                    disabled={
                      report.status === "resolved" ||
                      actionBusyId === report.id
                    }
                    onClick={() => onResolve(report)}
                    className="px-3 py-2 text-xs font-mono uppercase rounded-md border border-line text-mist disabled:opacity-40"
                  >
                    Resolve
                  </button>
                  <button
                    type="button"
                    disabled={analyzingId === report.id}
                    onClick={() => reanalyze(report)}
                    className="px-3 py-2 text-xs font-mono uppercase rounded-md border border-amber/30 text-amber disabled:opacity-40 inline-flex items-center gap-1.5"
                  >
                    {analyzingId === report.id && (
                      <Loader2 size={12} className="animate-spin" />
                    )}
                    Re-run analyze API
                  </button>
                </div>
              </article>
            ))}
          </div>

          <div className="rounded-xl border border-line bg-panel/40 p-5 h-fit lg:sticky lg:top-20">
            <p className="font-mono text-[10px] tracking-[0.14em] text-amber inline-flex items-center gap-1.5">
              <Shield size={12} /> OPS NOTES
            </p>
            <ul className="mt-3 space-y-2 text-sm text-slate leading-relaxed">
              <li>
                — Verify calls{" "}
                <span className="font-mono text-mist">
                  POST /api/community-reports/&#123;id&#125;/verify
                </span>
                .
              </li>
              <li>
                — Resolve calls{" "}
                <span className="font-mono text-mist">
                  POST /api/community-reports/&#123;id&#125;/resolve
                </span>
                .
              </li>
              <li>
                — Re-run analyze calls{" "}
                <span className="font-mono text-mist">
                  POST /api/community-reports/analyze
                </span>
                .
              </li>
              <li>
                — Severity badges map to backend{" "}
                <span className="font-mono">
                  low / moderate / high / critical
                </span>
                .
              </li>
            </ul>
          </div>
        </div>
      )}

      {section === "help" && (
        <div className="space-y-4">
          <p className="text-sm text-slate max-w-2xl">
            Match pending requests to available volunteers in the same zone via
            the assistance API. Volunteers only see their own assignments.
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {help.length === 0 && (
              <p className="sm:col-span-2 lg:col-span-3 text-sm text-slate border border-dashed border-line rounded-xl p-8 text-center">
                Empty. Public /help submissions appear here as pending.
              </p>
            )}
            {help.map((h) => {
              const assignee = volunteers.find(
                (v) => v.volunteer_id === h.assigned_volunteer_id
              );
              const canMatch = h.status === "pending";
              return (
                <div
                  key={h.request_id}
                  className="rounded-xl border border-line bg-panel/50 p-5 flex flex-col"
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-mono text-[10px] text-amber">
                      {h.request_type}
                    </p>
                    <StatusPill status={h.status} />
                  </div>
                  <p className="font-display font-bold mt-2 text-lg">
                    {h.location}
                  </p>
                  <p className="text-slate text-sm mt-2 leading-relaxed flex-1">
                    {h.description}
                  </p>
                  <div className="mt-3 space-y-1 text-xs text-muted">
                    <p className="font-mono">Zone · {h.zone_id}</p>
                    <p className="font-mono uppercase">
                      {h.priority} · {h.hazard}
                    </p>
                    {Array.isArray(h.accessibility_needs) &&
                      h.accessibility_needs.length > 0 && (
                        <p className="font-mono text-teal">
                          Accessibility · {h.accessibility_needs.join(", ")}
                        </p>
                      )}
                    {assignee && (
                      <p className="font-mono text-teal">
                        Assigned · {assignee.name}
                      </p>
                    )}
                  </div>

                  {canMatch && (
                    <div className="mt-4 space-y-2">
                      <button
                        type="button"
                        className="w-full rounded-md bg-amber px-3 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright"
                        onClick={async () => {
                          try {
                            await matchAssistanceRequest(h.request_id);
                            await loadLive();
                          } catch (err) {
                            setLoadError(
                              err instanceof ApiError
                                ? err.message
                                : "Match failed."
                            );
                          }
                        }}
                      >
                        Auto-match available volunteer
                      </button>
                      {volunteers.filter(
                        (v) => v.available && v.zone_id === h.zone_id
                      ).length === 0 && (
                        <p className="text-[11px] text-slate">
                          No available volunteers in zone {h.zone_id}.
                        </p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {section === "users" && (
        <div className="space-y-4">
          <p className="text-sm text-slate max-w-2xl leading-relaxed">
            People who created accounts on the platform. Flood pipeline SMS goes
            to users marked SMS-eligible in the same zone as the run (phone +
            notification consent + zone_id).
          </p>
          <div className="flex flex-wrap gap-3 text-xs font-mono text-slate">
            <span className="rounded-md border border-line px-2.5 py-1">
              Total {users.length}
            </span>
            <span className="rounded-md border border-teal/30 bg-teal/10 text-teal px-2.5 py-1">
              SMS-eligible {smsEligibleUsers}
            </span>
            <span className="rounded-md border border-line px-2.5 py-1">
              Citizens {citizenUsers}
            </span>
          </div>
          <div className="rounded-xl border border-line overflow-hidden">
            <div className="grid grid-cols-[1.2fr_1fr_0.6fr_0.5fr_0.7fr] gap-2 px-4 py-2.5 bg-raised/40 font-mono text-[10px] tracking-wide text-slate border-b border-line">
              <span>NAME</span>
              <span>CONTACT</span>
              <span>ZONE</span>
              <span>ROLE</span>
              <span>SMS</span>
            </div>
            {users.length === 0 && (
              <p className="text-sm text-slate p-8 text-center border-t border-line">
                No signed-up users yet (or Mongo is unavailable). Citizen
                signups from /login appear here.
              </p>
            )}
            {users.map((u) => (
              <div
                key={u.user_id}
                className="grid grid-cols-[1.2fr_1fr_0.6fr_0.5fr_0.7fr] gap-2 px-4 py-3 border-t border-line items-center text-sm"
              >
                <div className="min-w-0">
                  <p className="font-medium truncate">
                    {u.display_name || "—"}
                  </p>
                  <p className="text-[11px] text-muted font-mono truncate">
                    {u.user_id}
                  </p>
                </div>
                <div className="min-w-0 text-xs text-slate">
                  <p className="truncate">{u.email || "—"}</p>
                  <p className="font-mono truncate">{u.phone || "no phone"}</p>
                </div>
                <span className="font-mono text-xs">
                  {u.zone_id || "—"}
                </span>
                <span className="font-mono text-[10px] uppercase text-slate">
                  {u.role || "—"}
                </span>
                <span
                  className={`font-mono text-[10px] ${
                    u.sms_eligible ? "text-teal" : "text-muted"
                  }`}
                >
                  {u.sms_eligible ? "ELIGIBLE" : "NO"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {section === "network" && (
        <div className="space-y-4">
          <p className="text-sm text-slate max-w-2xl">
            Volunteers registered on the assistance API. Match help from the Help
            queue — they only see their own assignments.
          </p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {volunteers.length === 0 && (
              <p className="sm:col-span-2 lg:col-span-3 text-sm text-slate border border-dashed border-line rounded-xl p-8 text-center">
                No volunteers registered yet. Sign-ups from /volunteer appear
                here.
              </p>
            )}
            {volunteers.map((v) => (
              <div
                key={v.volunteer_id}
                className="rounded-xl border border-line bg-panel/50 p-4 flex gap-3"
              >
                <span className="h-11 w-11 rounded-full bg-raised border border-line flex items-center justify-center font-display font-bold text-amber text-sm shrink-0">
                  {(v.name || "?")[0]}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-display font-bold truncate">{v.name}</p>
                      <p className="text-xs text-slate mt-0.5">
                        Zone {v.zone_id}
                        {v.phone ? ` · ${v.phone}` : ""}
                      </p>
                    </div>
                    <span
                      className={`inline-flex rounded-full border px-2 py-0.5 font-mono text-[10px] tracking-wide uppercase shrink-0 ${
                        v.available
                          ? "border-teal/40 text-teal bg-teal/10"
                          : "border-line text-slate bg-raised/40"
                      }`}
                    >
                      {v.available ? "available" : "offline"}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-mist truncate">
                    {(v.skills || []).join(" · ") || "No skills listed"}
                  </p>
                  <p className="mt-1 font-mono text-[10px] text-muted">
                    {v.vehicle_type || "none"} · cap {v.capacity || 0}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {section === "engine" && (
        <div className="max-w-2xl">
          <FloodAssessPanel allowPipeline />
        </div>
      )}
    </DashboardShell>
  );
}
