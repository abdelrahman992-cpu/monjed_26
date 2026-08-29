export default function TextField({ label, icon: Icon, type = "text", ...props }) {
  return (
    <label className="block">
      <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">
        {label}
      </span>
      <span className="relative flex items-center">
        {Icon && <Icon size={15} className="absolute left-3 text-slate" />}
        <input
          type={type}
          className={`w-full rounded-md border border-line bg-panel py-2.5 text-sm text-bone placeholder:text-muted focus:outline-none focus:border-amber transition-colors ${
            Icon ? "pl-9 pr-3" : "px-3"
          }`}
          {...props}
        />
      </span>
    </label>
  );
}
