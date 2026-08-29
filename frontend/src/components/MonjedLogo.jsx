/**
 * MONJED wordmark + signal mark.
 * @param {"sm"|"md"|"lg"|"xl"} size
 * @param {"light"|"dark"|"inherit"} tone — light = white text (hero), dark = ink, inherit = current
 */
export default function MonjedLogo({
  size = "md",
  tone = "inherit",
  className = "",
  showWordmark = true,
}) {
  const dims = {
    sm: { mark: 28, text: "text-lg", gap: "gap-2" },
    md: { mark: 36, text: "text-xl", gap: "gap-2.5" },
    lg: { mark: 48, text: "text-3xl sm:text-4xl", gap: "gap-3" },
    xl: { mark: 56, text: "text-4xl sm:text-5xl", gap: "gap-3.5" },
  }[size];

  const textTone =
    tone === "light"
      ? "text-white"
      : tone === "dark"
        ? "text-bone"
        : "text-current";

  return (
    <span
      className={`inline-flex items-center ${dims.gap} ${className}`}
      aria-label="MONJED"
    >
      <img
        src="/logo.svg"
        alt=""
        width={dims.mark}
        height={dims.mark}
        className="shrink-0"
        decoding="async"
      />
      {showWordmark ? (
        <span
          className={`font-display font-bold tracking-tight leading-none ${dims.text} ${textTone}`}
        >
          MONJED
        </span>
      ) : null}
    </span>
  );
}
