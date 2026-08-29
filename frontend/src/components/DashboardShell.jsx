import { useEffect, useId, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Check,
  ChevronDown,
  LogOut,
  Menu,
  UserRound,
  X,
} from "lucide-react";
import MonjedLogo from "./MonjedLogo.jsx";
import { useAuth } from "../lib/auth.jsx";
import BackNav from "./BackNav.jsx";

function Avatar({ session, size = 36 }) {
  const initials = (session?.name || "?")
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  if (session?.avatar) {
    return (
      <img
        src={session.avatar}
        alt=""
        width={size}
        height={size}
        className="rounded-full object-cover border border-line shrink-0"
        style={{ width: size, height: size }}
      />
    );
  }

  return (
    <span
      className="inline-flex items-center justify-center rounded-full bg-raised border border-line font-display font-bold text-amber shrink-0"
      style={{ width: size, height: size, fontSize: size * 0.32 }}
    >
      {initials || <UserRound size={size * 0.45} />}
    </span>
  );
}

function ProfilePanel({ open, onClose }) {
  const { session, updateProfile, updateAdminProfile, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: session?.name || "",
    phone: session?.phone || "",
    email: session?.email || "",
    organization: session?.organization || "",
    title: session?.title || "",
    zone: session?.zone || "",
    country: session?.country || "",
    vehicleType: session?.vehicleType || "",
    capacity: session?.capacity ?? "",
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!open || !session) return;
    setForm({
      name: session.name || "",
      phone: session.phone || "",
      email: session.email || "",
      organization: session.organization || "",
      title: session.title || "",
      zone: session.zone || "",
      country: session.country || "",
      vehicleType: session.vehicleType || "",
      capacity: session.capacity ?? "",
    });
    setMsg("");
    setErr("");
  }, [open, session]);

  if (!open) return null;

  async function save(e) {
    e.preventDefault();
    setSaving(true);
    setErr("");
    setMsg("");
    try {
      if (session.role === "admin") {
        await updateAdminProfile({
          name: form.name.trim() || session.name,
          phone: form.phone.trim(),
          email: form.email.trim(),
          organization: form.organization.trim(),
          title: form.title.trim(),
          country: form.country.trim(),
          zone: form.zone.trim(),
        });
      } else {
        const patch = {
          name: form.name.trim() || session.name,
          phone: form.phone.trim(),
        };
        if (session.role === "volunteer") {
          patch.zone = form.zone.trim();
          patch.country = form.country.trim();
          patch.vehicleType = form.vehicleType.trim();
          patch.capacity = Number(form.capacity) || 0;
        }
        await updateProfile(patch);
      }
      setMsg("Profile saved.");
    } catch (ex) {
      setErr(ex.message || "Could not save profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        type="button"
        className="absolute inset-0 bg-night/50 backdrop-blur-[2px]"
        aria-label="Close profile"
        onClick={onClose}
      />
      <aside className="relative z-10 flex h-full w-full max-w-md flex-col border-l border-line bg-panel shadow-xl animate-[slide-in_0.25s_ease-out]">
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
          <div>
            <p className="font-mono text-[10px] tracking-[0.16em] text-amber">
              ACCOUNT
            </p>
            <h2 className="font-display text-lg font-bold">Update profile</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate hover:text-bone hover:bg-raised"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-6">
          <div className="flex items-center gap-4">
            <Avatar session={session} size={72} />
            <div className="min-w-0">
              <p className="font-display font-bold truncate">{session?.name}</p>
              <p className="text-xs text-slate capitalize">
                {session?.title || session?.role}
                {session?.organization ? ` · ${session.organization}` : ""}
              </p>
            </div>
          </div>

          <form onSubmit={save} className="space-y-3">
            <label className="block">
              <span className="font-mono text-[10px] tracking-wide text-slate">
                DISPLAY NAME
              </span>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                required
              />
            </label>

            {session?.role === "admin" && (
              <>
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    ROLE / TITLE
                  </span>
                  <input
                    value={form.title}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, title: e.target.value }))
                    }
                    placeholder="Duty officer, Ops lead…"
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    ORGANIZATION
                  </span>
                  <input
                    value={form.organization}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, organization: e.target.value }))
                    }
                    placeholder="MONJED Operations"
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    WORK EMAIL
                  </span>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, email: e.target.value }))
                    }
                    placeholder="ops@example.org"
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
              </>
            )}

            <label className="block">
              <span className="font-mono text-[10px] tracking-wide text-slate">
                PHONE
              </span>
              <input
                value={form.phone}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                placeholder="+254…"
                className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
              />
            </label>

            {(session?.role === "admin" || session?.role === "volunteer") && (
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    ZONE
                  </span>
                  <input
                    value={form.zone}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, zone: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    COUNTRY
                  </span>
                  <input
                    value={form.country}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, country: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
              </div>
            )}

            {session?.role === "volunteer" && (
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    VEHICLE
                  </span>
                  <input
                    value={form.vehicleType}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, vehicleType: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
                <label className="block">
                  <span className="font-mono text-[10px] tracking-wide text-slate">
                    CAPACITY
                  </span>
                  <input
                    type="number"
                    min="0"
                    value={form.capacity}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, capacity: e.target.value }))
                    }
                    className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  />
                </label>
              </div>
            )}

            {msg && (
              <p className="text-xs text-teal inline-flex items-center gap-1">
                <Check size={12} /> {msg}
              </p>
            )}
            {err && <p className="text-xs text-crimson">{err}</p>}

            <button
              type="submit"
              disabled={saving}
              className="w-full rounded-md bg-amber px-4 py-2.5 text-sm font-semibold text-ink hover:bg-amber-bright disabled:opacity-60"
            >
              {saving ? "Saving…" : "Save changes"}
            </button>
          </form>
        </div>

        <div className="border-t border-line px-5 py-4">
          <button
            type="button"
            onClick={() => {
              logout();
              navigate("/");
            }}
            className="w-full inline-flex items-center justify-center gap-2 rounded-md border border-line px-4 py-2.5 text-sm text-slate hover:text-bone hover:border-crimson/40"
          >
            <LogOut size={15} /> Sign out
          </button>
        </div>
      </aside>
    </div>
  );
}

/**
 * Professional ops shell: top bar (logo left + profile), sidebar nav, back-home in body.
 */
export default function DashboardShell({
  title,
  subtitle,
  navItems,
  activeId,
  onNavigate,
  badge,
  children,
}) {
  const { session, logout } = useAuth();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenu, setUserMenu] = useState(false);
  const userMenuId = useId();
  const menuRef = useRef(null);

  useEffect(() => {
    function onDoc(e) {
      if (!menuRef.current?.contains(e.target)) setUserMenu(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  function go(id) {
    onNavigate(id);
    setMenuOpen(false);
  }

  const sidebar = (
    <nav className="flex flex-col h-full">
      <p className="px-4 pt-4 pb-2 font-mono text-[10px] tracking-[0.16em] text-slate">
        WORKSPACE
      </p>
      <ul className="px-2 space-y-0.5 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = item.id === activeId;
          return (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => go(item.id)}
                className={`w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  active
                    ? "bg-amber/15 text-bone font-semibold border border-amber/30"
                    : "text-mist hover:bg-raised/60 border border-transparent"
                }`}
              >
                <Icon
                  size={17}
                  className={active ? "text-amber" : "text-slate"}
                  strokeWidth={1.75}
                />
                <span className="flex-1 text-left">{item.label}</span>
                {item.count != null && (
                  <span
                    className={`font-mono text-[10px] tabular-nums px-1.5 py-0.5 rounded ${
                      active ? "bg-amber/20 text-amber" : "bg-raised text-slate"
                    }`}
                  >
                    {item.count}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
      <div className="px-4 py-4 border-t border-line">
        <p className="font-mono text-[9px] tracking-wide text-muted leading-relaxed">
          Flood and earthquake scores are never blended.
        </p>
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen flex flex-col bg-night text-bone">
      {/* Top navbar — logo left, profile right */}
      <header className="sticky top-0 z-30 border-b border-line bg-panel/95 backdrop-blur">
        <div className="flex h-14 items-center gap-3 px-3 sm:px-5">
          <button
            type="button"
            className="lg:hidden rounded-md p-2 text-slate hover:text-bone hover:bg-raised"
            onClick={() => setMenuOpen(true)}
            aria-label="Open menu"
          >
            <Menu size={20} />
          </button>

          <div className="flex items-center min-w-0">
            <MonjedLogo size="sm" tone="dark" />
          </div>

          <div className="ml-auto flex items-center gap-2 sm:gap-3">
            {badge}
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                aria-expanded={userMenu}
                aria-controls={userMenuId}
                onClick={() => setUserMenu((v) => !v)}
                className="inline-flex items-center gap-2 rounded-full border border-line bg-night/30 pl-1 pr-2.5 py-1 hover:border-amber/40 transition-colors"
              >
                <Avatar session={session} size={30} />
                <span className="hidden sm:block text-sm font-medium max-w-[120px] truncate">
                  {session?.name || "Sign in"}
                </span>
                <ChevronDown size={14} className="text-slate" />
              </button>
              {userMenu && (
                <div
                  id={userMenuId}
                  className="absolute right-0 mt-2 w-52 rounded-xl border border-line bg-panel shadow-lg py-1.5 z-40"
                >
                  {session ? (
                    <>
                      <button
                        type="button"
                        className="w-full px-3.5 py-2.5 text-left text-sm hover:bg-raised flex items-center gap-2"
                        onClick={() => {
                          setUserMenu(false);
                          setProfileOpen(true);
                        }}
                      >
                        <UserRound size={15} className="text-amber" />
                        Update profile
                      </button>

                      <button
                        type="button"
                        className="w-full px-3.5 py-2.5 text-left text-sm text-crimson hover:bg-raised flex items-center gap-2 border-t border-line"
                        onClick={() => {
                          setUserMenu(false);
                          setProfileOpen(false);
                          logout();
                          navigate("/");
                        }}
                      >
                        <LogOut size={15} />
                        Sign out
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      className="w-full px-3.5 py-2.5 text-left text-sm hover:bg-raised flex items-center gap-2"
                      onClick={() => {
                        setUserMenu(false);
                        navigate("/login");
                      }}
                    >
                      <UserRound size={15} className="text-amber" />
                      Sign in
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        {/* Desktop sidebar */}
        <aside className="hidden lg:sticky lg:top-14 lg:flex h-[calc(100vh-3.5rem)] w-60 shrink-0 self-start flex-col overflow-y-auto border-r border-line bg-panel/40">
          {sidebar}
        </aside>

        {/* Mobile drawer */}
        {menuOpen && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-night/60"
              aria-label="Close menu"
              onClick={() => setMenuOpen(false)}
            />
            <aside className="relative z-10 h-full w-72 max-w-[85vw] border-r border-line bg-panel shadow-xl flex flex-col">
              <div className="flex items-center justify-between px-4 h-14 border-b border-line">
                <MonjedLogo size="sm" tone="dark" showWordmark={false} />
                <button
                  type="button"
                  onClick={() => setMenuOpen(false)}
                  className="p-2 text-slate"
                  aria-label="Close"
                >
                  <X size={18} />
                </button>
              </div>
              {sidebar}
            </aside>
          </div>
        )}

        {/* Main body */}
        <main className="flex-1 min-w-0 overflow-x-hidden">
          <div className="px-4 sm:px-6 lg:px-8 pt-4 pb-12 max-w-7xl mx-auto">
            <BackNav />

            <div className="mt-4 mb-6 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
                  {title}
                </h1>
                {subtitle && (
                  <p className="mt-1.5 text-sm text-slate max-w-2xl leading-relaxed">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>

            {children}
          </div>
        </main>
      </div>

      <ProfilePanel open={profileOpen} onClose={() => setProfileOpen(false)} />
    </div>
  );
}

export { Avatar };
