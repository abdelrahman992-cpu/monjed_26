import { useState } from "react";
import { Lock, Eye, EyeOff } from "lucide-react";

export default function PasswordField({
  label,
  value,
  onChange,
  placeholder,
  ...props
}) {
  const [show, setShow] = useState(false);
  return (
    <label className="block">
      <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">
        {label}
      </span>
      <span className="relative flex items-center">
        <Lock size={15} className="absolute left-3 text-slate" />
        <input
          type={show ? "text" : "password"}
          placeholder={placeholder}
          className="w-full rounded-md border border-line bg-panel py-2.5 pl-9 pr-9 text-sm text-bone placeholder:text-muted focus:outline-none focus:border-amber transition-colors"
          {...(value !== undefined ? { value, onChange } : { onChange })}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          className="absolute right-3 text-slate hover:text-bone focus:outline-none"
          aria-label={show ? "Hide password" : "Show password"}
        >
          {show ? <EyeOff size={15} /> : <Eye size={15} />}
        </button>
      </span>
    </label>
  );
}
