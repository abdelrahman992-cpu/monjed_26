/** Known East Africa towns for volunteer base GPS (approx city centers). */
export const PLACES = [
  { name: "Kisumu", country: "KE", lat: -0.0917, lng: 34.768 },
  { name: "Nairobi", country: "KE", lat: -1.2864, lng: 36.8172 },
  { name: "Mombasa", country: "KE", lat: -4.0435, lng: 39.6682 },
  { name: "Nakuru", country: "KE", lat: -0.3031, lng: 36.08 },
  { name: "Eldoret", country: "KE", lat: 0.5143, lng: 35.2698 },
  { name: "Meru", country: "KE", lat: 0.0463, lng: 37.6559 },
  { name: "Nyeri", country: "KE", lat: -0.4197, lng: 36.9476 },
  { name: "Kakamega", country: "KE", lat: 0.2827, lng: 34.7519 },
  { name: "Kisii", country: "KE", lat: -0.6817, lng: 34.7667 },
  { name: "Malindi", country: "KE", lat: -3.2175, lng: 40.1191 },
  { name: "Garissa", country: "KE", lat: -0.4532, lng: 39.6461 },
  { name: "Kitale", country: "KE", lat: 1.0157, lng: 35.0062 },
  { name: "Thika", country: "KE", lat: -1.0333, lng: 37.0693 },
  { name: "Lamu", country: "KE", lat: -2.2717, lng: 40.902 },
  { name: "Kampala", country: "UG", lat: 0.3476, lng: 32.5825 },
  { name: "Mogadishu", country: "SO", lat: 2.0469, lng: 45.3182 },
  { name: "Addis Ababa", country: "ET", lat: 9.03, lng: 38.74 },
  { name: "Dar es Salaam", country: "TZ", lat: -6.7924, lng: 39.2083 },
];

/**
 * Resolve a town/area string to coordinates.
 * Prefers exact/starts-with match within optional country code.
 */
export function resolvePlace(query, countryCode = null) {
  const q = String(query || "")
    .trim()
    .toLowerCase();
  if (!q) return null;

  const country = countryCode
    ? String(countryCode).trim().toUpperCase()
    : null;

  const pool = country
    ? PLACES.filter((p) => p.country === country)
    : PLACES;

  const exact = pool.find((p) => p.name.toLowerCase() === q);
  if (exact) return exact;

  const starts = pool.find(
    (p) =>
      p.name.toLowerCase().startsWith(q) ||
      q.startsWith(p.name.toLowerCase())
  );
  if (starts) return starts;

  const includes = pool.find(
    (p) =>
      p.name.toLowerCase().includes(q) || q.includes(p.name.toLowerCase())
  );
  return includes || null;
}

/** Kenya country centroid is misleading (near Meru). Prefer Nairobi as KE default. */
export const ZONE_DEFAULTS = {
  KE: { name: "Nairobi", lat: -1.2864, lng: 36.8172 },
  UG: { name: "Kampala", lat: 0.3476, lng: 32.5825 },
  SO: { name: "Mogadishu", lat: 2.0469, lng: 45.3182 },
  ET: { name: "Addis Ababa", lat: 9.03, lng: 38.74 },
  TZ: { name: "Dar es Salaam", lat: -6.7924, lng: 39.2083 },
};
