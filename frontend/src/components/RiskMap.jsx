import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import { feature } from "topojson-client";
import { useTheme } from "../lib/theme.jsx";
import "leaflet/dist/leaflet.css";

const GEO_URL =
  "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

/** ISO 3166-1 numeric → MONJED country code */
const ISO_TO_CODE = {
  404: "KE",
  706: "SO",
  231: "ET",
  508: "MZ",
  566: "NG",
  710: "ZA",
  504: "MA",
  818: "EG",
  288: "GH",
  834: "TZ",
  729: "SD",
  180: "CD",
};

const RISK_COLOR = {
  high: "#e11d48",
  medium: "#f59e0b",
  low: "#0d9488",
};

function riskColor(level) {
  return RISK_COLOR[level] ?? "#94a3b8";
}

function FlyToSelected({ country }) {
  const map = useMap();
  useEffect(() => {
    if (!country?.lat || !country?.lng) return;
    map.flyTo([country.lat, country.lng], 5.4, { duration: 0.75 });
  }, [country?.code, country?.lat, country?.lng, map]);
  return null;
}

/**
 * Clean OpenStreetMap basemap + real country borders tinted by risk.
 * Free — no API key.
 */
export default function RiskMap({
  countries,
  selected,
  onSelect,
  metric = "flood",
  className = "",
}) {
  const { isDark } = useTheme();
  const [geoFeatures, setGeoFeatures] = useState(null);

  const byCode = useMemo(
    () => Object.fromEntries(countries.map((c) => [c.code, c])),
    [countries]
  );

  useEffect(() => {
    let cancelled = false;
    fetch(GEO_URL)
      .then((r) => r.json())
      .then((topology) => {
        if (cancelled) return;
        const fc = feature(topology, topology.objects.countries);
        setGeoFeatures(fc.features);
      })
      .catch(() => {
        if (!cancelled) setGeoFeatures([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const styleFeature = (feat) => {
    const code = ISO_TO_CODE[Number(feat.id)];
    const country = code ? byCode[code] : null;
    if (!country) {
      return {
        fillColor: isDark ? "#1a2438" : "#e2e8f0",
        fillOpacity: isDark ? 0.35 : 0.28,
        color: isDark ? "#2a3548" : "#cbd5e1",
        weight: 0.6,
        opacity: 0.75,
      };
    }
    const level = country[metric];
    const color = riskColor(level);
    const isSelected = selected?.code === code;
    return {
      fillColor: color,
      fillOpacity: isSelected ? 0.58 : 0.4,
      color: isSelected ? (isDark ? "#e8eef8" : "#0f172a") : color,
      weight: isSelected ? 2 : 1,
      opacity: 0.95,
    };
  };

  const onEachFeature = (feat, layer) => {
    const code = ISO_TO_CODE[Number(feat.id)];
    const country = code ? byCode[code] : null;
    if (!country) {
      layer.options.interactive = false;
      return;
    }
    const score =
      metric === "flood" ? country.floodScore : country.quakeScore;
    layer.bindTooltip(
      `<strong>${country.name}</strong><br/>${
        metric === "flood" ? "Flood" : "Earthquake"
      }: ${String(country[metric]).toUpperCase()} · ${score}`,
      { sticky: true, opacity: 0.95 }
    );
    layer.on({
      click: () => onSelect(country),
      mouseover: (e) => {
        e.target.setStyle({ fillOpacity: 0.65, weight: 2 });
      },
      mouseout: (e) => {
        e.target.setStyle(styleFeature(feat));
      },
    });
  };

  const geoKey = `${metric}-${isDark ? "d" : "l"}-${countries.map((c) => c.code).join(",")}-${selected?.code || ""}`;

  const tileUrl = isDark
    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  return (
    <div
      className={`relative overflow-hidden rounded-lg border border-line monjed-risk-map ${className}`}
    >
      {geoFeatures === null && (
        <div className="absolute inset-0 z-[500] flex items-center justify-center bg-panel/80 font-mono text-xs text-slate">
          Loading map…
        </div>
      )}

      <MapContainer
        center={[2, 20]}
        zoom={3.5}
        minZoom={3}
        maxZoom={9}
        scrollWheelZoom
        className="h-[440px] w-full z-0"
        worldCopyJump={false}
        maxBounds={[
          [-38, -28],
          [42, 58],
        ]}
      >
        <TileLayer
          key={isDark ? "dark" : "light"}
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · &copy; <a href="https://carto.com/">CARTO</a>'
          url={tileUrl}
          subdomains="abcd"
        />

        <FlyToSelected country={selected} />

        {geoFeatures && geoFeatures.length > 0 && (
          <GeoJSON
            key={geoKey}
            data={{ type: "FeatureCollection", features: geoFeatures }}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}

        {/* Compact pins so tiny countries stay easy to hit */}
        {countries.map((c) => {
          const level = c[metric];
          const color = riskColor(level);
          const isSelected = selected?.code === c.code;
          const score = metric === "flood" ? c.floodScore : c.quakeScore;
          return (
            <CircleMarker
              key={c.code}
              center={[c.lat, c.lng]}
              radius={isSelected ? 7 : 4.5}
              pathOptions={{
                color: "#ffffff",
                weight: 1.5,
                fillColor: color,
                fillOpacity: 1,
              }}
              eventHandlers={{ click: () => onSelect(c) }}
            >
              <Tooltip direction="top" offset={[0, -4]} opacity={0.95}>
                <span className="font-mono text-[10px]">
                  {c.code} · {String(level).toUpperCase()} · {score}
                </span>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {geoFeatures && geoFeatures.length === 0 && (
        <p className="absolute bottom-2 left-2 right-2 z-[500] rounded bg-panel/95 px-2 py-1.5 font-mono text-[10px] text-crimson">
          Borders failed to load — pins still work. Check your connection.
        </p>
      )}
    </div>
  );
}

export { riskColor, RISK_COLOR };
