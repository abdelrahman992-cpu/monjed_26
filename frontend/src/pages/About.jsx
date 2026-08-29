import { Link } from "react-router-dom";
import { ArrowRight, Radio, ShieldCheck, Users, Waves } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 sm:px-8 py-10 pb-16">
      <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
        ABOUT MONJED
      </p>
      <h1 className="mt-3 font-display text-3xl sm:text-4xl font-bold">
        Early warning that stays human
      </h1>
      <p className="mt-4 text-mist leading-relaxed">
        MONJED is a pan-African early-warning platform for flood and earthquake
        risk. Flood and earthquake scores are never blended into one index. When
        a warning alone is not enough, people can report ground conditions and
        request help — and volunteers who opt in can be matched by operations.
      </p>

      <div className="mt-10 grid sm:grid-cols-2 gap-4">
        {[
          {
            icon: Waves,
            t: "Explainable flood risk",
            d: "Rule-based scoring from rainfall, soil moisture, and trend — with plain reasons.",
          },
          {
            icon: Radio,
            t: "Ground truth",
            d: "Community reports and help requests feed ops with what satellites cannot see.",
          },
          {
            icon: Users,
            t: "Volunteer network",
            d: "Skills, vehicles, and private assignment inboxes — no fake dispatch.",
          },
          {
            icon: ShieldCheck,
            t: "Alerts that reach phones",
            d: "Accounts let us reach people where they live — Africa's Talking SMS later.",
          },
        ].map((item) => (
          <div
            key={item.t}
            className="rounded-xl border border-line bg-panel/50 p-5"
          >
            <item.icon size={20} className="text-amber" strokeWidth={1.75} />
            <h2 className="mt-3 font-display font-bold">{item.t}</h2>
            <p className="mt-2 text-sm text-slate leading-relaxed">{item.d}</p>
          </div>
        ))}
      </div>

      <p className="mt-10 text-sm text-slate leading-relaxed">
        Want to partner, report a technical issue, or ask for extra support?{" "}
        <Link to="/contact" className="text-amber hover:underline inline-flex items-center gap-1">
          Contact us <ArrowRight size={14} />
        </Link>
      </p>
    </div>
  );
}
