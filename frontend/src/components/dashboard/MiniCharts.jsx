/** Lightweight SVG charts for dashboard overview panels (no chart library). */

export function DonutChart({ segments, size = 132, thickness = 18, centerLabel, centerValue }) {
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  let offset = 0;
  const total = segments.reduce((s, seg) => s + seg.value, 0) || 1;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={thickness}
          className="text-line"
        />
        {segments.map((seg) => {
          const len = (seg.value / total) * c;
          const dash = `${len} ${c - len}`;
          const el = (
            <circle
              key={seg.label}
              cx={size / 2}
              cy={size / 2}
              r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth={thickness}
              strokeDasharray={dash}
              strokeDashoffset={-offset}
              strokeLinecap="butt"
            />
          );
          offset += len;
          return el;
        })}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
        {centerValue != null && (
          <span className="font-display text-2xl font-bold tabular-nums leading-none">
            {centerValue}
          </span>
        )}
        {centerLabel && (
          <span className="mt-1 font-mono text-[9px] tracking-wide text-slate uppercase">
            {centerLabel}
          </span>
        )}
      </div>
    </div>
  );
}

export function BarChart({ rows, max = null, height = 160 }) {
  const peak = max ?? Math.max(1, ...rows.map((r) => r.value));
  return (
    <div className="w-full" style={{ height }}>
      <div className="flex h-full items-end gap-2">
        {rows.map((row) => {
          const pct = Math.max(4, (row.value / peak) * 100);
          return (
            <div key={row.label} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
              <span className="font-mono text-[10px] text-mist tabular-nums">{row.value}</span>
              <div
                className="w-full rounded-t-md transition-[height] duration-500 ease-out"
                style={{
                  height: `${pct}%`,
                  background: row.color || "var(--color-amber)",
                  opacity: 0.9,
                }}
                title={`${row.label}: ${row.value}`}
              />
              <span className="font-mono text-[9px] text-slate truncate w-full text-center">
                {row.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function SparkBars({ values, color = "var(--color-teal)" }) {
  const peak = Math.max(1, ...values);
  return (
    <div className="flex items-end gap-0.5 h-10">
      {values.map((v, i) => (
        <div
          key={i}
          className="flex-1 rounded-sm min-w-[3px]"
          style={{
            height: `${Math.max(8, (v / peak) * 100)}%`,
            background: color,
            opacity: 0.35 + (v / peak) * 0.65,
          }}
        />
      ))}
    </div>
  );
}

export function Legend({ items }) {
  return (
    <ul className="space-y-1.5">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-2 text-xs text-mist">
          <span
            className="h-2.5 w-2.5 rounded-sm shrink-0"
            style={{ background: item.color }}
          />
          <span className="flex-1 truncate">{item.label}</span>
          <span className="font-mono tabular-nums text-slate">{item.value}</span>
        </li>
      ))}
    </ul>
  );
}
