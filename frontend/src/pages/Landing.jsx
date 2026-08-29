import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Radio,
  Waves,
  Mountain,
  MessageSquare,
  Users,
  LifeBuoy,
  ShieldCheck,
  Languages,
  Activity,
  Menu,
  X,
  Route,
  Car,
  Siren,
  CheckCircle2,
  ChevronDown,
} from "lucide-react";
import RiskBadge from "../components/ui/RiskBadge.jsx";
import ThemeToggle from "../components/ThemeToggle.jsx";
import MonjedLogo from "../components/MonjedLogo.jsx";
import MonjedBot from "../components/MonjedBot.jsx";
import { COUNTRIES } from "../data/mockRisk.js";
import { useAuth } from "../lib/auth.jsx";

const AFRICA_CLIP =
  "polygon(36.7% 2.9%, 50% 4.4%, 63.3% 11.8%, 71.7% 20.6%, 85% 27.9%, 76.7% 38.2%, 71.7% 47.1%, 66.7% 55.9%, 65% 67.6%, 58.3% 79.4%, 50% 91.2%, 43.3% 98.5%, 36.7% 91.2%, 31.7% 79.4%, 26.7% 67.6%, 23.3% 55.9%, 18.3% 44.1%, 13.3% 35.3%, 18.3% 27.9%, 25% 20.6%, 23.3% 11.8%, 30% 5.9%)";

const NODES = [
  { name: "Morocco", x: 25, y: 15, level: "low" },
  { name: "Algeria", x: 36, y: 21, level: "low" },
  { name: "Egypt", x: 60, y: 15, level: "medium" },
  { name: "Sudan", x: 60, y: 30, level: "low" },
  { name: "Ethiopia", x: 72, y: 35, level: "medium" },
  { name: "Somalia", x: 80, y: 33, level: "high" },
  { name: "Nigeria", x: 30, y: 45, level: "medium" },
  { name: "Ghana", x: 22, y: 49, level: "low" },
  { name: "DR Congo", x: 45, y: 58, level: "low" },
  { name: "Kenya", x: 65, y: 49, level: "high" },
  { name: "Tanzania", x: 62, y: 59, level: "low" },
  { name: "Zambia", x: 50, y: 71, level: "low" },
  { name: "Mozambique", x: 60, y: 76, level: "high" },
  { name: "South Africa", x: 45, y: 90, level: "low" },
];

const LEVEL_COLOR = {
  low: "#0D9488",
  medium: "#F59E0B",
  high: "#E11D48",
};

function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const fn = (e) => setReduced(e.matches);
    mq.addEventListener?.("change", fn);
    return () => mq.removeEventListener?.("change", fn);
  }, []);
  return reduced;
}

function useReveal() {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          obs.unobserve(el);
        }
      },
      { threshold: 0.12 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return [ref, inView];
}

function Reveal({ children, className = "", delay = 0 }) {
  const [ref, inView] = useReveal();
  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
      } ${className}`}
      style={{ transitionDelay: inView ? `${delay}ms` : "0ms" }}
    >
      {children}
    </div>
  );
}

function PulseMap({ reduced }) {
  return (
    <div className="relative w-full aspect-[300/340] max-w-[360px] mx-auto select-none">
      <div
        className="absolute inset-0 bg-[#0B1F3A]"
        style={{ clipPath: AFRICA_CLIP }}
      />
      <div
        className="absolute inset-0 opacity-[0.9]"
        style={{
          clipPath: AFRICA_CLIP,
          backgroundImage:
            "linear-gradient(rgba(59,130,246,0.18) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.18) 1px, transparent 1px)",
          backgroundSize: "10% 10%",
        }}
      />
      {!reduced && (
        <div
          className="absolute inset-0 origin-center animate-[spin_7s_linear_infinite]"
          style={{ clipPath: AFRICA_CLIP }}
        >
          <div
            className="w-full h-full"
            style={{
              background:
                "conic-gradient(from 0deg, rgba(59,130,246,0.55), transparent 28%, transparent 100%)",
            }}
          />
        </div>
      )}
      {NODES.map((n) => (
        <div
          key={n.name}
          className="absolute -translate-x-1/2 -translate-y-1/2 group"
          style={{ left: `${n.x}%`, top: `${n.y}%` }}
        >
          {!reduced && (n.level === "high" || n.level === "medium") && (
            <span
              className="absolute inset-0 rounded-full animate-ping"
              style={{
                backgroundColor: LEVEL_COLOR[n.level],
                opacity: 0.35,
                animationDuration: n.level === "high" ? "1.4s" : "2.4s",
              }}
            />
          )}
          <span
            className="relative block rounded-full ring-1 ring-white/30"
            style={{
              width: n.level === "high" ? 9 : 6,
              height: n.level === "high" ? 9 : 6,
              backgroundColor: LEVEL_COLOR[n.level],
            }}
          />
          <span className="pointer-events-none absolute left-1/2 -translate-x-1/2 top-full mt-1.5 whitespace-nowrap text-[9px] font-mono tracking-wide text-white/70 opacity-0 group-hover:opacity-100 transition-opacity">
            {n.name.toUpperCase()}
          </span>
        </div>
      ))}
    </div>
  );
}

function Ticker({ reduced }) {
  const items = [
    "KE — FLOOD HIGH · 3-DAY RAINFALL 12.1MM · QUAKE LOW",
    "SO — FLOOD HIGH · CUMULATIVE 94MM · QUAKE LOW",
    "ET — QUAKE MEDIUM · 2 EVENTS / 30D · FLOOD LOW",
    "MZ — FLOOD HIGH · INCREASING TREND · QUAKE LOW",
    "NG — FLOOD MEDIUM · QUAKE MEDIUM · M3.8 LOGGED",
    "ZA — ALL HAZARDS LOW · NO ELEVATED SIGNAL",
  ];
  const line = items.join("    ·    ");
  return (
    <div className="relative overflow-hidden border-t border-white/15 bg-[#0b1220]/75 py-2.5 backdrop-blur-sm">
      <div
        className={`flex whitespace-nowrap font-mono text-[11px] tracking-wide text-white/55 ${
          reduced ? "" : "animate-ticker"
        }`}
      >
        <span className="px-4">{line}</span>
        <span className="px-4">{line}</span>
      </div>
    </div>
  );
}

const STEPS = [
  {
    n: "01",
    t: "Live signals",
    d: "Rainfall and soil inputs feed the flood engine. Earthquake activity is tracked on a separate path so one hazard never hides the other.",
  },
  {
    n: "02",
    t: "Explainable score",
    d: "Rule-based scoring returns 0–100, a level, and plain reasons — heavy rain, saturated soil, rising trend — not a black-box probability.",
  },
  {
    n: "03",
    t: "Ground truth",
    d: "Typed reports confirm or contradict the alert. Optional notes go to the live analyze API for severity and evidence flags.",
  },
  {
    n: "04",
    t: "Human when stuck",
    d: "If the recommended action is not realistic — blocked road, no transport — a volunteer in that zone can take the request privately.",
  },
];

const REPORT_TYPES = [
  {
    key: "WATER RISING",
    icon: Waves,
    d: "Cross-checks the flood engine. Repeated reports in one zone raise confidence; a single tap does not override the score.",
  },
  {
    key: "ROAD BLOCKED",
    icon: Route,
    d: "Feasibility flag. If this clusters under an active flood alert, responders annotate: verify the route before travel.",
  },
  {
    key: "NEED HELP",
    icon: Siren,
    d: "Opens a public help request. Nearby volunteers only see it after they sign in — we do not invent a dispatch from this page.",
  },
  {
    key: "NO TRANSPORT",
    icon: Car,
    d: "Matches volunteers who registered a vehicle. Mobility assistance is tracked as a separate need, not the same as transport.",
  },
  {
    key: "I AM SAFE",
    icon: CheckCircle2,
    d: "Closes the loop for responders. Safe check-ins are logged but never used to silently cancel an alert.",
  },
];

const ALERTS = {
  EN: {
    lang: "English",
    body: "HIGH flood risk, western Kenya. Rain has been climbing for three days. If water is already on the road, do not wait for a second message — move to higher ground. If you cannot move, reply NEED HELP. This is not an earthquake alert.",
  },
  SW: {
    lang: "Kiswahili",
    body: "Hatari KUBWA ya mafuriko, magharibi mwa Kenya. Mvua imeongezeka kwa siku tatu. Ikiwa barabara imefunikwa maji, usisubiri ujumbe wa pili — nenda sehemu ya juu. Usipoweza kusogea, jibu NEED HELP. Hii si tahadhari ya tetemeko.",
  },
  FR: {
    lang: "Français",
    body: "Risque ÉLEVÉ d’inondation, ouest du Kenya. La pluie augmente depuis trois jours. Si la route est déjà sous l’eau, n’attendez pas un second message — gagnez un terrain plus élevé. Si vous ne pouvez pas bouger, répondez NEED HELP. Ceci n’est pas une alerte sismique.",
  },
  AR: {
    lang: "العربية",
    body: "خطر فيضان مرتفع غرب كينيا. الأمطار في تصاعد منذ ثلاثة أيام. إذا كان الطريق مغموراً فلا تنتظر رسالة ثانية — انتقل إلى أرض أعلى. إن لم تستطع الحركة، رد NEED HELP. هذه ليست تنبيه زلزال.",
  },
  PT: {
    lang: "Português",
    body: "Risco ALTO de inundação no oeste do Quénia. A chuva sobe há três dias. Se a estrada já estiver submersa, não espere uma segunda mensagem — vá para terreno mais alto. Se não puder mover-se, responda NEED HELP. Isto não é um alerta sísmico.",
  },
};

const COVERAGE = [
  "Morocco",
  "Algeria",
  "Egypt",
  "Sudan",
  "Ethiopia",
  "Somalia",
  "Senegal",
  "Mali",
  "Ghana",
  "Nigeria",
  "Cameroon",
  "DR Congo",
  "Uganda",
  "Kenya",
  "Rwanda",
  "Tanzania",
  "Zambia",
  "Mozambique",
  "Madagascar",
  "South Africa",
];

/** Nepal flood before/after — local asset for WHY MONJED EXISTS. */
const NEPAL_BEFORE_AFTER = "/media/nepal-before-after.jpg";

/** Real documented African disasters — Wikimedia Commons */
const DISASTER_IMAGES = [
  {
    src: "https://commons.wikimedia.org/wiki/Special:FilePath/Flooding_aftermath_of_Cyclone_Idai%2C_Mozambique_(9410).jpg?width=1400",
    alt: "Flooding aftermath of Cyclone Idai in Mozambique, 2019",
    place: "Beira, Mozambique",
    event: "Cyclone Idai floods · Mar 2019",
    hazard: "Flood",
  },
  {
    src: "https://commons.wikimedia.org/wiki/Special:FilePath/Flood_near_Zambezi_Delta_after_Cyclone_Idai.jpg?width=1400",
    alt: "Flooding near the Zambezi Delta after Cyclone Idai",
    place: "Zambezi Delta",
    event: "Idai inundation · Mar 2019",
    hazard: "Flood",
  },
  {
    src: "https://commons.wikimedia.org/wiki/Special:FilePath/Campmint_Amezmiz.jpg?width=1400",
    alt: "Emergency shelter camp near Amizmiz after the 2023 Morocco earthquake",
    place: "Amizmiz, Morocco",
    event: "Marrakesh–Safi quake · Sep 2023",
    hazard: "Earthquake",
  },
];

const FAQ = [
  {
    q: "Is this a trained forecast model?",
    a: "No. The flood engine is rule-based: rainfall, soil moisture, and trend map to a score and reasons. Thresholds would need calibration against historical disasters before operational use.",
  },
  {
    q: "Why not one combined risk score?",
    a: "A country can be high for floods and low for earthquakes at the same time. Blending hides which hazard is driving the alert. Flood and earthquake stay in separate columns — always.",
  },
  {
    q: "How precise is the location?",
    a: "MVP risk is country-level. Rainfall is sampled at a representative point per country, not averaged across the full area. Grid-level risk needs finer data than the free sources allow in this sprint.",
  },
  {
    q: "Does MONJED know my personal situation?",
    a: "Not in this version. Feasibility comes from ground reports — blocked roads, no transport, need help — and from volunteers who opt in with skills and a vehicle. Full household profiles are a later product.",
  },
];

const NAV = [
  { to: "/about", label: "About us" },
  { to: "/contact", label: "Contact us" },
  { to: "/volunteer", label: "Volunteer" },
];

export default function Landing() {
  const { isSignedIn } = useAuth();
  const mapTo = isSignedIn ? "/map" : "/login";
  const mapState = isSignedIn ? undefined : { from: "/map" };
  const reduced = useReducedMotion();
  const [menuOpen, setMenuOpen] = useState(false);
  const [openCountry, setOpenCountry] = useState(COUNTRIES[0].code);
  const [reportType, setReportType] = useState("ROAD BLOCKED");
  const [alertLang, setAlertLang] = useState("EN");
  const [faqOpen, setFaqOpen] = useState(0);

  const row = COUNTRIES.find((c) => c.code === openCountry) ?? COUNTRIES[0];
  const currentReport = REPORT_TYPES.find((r) => r.key === reportType);
  const currentAlert = ALERTS[alertLang];

  return (
    <div id="top" className="min-h-screen bg-night text-bone">
      <a
        href="#platform"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-20 focus:z-50 focus:bg-amber focus:text-ink focus:px-3 focus:py-2 focus:rounded"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-40 border-b border-line bg-panel/90 backdrop-blur">
        <div className="mx-auto max-w-6xl px-5 sm:px-8">
          <div className="flex h-16 items-center justify-between gap-4">
            <a href="#top" className="shrink-0">
              <MonjedLogo size="sm" tone="dark" />
            </a>
            <nav className="hidden md:flex items-center gap-7 text-sm text-mist">
              {NAV.map((l) => (
                <Link key={l.to} to={l.to} className="hover:text-bone transition-colors">
                  {l.label}
                </Link>
              ))}
            </nav>
            <div className="flex items-center gap-2 sm:gap-3">
              <ThemeToggle />
              <Link
                to={mapTo}
                state={mapState}
                className="hidden md:inline-flex items-center gap-1.5 rounded-md bg-amber px-4 py-2 text-sm font-semibold text-ink hover:bg-amber-bright transition-colors"
              >
                Open live map <ArrowRight size={15} />
              </Link>
              <button
                type="button"
                className="md:hidden text-bone p-1"
                onClick={() => setMenuOpen((v) => !v)}
                aria-label={menuOpen ? "Close menu" : "Open menu"}
              >
                {menuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>
          </div>
        </div>
        {menuOpen && (
          <div className="md:hidden border-t border-line bg-night px-5 py-4 space-y-3">
            {NAV.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                className="block text-sm text-mist"
                onClick={() => setMenuOpen(false)}
              >
                {l.label}
              </Link>
            ))}
            <Link
              to={mapTo}
              state={mapState}
              className="block text-center rounded-md bg-amber px-4 py-2 text-sm font-semibold text-ink"
              onClick={() => setMenuOpen(false)}
            >
              Open live map
            </Link>
          </div>
        )}
      </header>

      {/* HERO — full-bleed Cyclone Idai flood imagery */}
      <section className="relative min-h-[min(92vh,840px)] overflow-hidden border-b border-line flex flex-col">
        <img
          src={DISASTER_IMAGES[0].src}
          alt={DISASTER_IMAGES[0].alt}
          className="absolute inset-0 h-full w-full object-cover object-center"
          fetchPriority="high"
          decoding="async"
          referrerPolicy="no-referrer"
        />
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(105deg, rgba(11,18,32,0.92) 0%, rgba(11,18,32,0.72) 42%, rgba(11,18,32,0.35) 70%, rgba(11,18,32,0.45) 100%)",
          }}
        />
        <div className="relative flex-1 mx-auto w-full max-w-6xl px-5 sm:px-8 pt-16 pb-14 grid md:grid-cols-2 gap-12 items-center">
          <div className="max-w-2xl">
            <Reveal>
              <MonjedLogo size="xl" tone="light" />
              <p className="mt-4 font-mono text-xs sm:text-sm tracking-[0.2em] text-amber-bright">
                MULTI-HAZARD · LIVE DATA · 20+ COUNTRIES
              </p>
            </Reveal>
            <Reveal delay={80}>
              <h1 className="mt-7 font-display text-3xl sm:text-4xl lg:text-5xl font-bold leading-[1.08] tracking-tight text-white">
                The signal reaches
                <br />
                before the disaster does.
              </h1>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-7 text-lg sm:text-xl leading-relaxed text-white/80 max-w-lg">
                MONJED tracks flood and earthquake risk across Africa —
                separately, never as a blended index — then puts a volunteer
                behind the moments a warning alone cannot solve.
              </p>
            </Reveal>
            <Reveal delay={240}>
              <div className="mt-10 flex flex-wrap gap-3">
                <Link
                  to={mapTo}
                  state={mapState}
                  className="inline-flex items-center gap-2 rounded-md bg-amber px-6 py-3 text-base font-semibold text-ink hover:bg-amber-bright transition-colors"
                >
                  View live risk map <ArrowRight size={18} />
                </Link>
                <a
                  href="#responders"
                  className="inline-flex items-center gap-2 rounded-md border border-white/35 bg-white/5 px-6 py-3 text-base font-semibold text-white hover:border-white/60 transition-colors"
                >
                  Request help
                </a>
              </div>
            </Reveal>
            <Reveal delay={320}>
              <p className="mt-10 font-mono text-xs tracking-[0.14em] text-white/50">
                {DISASTER_IMAGES[0].place} · {DISASTER_IMAGES[0].event}
              </p>
            </Reveal>
          </div>
          <Reveal delay={200}>
            <div className="relative rounded-xl border border-white/15 bg-[#0b1220]/55 p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between font-mono text-[10px] tracking-[0.14em] text-white/55">
                <span className="inline-flex items-center gap-1.5">
                  <Radio size={12} className="text-teal" />
                  MONITORING NETWORK
                </span>
                <span className="text-teal">LIVE</span>
              </div>
              <PulseMap reduced={reduced} />
              <div className="flex items-center gap-4 justify-center font-mono text-[9px] text-white/50 mt-2">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-crimson" /> HIGH
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#F59E0B]" /> MEDIUM
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal" /> LOW
                </span>
              </div>
            </div>
          </Reveal>
        </div>
        <Ticker reduced={reduced} />
      </section>

      <div className="border-b border-line bg-panel/40">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { n: "20+", l: "COUNTRIES TRACKED" },
            { n: "2", l: "HAZARDS SCORED APART" },
            { n: "5", l: "TYPED REPORT KINDS" },
            { n: "0", l: "COST TO COMMUNITIES" },
          ].map((s, i) => (
            <Reveal key={s.l} delay={i * 70}>
              <div className="border-l border-line pl-4">
                <div className="font-display text-3xl font-bold">{s.n}</div>
                <div className="mt-1 font-mono text-[10px] tracking-[0.14em] text-slate">
                  {s.l}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>

      {/* WHY NOW — copy left, Nepal before/after image right */}
      <section
        id="why-now"
        className="border-b border-line bg-night"
      >
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-16 sm:py-20 grid lg:grid-cols-2 gap-10 lg:gap-14 items-center">
          <div>
            <Reveal>
              <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
                WHY MONJED EXISTS
              </p>
            </Reveal>
            <Reveal delay={80}>
              <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold leading-[1.12] tracking-tight max-w-xl">
                Floods like the crisis hitting Nepal are the problems MONJED is
                built to face.
              </h2>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-slate">
                When water rises, people need a clear signal, a plain action, and
                a path to help if they cannot move. MONJED connects risk, alerts,
                ground reports, and volunteers so a warning does not stop at the
                screen.
              </p>
            </Reveal>
          </div>

          <Reveal delay={120}>
            <figure className="overflow-hidden rounded-lg border border-line bg-raised shadow-[0_20px_50px_-28px_rgba(15,23,42,0.55)]">
              <img
                src={NEPAL_BEFORE_AFTER}
                alt="Nepal flood before and after: a riverside town intact, then buried under mud and debris"
                className="w-full h-auto object-cover"
                loading="lazy"
                decoding="async"
              />
            </figure>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <div className="grid md:grid-cols-[1.15fr_0.85fr] gap-10 lg:gap-14 items-center">
          <div>
            <Reveal>
              <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
                THE GAP
              </p>
            </Reveal>
            <Reveal delay={80}>
              <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold leading-tight">
                Most early-warning tools stop at detection. They rarely ask
                whether the person receiving the warning can do anything about
                it.
              </h2>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 max-w-xl text-slate leading-relaxed">
                A blocked road, no transport, or no data connection can make a
                technically correct alert useless. MONJED is built for that last
                stretch: score each hazard on its own terms, say it plainly,
                listen on the ground, and put a volunteer behind the moments a
                message cannot solve.
              </p>
            </Reveal>
          </div>
          <Reveal delay={120}>
            <MonjedBot reduced={reduced} />
          </Reveal>
        </div>
      </section>

      <section id="how-it-works" className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            HOW IT WORKS
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold">
            From raw signal to someone acting on it
          </h2>
        </Reveal>
        <div className="mt-14 grid md:grid-cols-4 gap-px bg-line rounded-lg overflow-hidden">
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 90} className="bg-panel p-6 h-full">
              <span className="font-mono text-xs text-amber">{s.n}</span>
              <h3 className="mt-3 font-display text-lg font-bold">{s.t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </section>

      <section id="platform" className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            WHY TWO SCORES
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-3xl">
            Kenya can be high for floods and low for earthquakes at the same
            time. That is the point.
          </h2>
          <p className="mt-4 max-w-2xl text-slate leading-relaxed">
            Blending hazards into one index hides which threat is moving. The
            dashboard, the SMS, and the volunteer match all read the hazard that
            is active — never a diluted average.
          </p>
        </Reveal>
        <div className="mt-12 grid md:grid-cols-2 gap-5">
          <Reveal>
            <div className="h-full rounded-lg border border-line bg-panel/60 p-7">
              <Waves size={22} className="text-amber" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-xl font-bold">Flood engine</h3>
              <ul className="mt-4 space-y-2 text-sm text-slate leading-relaxed">
                <li>Recent rainfall in mm — heavy rain carries the most weight</li>
                <li>Soil moisture from 0 to 1 — saturation compounds flood risk</li>
                <li>Trend: increasing, stable, or decreasing</li>
                <li>
                  Live today via{" "}
                  <span className="font-mono text-mist">POST /api/flood/risk</span>
                </li>
              </ul>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <div className="h-full rounded-lg border border-line bg-panel/60 p-7">
              <Mountain size={22} className="text-crimson" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-xl font-bold">
                Earthquake track
              </h3>
              <ul className="mt-4 space-y-2 text-sm text-slate leading-relaxed">
                <li>Shown per country on the public risk map</li>
                <li>Never mixed into the flood score</li>
                <li>A dry, seismically active country stays visible</li>
                <li>Dedicated HTTP engine is next — snapshot data is live on the UI</li>
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 pb-8">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[
            {
              icon: Activity,
              t: "Independent engines",
              d: "Flood and earthquake risk scored separately so a spike in one never masks the other.",
            },
            {
              icon: Languages,
              t: "Plain-language alerts",
              d: "The message names the hazard, the place, and what to do if you cannot move — written for SMS length.",
            },
            {
              icon: MessageSquare,
              t: "Typed ground reports",
              d: "Five taps under stress. Optional notes hit the live analyze API for severity and evidence.",
            },
            {
              icon: LifeBuoy,
              t: "Help without an account",
              d: "Request publicly. Matching only happens after a volunteer signs in — no fake dispatch.",
            },
            {
              icon: Users,
              t: "Volunteer network",
              d: "Skills, vehicle, zone, availability. Inbox is private; registration is public.",
            },
            {
              icon: ShieldCheck,
              t: "Responder console",
              d: "Operations staff triage New → Verified → Resolved. That console is private.",
            },
          ].map((f, i) => {
            const Icon = f.icon;
            return (
              <Reveal key={f.t} delay={i * 60}>
                <div className="h-full rounded-lg border border-line bg-panel/60 p-6 hover:border-amber/40 transition-colors">
                  <Icon size={20} className="text-amber" strokeWidth={1.75} />
                  <h3 className="mt-4 font-display text-base font-bold">{f.t}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate">{f.d}</p>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      <section id="reports" className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            GROUND TRUTH
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-2xl">
            Five taps, not a paragraph, when the water is already at the door
          </h2>
          <p className="mt-4 max-w-2xl text-slate leading-relaxed">
            Free text is slow under stress and noisy to map. Reports are typed
            so they plot immediately and feed the feasibility layer. Optional
            notes can still be analysed when someone has time to write.
          </p>
        </Reveal>
        <div className="mt-10 grid lg:grid-cols-[1fr_1.1fr] gap-6 items-start">
          <div className="space-y-2">
            {REPORT_TYPES.map((r) => {
              const Icon = r.icon;
              const on = r.key === reportType;
              return (
                <button
                  key={r.key}
                  type="button"
                  onClick={() => setReportType(r.key)}
                  className={`w-full flex items-center gap-3 rounded-lg border px-4 py-3.5 text-left transition-colors ${
                    on
                      ? "border-amber/50 bg-amber/10"
                      : "border-line bg-panel/40 hover:border-mist/20"
                  }`}
                >
                  <Icon
                    size={18}
                    className={on ? "text-amber" : "text-slate"}
                    strokeWidth={1.75}
                  />
                  <span className="font-mono text-xs tracking-wide">{r.key}</span>
                </button>
              );
            })}
          </div>
          <div className="rounded-lg border border-line bg-panel/60 p-7 min-h-[200px]">
            <p className="font-mono text-[10px] tracking-[0.16em] text-amber">
              WHAT THE SYSTEM DOES
            </p>
            <h3 className="mt-3 font-display text-2xl font-bold">
              {currentReport.key}
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-slate">
              {currentReport.d}
            </p>
            <p className="mt-6 text-xs text-muted leading-relaxed">
              Confidence rule: one report = low confidence. Several similar
              reports in the same zone and window = higher confidence and an
              automatic priority flag. No single report silently overrides the
              risk engine.
            </p>
            <Link
              to={isSignedIn ? "/report" : "/login"}
              state={isSignedIn ? undefined : { from: "/report" }}
              className="mt-6 inline-flex items-center gap-1.5 text-sm text-amber hover:underline"
            >
              File a report now <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            THE MESSAGE THAT ARRIVES
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-2xl">
            Written for a feature phone, in the language already on that phone
          </h2>
          <p className="mt-4 max-w-2xl text-slate leading-relaxed">
            The alert names the hazard, the place, why the score moved, and what
            to do if the recommended action is impossible. Flood copy never
            borrows earthquake language.
          </p>
        </Reveal>
        <Reveal delay={80}>
          <div className="mt-10 rounded-lg border border-line overflow-hidden">
            <div className="flex flex-wrap gap-1 bg-panel px-3 pt-3">
              {Object.entries(ALERTS).map(([code, v]) => (
                <button
                  key={code}
                  type="button"
                  onClick={() => setAlertLang(code)}
                  className={`px-3 py-2 text-xs font-mono tracking-wide rounded-t-md ${
                    alertLang === code
                      ? "bg-panel text-amber border border-line border-b-panel"
                      : "text-slate hover:text-bone"
                  }`}
                >
                  {code} · {v.lang}
                </button>
              ))}
            </div>
            <div
              className="bg-raised/50 p-6 sm:p-8"
              dir={alertLang === "AR" ? "rtl" : "ltr"}
            >
              <div className="flex items-center justify-between gap-3 font-mono text-[10px] tracking-[0.14em] text-slate mb-4">
                <span>SMS LENGTH · PLAIN LANGUAGE</span>
                <span className="text-teal shrink-0">HAZARD: FLOOD</span>
              </div>
              <p className="text-bone leading-relaxed text-base sm:text-lg max-w-3xl">
                {currentAlert.body}
              </p>
            </div>
          </div>
        </Reveal>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            FEASIBILITY LAYER
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-3xl">
            A correct warning is still useless if the road out is already gone
          </h2>
          <p className="mt-4 max-w-2xl text-slate leading-relaxed">
            When ground reports contradict the recommended action, escalate to a
            human instead of repeating the same SMS. Full household profiles are
            the next version — this one ships the insight that matters in a
            demo.
          </p>
        </Reveal>
        <div className="mt-12 grid md:grid-cols-3 gap-px bg-line rounded-lg overflow-hidden">
          {[
            {
              t: "Alert issued",
              d: "High flood risk for Kenya — evaluated on its own, not mixed with the earthquake score.",
            },
            {
              t: "Reports in the same zone",
              d: "Two ROAD BLOCKED and one NO TRANSPORT arrive within the window.",
            },
            {
              t: "Flag + human",
              d: "Alert annotated “verify route.” A signed-in volunteer with a vehicle can accept the request.",
            },
          ].map((s, i) => (
            <Reveal key={s.t} delay={i * 80} className="bg-panel p-6">
              <span className="font-mono text-xs text-amber">0{i + 1}</span>
              <h3 className="mt-3 font-display text-lg font-bold">{s.t}</h3>
              <p className="mt-2 text-sm text-slate leading-relaxed">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </section>

      <section id="snapshot" className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            LIVE RISK SNAPSHOT
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold">
            What the engines are seeing — open a row for the reasons
          </h2>
          <p className="mt-3 max-w-xl text-slate">
            Flood and earthquake stay in separate columns. Run the live flood
            engine yourself on the risk map.
          </p>
        </Reveal>
        <div className="mt-10 grid lg:grid-cols-[1.3fr_0.9fr] gap-5 items-start">
          <Reveal delay={80}>
            <div className="rounded-lg border border-line overflow-hidden">
              <div className="grid grid-cols-3 bg-panel px-5 py-3 font-mono text-[10px] tracking-[0.14em] text-slate">
                <span>COUNTRY</span>
                <span>FLOOD</span>
                <span>EARTHQUAKE</span>
              </div>
              {COUNTRIES.map((c, i) => (
                <button
                  key={c.code}
                  type="button"
                  onClick={() => setOpenCountry(c.code)}
                  className={`grid grid-cols-3 items-center w-full px-5 py-3.5 text-sm text-left transition-colors ${
                    openCountry === c.code
                      ? "bg-amber/10"
                      : i % 2 === 0
                        ? "bg-night"
                        : "bg-panel/50"
                  }`}
                >
                  <span className="font-medium">{c.name}</span>
                  <RiskBadge level={c.flood} />
                  <RiskBadge level={c.quake} />
                </button>
              ))}
            </div>
          </Reveal>
          <Reveal delay={140}>
            <div className="rounded-lg border border-line bg-panel/60 p-6">
              <p className="font-mono text-[10px] tracking-[0.16em] text-amber">
                {row.code} · NOT A BLENDED INDEX
              </p>
              <h3 className="mt-2 font-display text-xl font-bold">{row.name}</h3>
              <div className="mt-5 space-y-5">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Flood · {row.floodScore}/100</span>
                    <RiskBadge level={row.flood} />
                  </div>
                  <ul className="mt-2 space-y-1">
                    {row.floodReasons.map((r) => (
                      <li key={r} className="text-xs text-slate leading-relaxed">
                        — {r}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="border-t border-line pt-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">
                      Earthquake · {row.quakeScore}/100
                    </span>
                    <RiskBadge level={row.quake} />
                  </div>
                  <ul className="mt-2 space-y-1">
                    {row.quakeReasons.map((r) => (
                      <li key={r} className="text-xs text-slate leading-relaxed">
                        — {r}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <Link
                to={mapTo}
                state={mapState}
                className="mt-6 inline-flex items-center gap-1.5 text-sm text-amber hover:underline"
              >
                Open full map + flood engine <ArrowRight size={14} />
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 py-16">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            COVERAGE
          </p>
          <h2 className="mt-4 font-display text-2xl sm:text-3xl font-bold">
            Country-level for the MVP — one representative rainfall point per
            country, not a grid
          </h2>
          <p className="mt-3 max-w-2xl text-sm text-slate leading-relaxed">
            Sub-national resolution is a later upgrade. Saying that up front is
            part of being operational, not decorative. These frames are real
            African flood and earthquake events the network is built to face.
          </p>
        </Reveal>
        <div className="mt-10 grid sm:grid-cols-3 gap-4">
          {DISASTER_IMAGES.map((img, i) => (
            <Reveal key={img.event} delay={i * 90}>
              <figure className="group overflow-hidden rounded-lg border border-line bg-raised">
                <div className="relative aspect-[4/3] overflow-hidden bg-raised">
                  <img
                    src={img.src}
                    alt={img.alt}
                    loading="lazy"
                    decoding="async"
                    referrerPolicy="no-referrer"
                    className="h-full w-full object-cover opacity-95 transition-transform duration-700 group-hover:scale-[1.03]"
                  />
                  <span className="absolute left-3 top-3 rounded bg-night/80 px-2 py-1 font-mono text-[10px] tracking-wide text-bone backdrop-blur-sm">
                    {img.hazard}
                  </span>
                </div>
                <figcaption className="p-4 border-t border-line">
                  <p className="font-display text-sm font-bold">{img.place}</p>
                  <p className="mt-1 font-mono text-[10px] tracking-[0.12em] text-slate">
                    {img.event}
                  </p>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
        <Reveal delay={120}>
          <div className="mt-8 flex flex-wrap gap-2">
            {COVERAGE.map((c) => (
              <span
                key={c}
                className="rounded-md border border-line bg-panel/40 px-3 py-1.5 font-mono text-[11px] tracking-wide text-mist"
              >
                {c}
              </span>
            ))}
          </div>
        </Reveal>
      </section>

      <section id="responders" className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <div className="grid md:grid-cols-2 gap-5">
          <Reveal>
            <div className="h-full rounded-lg border border-line bg-panel p-8 dark:bg-raised dark:border-line">
              <div className="h-1 w-12 rounded-full bg-crimson/70 mb-5" />
              <LifeBuoy size={22} className="text-crimson" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-2xl font-bold">
                Need help right now?
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate">
                No account. Tell us what you need and where you are. Volunteers
                see it only after they sign in — we will not pretend someone is
                already on the way.
              </p>
              <Link
                to={isSignedIn ? "/help" : "/login"}
                state={isSignedIn ? undefined : { from: "/help" }}
                className="mt-6 inline-flex items-center gap-1.5 rounded-md border border-crimson/40 px-4 py-2 text-sm font-semibold text-bone hover:bg-crimson/10 transition-colors"
              >
                Request help <ArrowRight size={15} />
              </Link>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <div className="h-full rounded-lg border border-line bg-panel p-8 dark:bg-raised dark:border-line">
              <div className="h-1 w-12 rounded-full bg-teal/70 mb-5" />
              <Users size={22} className="text-teal" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-2xl font-bold">
                Want to help your community?
              </h3>
              <p className="mt-3 text-sm leading-relaxed text-slate">
                Register skills, vehicle, and zone once. Your inbox of assigned
                requests is private. Registration is public.
              </p>
              <Link
                to="/volunteer"
                className="mt-6 inline-flex items-center gap-1.5 rounded-md border border-teal/40 px-4 py-2 text-sm font-semibold text-bone hover:bg-teal/10 transition-colors"
              >
                Become a volunteer <ArrowRight size={15} />
              </Link>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 sm:px-8 py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            SAID UP FRONT
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold">
            Limits we will not hide
          </h2>
        </Reveal>
        <div className="mt-10 divide-y divide-line border-y border-line">
          {FAQ.map((item, i) => {
            const on = faqOpen === i;
            return (
              <div key={item.q}>
                <button
                  type="button"
                  className="flex w-full items-center justify-between gap-4 py-5 text-left"
                  onClick={() => setFaqOpen(on ? -1 : i)}
                  aria-expanded={on}
                >
                  <span className="font-display text-base sm:text-lg font-bold">
                    {item.q}
                  </span>
                  <ChevronDown
                    size={18}
                    className={`shrink-0 text-slate transition-transform ${
                      on ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {on && (
                  <p className="pb-5 max-w-3xl text-sm leading-relaxed text-slate">
                    {item.a}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-12">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6">
            <div>
              <MonjedLogo size="md" tone="dark" />
              <p className="mt-3 max-w-sm text-base text-slate leading-relaxed">
                A pan-African early warning and response layer — live hazard
                data, plain language, and a human when the recommended action is
                not realistic.
              </p>
            </div>
            <div className="font-mono text-[10px] tracking-[0.14em] text-slate leading-relaxed">
              <p>FLOOD ENGINE: LIVE API</p>
              <p>REPORT ANALYZE: LIVE API</p>
              <p>SCORES: NEVER BLENDED</p>
            </div>
          </div>
          <div className="mt-10 pt-6 border-t border-line flex flex-col sm:flex-row justify-between gap-3 text-xs text-muted">
            <span>Staff console and volunteer inbox are private.</span>
            <span>Free for affected communities. Always.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
