import { useState } from "react";
import { CheckCircle2, Mail, MessageSquare, Building2 } from "lucide-react";
import TextField from "../components/ui/TextField.jsx";
import { submitContact, ApiError, toE164 } from "../lib/api.js";

const TOPICS = [
  { id: "technical", label: "Technical error", icon: MessageSquare },
  { id: "help", label: "Extra help", icon: Mail },
  { id: "partner", label: "Partnership", icon: Building2 },
];

export default function ContactPage() {
  const [topic, setTopic] = useState("technical");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const data = new FormData(e.target);
    try {
      const phoneRaw = String(data.get("phone") || "").trim();
      await submitContact({
        name: String(data.get("name") || "").trim(),
        email: String(data.get("email") || "").trim(),
        phone: toE164(phoneRaw) || undefined,
        subject: TOPICS.find((t) => t.id === topic)?.label || topic,
        message: String(data.get("message") || "").trim(),
      });
      setSent(true);
      e.target.reset();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not send message.");
    } finally {
      setBusy(false);
    }
  }

  if (sent) {
    return (
      <div className="mx-auto max-w-lg px-5 sm:px-8 py-16 text-center">
        <CheckCircle2 size={36} className="mx-auto text-teal" />
        <h1 className="mt-4 font-display text-2xl font-bold">Message received</h1>
        <p className="mt-2 text-sm text-slate leading-relaxed">
          Thanks — we will follow up using the contact details you shared.
          Your message was sent to the MONJED backend inbox.
        </p>
        <button
          type="button"
          onClick={() => setSent(false)}
          className="mt-6 text-sm text-amber hover:underline"
        >
          Send another message
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg px-5 sm:px-8 py-10 pb-16">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        CONTACT US
      </p>
      <h1 className="mt-3 font-display text-3xl font-bold">Get in touch</h1>
      <p className="mt-2 text-sm text-slate leading-relaxed">
        Technical problems, extra support, or partnership ideas — tell us what
        you need.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        {TOPICS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTopic(t.id)}
            className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-mono ${
              topic === t.id
                ? "border-amber bg-amber/10 text-bone"
                : "border-line text-slate"
            }`}
          >
            <t.icon size={12} />
            {t.label}
          </button>
        ))}
      </div>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <TextField label="Your name" name="name" required minLength={2} />
        <TextField
          label="Email"
          name="email"
          type="email"
          required
          placeholder="you@example.com"
        />
        <TextField
          label="Phone (optional)"
          name="phone"
          type="tel"
          placeholder="+2547XXXXXXXX"
        />
        <label className="block">
          <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">
            Message
          </span>
          <textarea
            name="message"
            required
            rows={5}
            minLength={5}
            className="w-full rounded-md border border-line bg-panel px-3 py-2.5 text-sm leading-relaxed focus:outline-none focus:border-amber"
            placeholder="Describe the issue, or how you’d like to partner…"
          />
        </label>
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-md bg-amber px-4 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright disabled:opacity-60"
        >
          {busy ? "Sending…" : "Send message"}
        </button>
      </form>
    </div>
  );
}
