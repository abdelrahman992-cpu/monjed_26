const DEFAULT_BASE = "http://127.0.0.1:8000";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? 0;
    this.body = body ?? null;
  }
}

/** Normalize to E.164 (+digits only) for backend phone validation. */
export function toE164(phone) {
  const raw = String(phone || "").replace(/[\s()-]/g, "");
  if (!raw) return null;
  const withPlus = raw.startsWith("+") ? raw : /^\d{8,15}$/.test(raw) ? `+${raw}` : null;
  if (!withPlus) return null;
  if (!/^\+[1-9]\d{7,14}$/.test(withPlus)) return null;
  return withPlus;
}

function detailMessage(body, fallback) {
  if (body == null) return fallback;
  if (typeof body === "string") return body;
  const detail = body.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc)
          ? item.loc.filter((p) => p !== "body" && p !== "query").join(".")
          : "";
        const msg = item?.msg || item?.message || JSON.stringify(item);
        return field ? `${field}: ${msg}` : msg;
      })
      .join("; ");
  }
  if (typeof body.message === "string") return body.message;
  try {
    return JSON.stringify(body);
  } catch {
    return fallback;
  }
}

function authHeaders() {
  try {
    const raw = localStorage.getItem("monjed_session");
    if (!raw) return {};
    const session = JSON.parse(raw);
    if (session?.access_token) {
      return { Authorization: `Bearer ${session.access_token}` };
    }
  } catch {
    /* ignore */
  }
  return {};
}

export async function request(path, { method = "GET", body, headers } = {}) {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  let response;
  try {
    response = await fetch(url, {
      method,
      headers: {
        Accept: "application/json",
        ...authHeaders(),
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  } catch (err) {
    throw new ApiError(
      "Cannot reach the MONJED API. Confirm the backend is running and CORS allows this origin.",
      { status: 0, body: { cause: err?.message } }
    );
  }

  const raw = await response.text();
  let parsed = null;
  if (raw) {
    try {
      parsed = JSON.parse(raw);
    } catch {
      parsed = raw;
    }
  }

  if (!response.ok) {
    throw new ApiError(detailMessage(parsed, response.statusText || "Request failed"), {
      status: response.status,
      body: parsed,
    });
  }

  return parsed;
}

export function get(path) {
  return request(path, { method: "GET" });
}

export function post(path, body) {
  return request(path, { method: "POST", body });
}

export function put(path, body) {
  return request(path, { method: "PUT", body });
}

export function patch(path, body) {
  return request(path, { method: "PATCH", body });
}

export function healthCheck() {
  return get("/health");
}

/** POST /risk/flood */
export function assessFloodRisk(payload) {
  return post("/risk/flood", payload);
}

/** POST /risk/earthquake */
export function assessEarthquakeRisk(payload) {
  return post("/risk/earthquake", payload);
}

/** POST /api/community-reports/analyze */
export function analyzeCommunityReport(payload) {
  return post("/api/community-reports/analyze", payload);
}

/** POST /api/community-reports/submit */
export function submitCommunityReport(payload) {
  return post("/api/community-reports/submit", payload);
}

/** GET /api/community-reports */
export function listCommunityReports(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.verified != null) q.set("verified", String(params.verified));
  if (params.resolved != null) q.set("resolved", String(params.resolved));
  const qs = q.toString();
  return get(`/api/community-reports${qs ? `?${qs}` : ""}`);
}

/** GET /api/community-reports/recent/{zone_id} */
export function recentCommunityReports(zoneId) {
  return get(`/api/community-reports/recent/${encodeURIComponent(zoneId)}`);
}

/** PATCH /api/community-reports/{id}/verify */
export function verifyCommunityReport(id) {
  return patch(`/api/community-reports/${encodeURIComponent(id)}/verify`);
}

/** PATCH /api/community-reports/{id}/resolve */
export function resolveCommunityReport(id) {
  return patch(`/api/community-reports/${encodeURIComponent(id)}/resolve`);
}

/** POST /auth/contact */
export function submitContact(payload) {
  return post("/auth/contact", payload);
}

/** Auth — POST /auth/register | /auth/login | /auth/admin */
export function registerUser(payload) {
  return post("/auth/register", payload);
}

export function loginUser(payload) {
  return post("/auth/login", payload);
}

export function loginAdmin(payload) {
  return post("/auth/admin", payload);
}

/** GET /users — platform directory for ops */
export function listPlatformUsers(params = {}) {
  const q = new URLSearchParams();
  if (params.role) q.set("role", params.role);
  if (params.zone_id) q.set("zone_id", params.zone_id);
  const qs = q.toString();
  return get(`/users${qs ? `?${qs}` : ""}`);
}

/** GET/PATCH /users/{user_id}/profile */
export function getUserProfile(userId) {
  return get(`/users/${encodeURIComponent(userId)}/profile`);
}

export function updateUserProfile(userId, payload) {
  return patch(`/users/${encodeURIComponent(userId)}/profile`, payload);
}

/** Assistance / volunteers */
export function registerVolunteer(payload) {
  return post("/assistance/volunteers", payload);
}

export function listVolunteers(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.available != null) q.set("available", String(params.available));
  const qs = q.toString();
  return get(`/assistance/volunteers${qs ? `?${qs}` : ""}`);
}

/** PATCH /assistance/volunteers/{id} body: { available } */
export function setVolunteerAvailability(volunteerId, available) {
  return patch(`/assistance/volunteers/${encodeURIComponent(volunteerId)}`, {
    available: Boolean(available),
  });
}

export function listVolunteerInbox(volunteerId) {
  return get(
    `/assistance/volunteers/${encodeURIComponent(volunteerId)}/requests`
  );
}

export function createAssistanceRequest(payload) {
  return post("/assistance/requests", payload);
}

export function listAssistanceRequests(params = {}) {
  const q = new URLSearchParams();
  if (params.status) q.set("status", params.status);
  const qs = q.toString();
  return get(`/assistance/requests${qs ? `?${qs}` : ""}`);
}

/** All help requests for the admin console. */
export function listAllAssistanceForOps() {
  return listAssistanceRequests();
}

export function listPendingAssistance() {
  return listAssistanceRequests({ status: "pending" });
}

export function getAssistanceRequest(id) {
  return get(`/assistance/requests/${encodeURIComponent(id)}`);
}

export function matchAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/match`);
}

export function startAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/start`);
}

export function resolveAssistanceRequest(id) {
  return post(`/assistance/requests/${encodeURIComponent(id)}/resolve`);
}

/** Dashboard */
export function dashboardOverview() {
  return get("/dashboard/overview");
}

export function dashboardRisks(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.hazard) q.set("hazard", params.hazard);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/risks${qs ? `?${qs}` : ""}`);
}

export function dashboardZone(zoneId) {
  return get(`/dashboard/zones/${encodeURIComponent(zoneId)}`);
}

export function dashboardAlerts(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/alerts${qs ? `?${qs}` : ""}`);
}

export function dashboardDecisions(params = {}) {
  const q = new URLSearchParams();
  if (params.zone_id) q.set("zone_id", params.zone_id);
  if (params.limit) q.set("limit", String(params.limit));
  const qs = q.toString();
  return get(`/dashboard/decisions${qs ? `?${qs}` : ""}`);
}

/** POST /pipeline/flood */
export function pipelineFlood(payload, accessibilityNeeds = []) {
  const q = new URLSearchParams();
  accessibilityNeeds.forEach((n) => q.append("accessibility_needs", n));
  const qs = q.toString();
  return post(`/pipeline/flood${qs ? `?${qs}` : ""}`, payload);
}

export const api = {
  get,
  post,
  patch,
  healthCheck,
  assessFloodRisk,
  assessEarthquakeRisk,
  analyzeCommunityReport,
  submitCommunityReport,
  listCommunityReports,
  recentCommunityReports,
  verifyCommunityReport,
  resolveCommunityReport,
  submitContact,
  registerUser,
  loginUser,
  loginAdmin,
  listPlatformUsers,
  getUserProfile,
  updateUserProfile,
  registerVolunteer,
  listVolunteers,
  setVolunteerAvailability,
  listVolunteerInbox,
  createAssistanceRequest,
  listAssistanceRequests,
  listPendingAssistance,
  matchAssistanceRequest,
  startAssistanceRequest,
  resolveAssistanceRequest,
  dashboardOverview,
  dashboardRisks,
  dashboardZone,
  dashboardAlerts,
  dashboardDecisions,
  pipelineFlood,
};

export default api;
