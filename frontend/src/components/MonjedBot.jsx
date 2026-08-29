/**
 * Lightweight CSS robot mascot using the MONJED mark as the face.
 * Pure CSS motion — no heavy animation libraries.
 */
export default function MonjedBot({ className = "", reduced = false }) {
  return (
    <div
      className={`relative mx-auto w-full max-w-[280px] select-none ${className}`}
      aria-hidden="true"
    >
      {/* Soft glow */}
      <div className="pointer-events-none absolute inset-x-8 bottom-2 h-10 rounded-full bg-amber/20 blur-2xl" />

      <div
        className={`relative flex flex-col items-center ${
          reduced ? "" : "animate-[bot-float_4.5s_ease-in-out_infinite]"
        }`}
      >
        {/* Antenna */}
        <div className="relative mb-1 flex flex-col items-center">
          <span
            className={`h-2.5 w-2.5 rounded-full bg-teal shadow-[0_0_10px_rgba(45,212,191,0.7)] ${
              reduced ? "" : "animate-pulse"
            }`}
          />
          <span className="h-5 w-0.5 bg-line" />
        </div>

        {/* Head */}
        <div className="relative z-10 flex h-28 w-28 items-center justify-center rounded-[1.75rem] border border-line bg-panel shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
          <div
            className={`absolute inset-2 rounded-[1.35rem] border border-amber/20 ${
              reduced ? "" : "animate-[bot-pulse-ring_3.2s_ease-in-out_infinite]"
            }`}
          />
          <img
            src="/logo.svg"
            alt=""
            width={64}
            height={64}
            className="relative z-10 drop-shadow-sm"
            decoding="async"
          />
          {/* Side ears */}
          <span className="absolute -left-2 top-1/2 h-8 w-2 -translate-y-1/2 rounded-full bg-raised border border-line" />
          <span className="absolute -right-2 top-1/2 h-8 w-2 -translate-y-1/2 rounded-full bg-raised border border-line" />
        </div>

        {/* Neck */}
        <div className="h-3 w-8 rounded-b-md bg-raised border-x border-b border-line" />

        {/* Body */}
        <div className="relative mt-0.5 w-40 rounded-2xl border border-line bg-panel px-4 py-5">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full border border-amber/30 bg-amber/10">
            <span
              className={`h-2 w-2 rounded-full bg-amber ${
                reduced ? "" : "animate-ping"
              }`}
            />
          </div>
          <div className="mt-3 flex justify-center gap-1.5">
            <span className="h-1.5 w-6 rounded-full bg-line" />
            <span className="h-1.5 w-4 rounded-full bg-teal/50" />
            <span className="h-1.5 w-5 rounded-full bg-line" />
          </div>
          {/* Arms */}
          <span
            className={`absolute -left-7 top-4 h-16 w-3.5 origin-top rounded-full border border-line bg-raised ${
              reduced ? "" : "animate-[bot-wave_2.8s_ease-in-out_infinite]"
            }`}
          />
          <span
            className={`absolute -right-7 top-4 h-16 w-3.5 origin-top rounded-full border border-line bg-raised ${
              reduced ? "" : "animate-[bot-wave_2.8s_ease-in-out_infinite_reverse]"
            }`}
          />
        </div>

        {/* Legs */}
        <div className="mt-1 flex gap-6">
          <span className="h-10 w-4 rounded-b-lg border border-line bg-raised" />
          <span className="h-10 w-4 rounded-b-lg border border-line bg-raised" />
        </div>
      </div>

      <p className="mt-4 text-center font-mono text-[10px] tracking-[0.16em] text-slate">
        MONJED · ACTION LAYER
      </p>
    </div>
  );
}
