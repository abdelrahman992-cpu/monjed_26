/** Zone catalog for map/login — geometry + observation inputs for risk APIs.
 * Risk scores/levels are NOT hardcoded; they come from POST /risk/flood
 * and POST /risk/earthquake.
 */

export const ZONES = [
  {
    name: "Kenya",
    code: "KE",
    zone_id: "KE",
    region: "East Africa",
    lat: -0.02,
    lng: 37.91,
    floodObs: { rainfall_1h_mm: 18, rainfall_24h_mm: 95, previous_rainfall_24h_mm: 70 },
    quakeObs: { magnitude: 3.2, depth_km: 18, distance_km: 120 },
  },
  {
    name: "Somalia",
    code: "SO",
    zone_id: "SO",
    region: "East Africa",
    lat: 5.15,
    lng: 46.2,
    floodObs: { rainfall_1h_mm: 22, rainfall_24h_mm: 110, previous_rainfall_24h_mm: 85 },
    quakeObs: { magnitude: 2.8, depth_km: 22, distance_km: 200 },
  },
  {
    name: "Ethiopia",
    code: "ET",
    zone_id: "ET",
    region: "East Africa",
    lat: 9.15,
    lng: 40.49,
    floodObs: { rainfall_1h_mm: 4, rainfall_24h_mm: 18, previous_rainfall_24h_mm: 12 },
    quakeObs: { magnitude: 5.1, depth_km: 12, distance_km: 80 },
  },
  {
    name: "Mozambique",
    code: "MZ",
    zone_id: "MZ",
    region: "Southern Africa",
    lat: -18.67,
    lng: 35.53,
    floodObs: { rainfall_1h_mm: 16, rainfall_24h_mm: 88, previous_rainfall_24h_mm: 60 },
    quakeObs: { magnitude: 2.5, depth_km: 25, distance_km: 250 },
  },
  {
    name: "Nigeria",
    code: "NG",
    zone_id: "NG",
    region: "West Africa",
    lat: 9.08,
    lng: 8.68,
    floodObs: { rainfall_1h_mm: 10, rainfall_24h_mm: 45, previous_rainfall_24h_mm: 40 },
    quakeObs: { magnitude: 4.6, depth_km: 15, distance_km: 90 },
  },
  {
    name: "South Africa",
    code: "ZA",
    zone_id: "ZA",
    region: "Southern Africa",
    lat: -30.56,
    lng: 22.94,
    floodObs: { rainfall_1h_mm: 2, rainfall_24h_mm: 12, previous_rainfall_24h_mm: 8 },
    quakeObs: { magnitude: 2.2, depth_km: 30, distance_km: 300 },
  },
  {
    name: "Morocco",
    code: "MA",
    zone_id: "MA",
    region: "North Africa",
    lat: 31.79,
    lng: -7.09,
    floodObs: { rainfall_1h_mm: 3, rainfall_24h_mm: 15, previous_rainfall_24h_mm: 10 },
    quakeObs: { magnitude: 6.2, depth_km: 10, distance_km: 40 },
  },
  {
    name: "Egypt",
    code: "EG",
    zone_id: "EG",
    region: "North Africa",
    lat: 26.82,
    lng: 30.8,
    floodObs: { rainfall_1h_mm: 1, rainfall_24h_mm: 8, previous_rainfall_24h_mm: 5 },
    quakeObs: { magnitude: 4.4, depth_km: 20, distance_km: 110 },
  },
  {
    name: "Ghana",
    code: "GH",
    zone_id: "GH",
    region: "West Africa",
    lat: 7.95,
    lng: -1.02,
    floodObs: { rainfall_1h_mm: 9, rainfall_24h_mm: 42, previous_rainfall_24h_mm: 35 },
    quakeObs: { magnitude: 2.4, depth_km: 28, distance_km: 280 },
  },
  {
    name: "Tanzania",
    code: "TZ",
    zone_id: "TZ",
    region: "East Africa",
    lat: -6.37,
    lng: 34.89,
    floodObs: { rainfall_1h_mm: 12, rainfall_24h_mm: 55, previous_rainfall_24h_mm: 48 },
    quakeObs: { magnitude: 3.5, depth_km: 16, distance_km: 150 },
  },
  {
    name: "Sudan",
    code: "SD",
    zone_id: "SD",
    region: "East Africa",
    lat: 12.86,
    lng: 30.22,
    floodObs: { rainfall_1h_mm: 15, rainfall_24h_mm: 80, previous_rainfall_24h_mm: 65 },
    quakeObs: { magnitude: 3.0, depth_km: 22, distance_km: 180 },
  },
  {
    name: "DR Congo",
    code: "CD",
    zone_id: "CD",
    region: "Central Africa",
    lat: -4.04,
    lng: 21.76,
    floodObs: { rainfall_1h_mm: 11, rainfall_24h_mm: 50, previous_rainfall_24h_mm: 44 },
    quakeObs: { magnitude: 4.8, depth_km: 14, distance_km: 70 },
  },
];

export function zoneByCode(code) {
  const c = String(code || "").toUpperCase();
  return ZONES.find((z) => z.code === c || z.zone_id === c) || ZONES[0];
}

/** Map API risk_level → map color key used by RiskMap / badges */
export function mapLevel(apiLevel) {
  const n = String(apiLevel || "low").toLowerCase();
  if (n === "critical" || n === "high") return n === "critical" ? "high" : "high";
  if (n === "moderate" || n === "medium") return "medium";
  return "low";
}
