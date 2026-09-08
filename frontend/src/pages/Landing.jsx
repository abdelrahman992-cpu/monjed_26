import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Radio,
  Waves,
  Mountain,
  Users,
  LifeBuoy,
  Menu,
  X,
  ChevronDown,
} from "lucide-react";
import ThemeToggle from "../components/ThemeToggle.jsx";
import MonjedLogo from "../components/MonjedLogo.jsx";
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

const STEPS = [
  {
    n: "01",
    t: "Watch the signals",
    d: "Rainfall, soil moisture, and seismic activity are tracked as separate streams — never mixed into one vague score.",
  },
  {
    n: "02",
    t: "See a clear level",
    d: "Each hazard gets a 0–100 score, a plain risk level, and short reasons you can actually act on.",
  },
  {
    n: "03",
    t: "Report from the ground",
    d: "Quick typed reports — blocked roads, rising water, need help — confirm what the engines cannot see.",
  },
  {
    n: "04",
    t: "Get a human when stuck",
    d: "If you cannot move or the route is gone, request help. Volunteers in your zone pick it up privately.",
  },
];

const ALERTS = {
  EN: {
    lang: "English",
    body: "HIGH flood risk, western Kenya. Rain has been climbing for three days. If water is already on the road, do not wait for a second message — move to higher ground. If you cannot move, reply NEED HELP.",
  },
  SW: {
    lang: "Kiswahili",
    body: "Hatari KUBWA ya mafuriko, magharibi mwa Kenya. Mvua imeongezeka kwa siku tatu. Ikiwa barabara imefunikwa maji, usisubiri ujumbe wa pili — nenda sehemu ya juu. Usipoweza kusogea, jibu NEED HELP.",
  },
  FR: {
    lang: "Français",
    body: "Risque ÉLEVÉ d’inondation, ouest du Kenya. La pluie augmente depuis trois jours. Si la route est déjà sous l’eau, n’attendez pas un second message — gagnez un terrain plus élevé. Si vous ne pouvez pas bouger, répondez NEED HELP.",
  },
};

const NEPAL_BEFORE_AFTER = "/media/nepal-before-after.jpg";

const DISASTER_IMAGES = [
  {
    src: "https://commons.wikimedia.org/wiki/Special:FilePath/Flooding_aftermath_of_Cyclone_Idai%2C_Mozambique_(9410).jpg?width=1400",
    alt: "Flooding aftermath of Cyclone Idai in Mozambique, 2019",
    place: "Beira, Mozambique",
    event: "Cyclone Idai floods · Mar 2019",
  },
];

const FAQ = [
  {
    q: "Is this a trained forecast model?",
    a: "No. The flood engine is rule-based: rainfall, soil moisture, and trend map to a score and reasons. Thresholds would need calibration against historical disasters before operational use.",
  },
  {
    q: "Why not one combined risk score?",
    a: "A country can be high for floods and low for earthquakes at the same time. Blending hides which hazard is driving the alert. Flood and earthquake stay separate — always.",
  },
  {
    q: "How precise is the location?",
    a: "MVP risk is country-level, with rainfall sampled at a representative point per country. Finer grid-level risk needs richer data than this version ships.",
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
  const [alertLang, setAlertLang] = useState("EN");
  const [faqOpen, setFaqOpen] = useState(0);

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
                <Link
  to="/help"
  className="inline-flex items-center gap-2 rounded-md bg-red-600 hover:bg-red-700 px-6 py-3 text-base font-bold text-white shadow-lg shadow-red-600/30 active:scale-95 transition-all"
>
  <span className="relative flex h-2.5 w-2.5">
    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-white"></span>
  </span>
  Request help
</Link>
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
      </section>

      {/* WHY — purpose + image */}
      <section id="why-now" className="border-b border-line bg-night">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-16 sm:py-20 grid lg:grid-cols-2 gap-10 lg:gap-14 items-center">
          <div>
            <Reveal>
              <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
                WHY MONJED EXISTS
              </p>
            </Reveal>
            <Reveal delay={80}>
              <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold leading-[1.12] tracking-tight max-w-xl">
                Warnings should reach people before the water does — and help
                should follow when they cannot move.
              </h2>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-slate">
                MONJED connects live hazard risk, plain-language alerts, ground
                reports, and volunteers so a warning does not stop at the
                screen.
              </p>
            </Reveal>
          </div>
          <Reveal delay={120}>
            <figure className="overflow-hidden rounded-lg border border-line bg-raised">
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

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-5 sm:px-8 py-20 sm:py-24">
        <Reveal>
          <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
            HOW IT WORKS
          </p>
          <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-2xl">
            From signal to someone who can act
          </h2>
        </Reveal>
        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 80}>
              <span className="font-mono text-xs text-amber">{s.n}</span>
              <h3 className="mt-3 font-display text-lg font-bold">{s.t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* TWO SCORES */}
      <section id="platform" className="border-y border-line bg-panel/30">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-20 sm:py-24">
          <Reveal>
            <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
              TWO HAZARDS · TWO SCORES
            </p>
            <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-3xl">
              Flood and earthquake never share one number.
            </h2>
            <p className="mt-4 max-w-2xl text-slate leading-relaxed">
              A place can be high for floods and low for quakes at the same
              time. Mixing them hides which threat is moving — so we keep them
              apart on the map, in alerts, and in response.
            </p>
          </Reveal>
          <div className="mt-12 grid md:grid-cols-2 gap-10 md:gap-14">
            <Reveal>
              <Waves size={22} className="text-amber" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-xl font-bold">Flood</h3>
              <p className="mt-3 text-sm leading-relaxed text-slate">
                Built from recent rainfall, soil moisture, and whether conditions
                are getting worse. You get a level and short reasons — not a
                black-box probability.
              </p>
            </Reveal>
            <Reveal delay={90}>
              <Mountain size={22} className="text-crimson" strokeWidth={1.75} />
              <h3 className="mt-4 font-display text-xl font-bold">Earthquake</h3>
              <p className="mt-3 text-sm leading-relaxed text-slate">
                Tracked per country on its own column. A dry, seismically active
                area stays visible even when flood risk is low.
              </p>
            </Reveal>
          </div>
        </div>
      </section>

      {/* ALERT SAMPLE */}
      <section className="border-b border-line bg-panel/30">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-20 sm:py-24">
          <Reveal>
            <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
              THE MESSAGE THAT ARRIVES
            </p>
            <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold max-w-2xl">
              Plain language, ready for SMS
            </h2>
            <p className="mt-4 max-w-2xl text-slate leading-relaxed">
              The alert names the hazard, the place, and what to do if you cannot
              move — written short enough for a feature phone.
            </p>
          </Reveal>
          <Reveal delay={80}>
            <div className="mt-10">
              <div className="flex flex-wrap gap-2 mb-4">
                {Object.entries(ALERTS).map(([code, v]) => (
                  <button
                    key={code}
                    type="button"
                    onClick={() => setAlertLang(code)}
                    className={`px-3 py-1.5 text-xs font-mono tracking-wide rounded-md border transition-colors ${
                      alertLang === code
                        ? "border-amber/50 bg-amber/10 text-amber"
                        : "border-line text-slate hover:text-bone"
                    }`}
                  >
                    {v.lang}
                  </button>
                ))}
              </div>
              <div
                className="rounded-lg border border-line bg-raised/40 p-6 sm:p-8"
                dir={alertLang === "AR" ? "rtl" : "ltr"}
              >
                <p className="font-mono text-[10px] tracking-[0.14em] text-teal mb-4">
                  HAZARD: FLOOD
                </p>
                <p className="text-bone leading-relaxed text-base sm:text-lg max-w-3xl">
                  {currentAlert.body}
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* CTAs */}
      <section id="responders" className="mx-auto max-w-6xl px-5 sm:px-8 py-20 sm:py-24">
        <div className="grid md:grid-cols-2 gap-10 md:gap-16">
          <Reveal>
            <LifeBuoy size={22} className="text-crimson" strokeWidth={1.75} />
            <h3 className="mt-4 font-display text-2xl font-bold">
              Need help right now?
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-slate max-w-md">
              Tell us what you need and where you are. Volunteers only see the
              request after they sign in — we will not pretend someone is already
              on the way.
            </p>
            <Link
              to="/help"
              className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-amber hover:underline"
            >
              Request help <ArrowRight size={15} />
            </Link>
          </Reveal>
          <Reveal delay={80}>
            <Users size={22} className="text-teal" strokeWidth={1.75} />
            <h3 className="mt-4 font-display text-2xl font-bold">
              Want to help your community?
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-slate max-w-md">
              Register your skills, vehicle, and zone once. Assigned requests
              stay in your private inbox.
            </p>
            <Link
              to="/volunteer"
              className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-amber hover:underline"
            >
              Become a volunteer <ArrowRight size={15} />
            </Link>
          </Reveal>
        </div>
      </section>

      {/* FAQ */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-20 sm:py-24">
          <Reveal>
            <p className="font-mono text-[11px] tracking-[0.18em] text-amber">
              HONEST LIMITS
            </p>
            <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold">
              What this version is — and is not
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
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-12">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6">
            <div>
              <MonjedLogo size="md" tone="dark" />
              <p className="mt-3 max-w-sm text-base text-slate leading-relaxed">
                Early warning and response for Africa — clear hazard scores,
                plain alerts, and a human when a message is not enough.
              </p>
            </div>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-mist">
              <Link to="/about" className="hover:text-bone transition-colors">
                About
              </Link>
              <Link to="/contact" className="hover:text-bone transition-colors">
                Contact
              </Link>
              <Link to="/volunteer" className="hover:text-bone transition-colors">
                Volunteer
              </Link>
              <Link to="/help" className="hover:text-bone transition-colors">
                Request help
              </Link>
            </div>
          </div>
          <div className="mt-10 pt-6 border-t border-line flex flex-col sm:flex-row justify-between gap-3 text-xs text-muted">
            <span>Flood and earthquake scores are never blended.</span>
            <span>Free for affected communities.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
