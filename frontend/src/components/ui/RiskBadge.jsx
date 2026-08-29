export default function RiskBadge({ level = "low" }) {
  const normalized = String(level || "low").toLowerCase();
  const key =
    normalized === "moderate"
      ? "medium"
      : normalized === "critical"
        ? "critical"
        : normalized;

  // Risk colors stay semantic (not brand blue)
  const styles = {
    high: "bg-[#E11D48]/12 text-[#BE123C] border-[#E11D48]/35",
    critical: "bg-[#E11D48]/18 text-[#9F1239] border-[#E11D48]/45",
    medium: "bg-[#F59E0B]/15 text-[#B45309] border-[#F59E0B]/40",
    low: "bg-[#0D9488]/12 text-[#0F766E] border-[#0D9488]/35",
  };

  const labels = {
    high: "HIGH",
    critical: "CRITICAL",
    medium: "MEDIUM",
    low: "LOW",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded font-mono text-[10px] tracking-wider border uppercase ${
        styles[key] || styles.low
      }`}
    >
      {labels[key] || labels.low}
    </span>
  );
}
