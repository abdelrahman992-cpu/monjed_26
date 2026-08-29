/** Session storage + local ops inbox helpers used by staff dashboards. */

const SESSION_KEY = "monjed_session";
const USERS_KEY = "monjed_volunteers";
const REPORTS_KEY = "monjed_reports";
const HELP_KEY = "monjed_help_requests";
const VOLUNTEER_LINK_KEY = "monjed_volunteer_links";

export function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function writeJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getSession() {
  return readJson(SESSION_KEY, null);
}

export function setSession(session) {
  writeJson(SESSION_KEY, session);
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

/** Remember auth user_id → assistance volunteer_id after volunteer signup. */
export function linkVolunteerId(userId, volunteerId) {
  if (!userId || !volunteerId) return;
  const map = readJson(VOLUNTEER_LINK_KEY, {});
  map[userId] = volunteerId;
  writeJson(VOLUNTEER_LINK_KEY, map);
}

export function getLinkedVolunteerId(userId) {
  if (!userId) return null;
  const map = readJson(VOLUNTEER_LINK_KEY, {});
  return map[userId] || null;
}

/**
 * Map AuthResponse (or bare user) → frontend session shape.
 * Backend roles: citizen | volunteer | admin
 */
export function toClientSession(apiPayload, extras = {}) {
  const auth =
    apiPayload?.user && apiPayload?.access_token
      ? apiPayload
      : null;
  const u = auth?.user || apiPayload || {};

  return {
    access_token: auth?.access_token || apiPayload?.access_token || extras.access_token || "",
    role: u.role || apiPayload?.role || "citizen",
    id: u.user_id || u.id || apiPayload?.volunteer_id || apiPayload?.user_id || "",
    name: u.display_name || u.name || "",
    phone: u.phone || "",
    email: u.email || u.work_email || "",
    organization: u.organization || "",
    title: u.role_title || u.title || "",
    zone_id: u.zone_id || "",
    country: u.country || "",
    countryCode: u.country_code || u.countryCode || u.zone_id || "",
    zone: u.zone || "",
    preferred_language: u.preferred_language || "en",
    notification_consent: u.notification_consent,
    accessibility_needs: u.accessibility_needs || [],
    available: apiPayload?.available ?? extras.available,
    vehicleType: apiPayload?.vehicle_type || apiPayload?.vehicleType || extras.vehicleType,
    capacity: apiPayload?.capacity ?? extras.capacity,
    skills: apiPayload?.skills || extras.skills || [],
    volunteer_id:
      extras.volunteer_id ||
      apiPayload?.volunteer_id ||
      getLinkedVolunteerId(u.user_id || u.id) ||
      null,
    ...extras,
  };
}

/** Map UserProfileResponse into current session fields. */
export function applyProfileToSession(session, profile) {
  if (!session || !profile) return session;
  return {
    ...session,
    name: profile.display_name || session.name,
    phone: profile.phone || session.phone,
    email: profile.work_email || profile.email || session.email,
    organization: profile.organization || session.organization,
    title: profile.role_title || session.title,
    zone_id: profile.zone_id || session.zone_id,
    country: profile.country || session.country,
    preferred_language: profile.preferred_language || session.preferred_language,
    notification_consent: profile.notification_consent,
    accessibility_needs: profile.accessibility_needs || [],
  };
}

export function listVolunteers() {
  return readJson(USERS_KEY, []);
}

export function listReports() {
  return readJson(REPORTS_KEY, []);
}

export function addReport(report) {
  const next = [{ ...report, id: `rep-${Date.now()}` }, ...listReports()];
  writeJson(REPORTS_KEY, next);
  return next[0];
}

export function patchReport(id, patch) {
  const next = listReports().map((r) => (r.id === id ? { ...r, ...patch } : r));
  writeJson(REPORTS_KEY, next);
  return next;
}

export function listHelpRequests() {
  return readJson(HELP_KEY, []);
}

export function addHelpRequest(request) {
  const next = [{ ...request, id: `help-${Date.now()}` }, ...listHelpRequests()];
  writeJson(HELP_KEY, next);
  return next[0];
}

export function patchHelpRequest(id, patch) {
  const next = listHelpRequests().map((r) =>
    r.id === id ? { ...r, ...patch } : r
  );
  writeJson(HELP_KEY, next);
  return next;
}
