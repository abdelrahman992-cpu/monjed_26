import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import {
  Camera,
  Check,
  ChevronDown,
  LogIn,
  LogOut,
  UserRound,
  X,
} from "lucide-react";
import { useAuth } from "../lib/auth.jsx";
import { COUNTRIES } from "../data/mockRisk.js";

export function Avatar({ session, size = 36 }) {
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
      {session ? initials : <UserRound size={size * 0.45} />}
    </span>
  );
}

async function fileToAvatarDataUrl(file) {
  if (!file || !file.type.startsWith("image/")) {
    throw new Error("Choose an image file (PNG or JPG).");
  }

  if (file.size > 4 * 1024 * 1024) {
    throw new Error("Image must be under 4 MB.");
  }

  const bitmap = await createImageBitmap(file);
  const max = 320;
  const scale = Math.min(1, max / Math.max(bitmap.width, bitmap.height));
  const w = Math.round(bitmap.width * scale);
  const h = Math.round(bitmap.height * scale);

  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(bitmap, 0, 0, w, h);
  bitmap.close?.();

  return canvas.toDataURL("image/jpeg", 0.85);
}

export function ProfilePanel({ open, onClose }) {
  const { session, updateProfile, logout } = useAuth();
  const navigate = useNavigate();
  const fileRef = useRef(null);

  const [form, setForm] = useState({
    name: "",
    phone: "",
    zone: "",
    country: "",
    countryCode: "",
    vehicleType: "",
    capacity: "",
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!open || !session) return;

    setForm({
      name: session.name || "",
      phone: session.phone || "",
      zone: session.zone || "",
      country: session.country || "",
      countryCode: session.countryCode || "",
      vehicleType: session.vehicleType || "",
      capacity: session.capacity ?? "",
    });
    setMsg("");
    setErr("");
  }, [open, session]);

  if (!open || !session) return null;

  async function onAvatar(e) {
    const file = e.target.files?.[0];
    e.target.value = "";

    if (!file) return;

    setErr("");

    try {
      const avatar = await fileToAvatarDataUrl(file);
      await updateProfile({ avatar });
      setMsg("Photo updated.");
    } catch (ex) {
      setErr(ex.message || "Could not upload image.");
    }
  }

  async function save(e) {
    e.preventDefault();
    setSaving(true);
    setErr("");
    setMsg("");

    try {
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

      if (session.role === "user" || session.role === "citizen") {
        const c = COUNTRIES.find((x) => x.code === form.countryCode);
        patch.zone = form.zone.trim();
        patch.countryCode = form.countryCode;
        patch.country = c?.name || form.country.trim();
        patch.zone_id = form.countryCode || session.zone_id;
      }

      await updateProfile(patch);
      setMsg("Profile saved.");
    } catch (ex) {
      setErr(ex.message || "Could not save profile.");
    } finally {
      setSaving(false);
    }
  }

  const panel = (
    <div className="fixed inset-0 z-[100] flex justify-end">
      <button
        type="button"
        className="absolute inset-0 bg-night/60 backdrop-blur-[2px]"
        aria-label="Close profile"
        onClick={onClose}
      />

      <aside
        className="relative z-10 flex h-dvh w-full max-w-md flex-col border-l border-line bg-panel shadow-2xl animate-[slide-in_0.25s_ease-out]"
        aria-label="Profile settings"
      >
        <div className="shrink-0 flex items-center justify-between gap-3 border-b border-line px-5 py-4">
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

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="relative shrink-0">
                <Avatar session={session} size={72} />
                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="absolute -bottom-1 -right-1 rounded-full border border-line bg-panel p-1.5 text-amber shadow-sm hover:bg-raised"
                  aria-label="Change photo"
                >
                  <Camera size={14} />
                </button>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={onAvatar}
                />
              </div>

              <div className="min-w-0">
                <p className="font-display font-bold truncate">
                  {session?.name}
                </p>
                <p className="text-xs text-slate capitalize">
                  {session?.role}
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
                  onChange={(e) =>
                    setForm((f) => ({ ...f, name: e.target.value }))
                  }
                  className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                  required
                />
              </label>

              <label className="block">
                <span className="font-mono text-[10px] tracking-wide text-slate">
                  PHONE
                </span>
                <input
                  value={form.phone}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, phone: e.target.value }))
                  }
                  className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                />
              </label>

              {(session?.role === "user" || session?.role === "citizen") && (
                <>
                  <label className="block">
                    <span className="font-mono text-[10px] tracking-wide text-slate">
                      COUNTRY
                    </span>
                    <select
                      value={form.countryCode}
                      onChange={(e) =>
                        setForm((f) => ({
                          ...f,
                          countryCode: e.target.value,
                        }))
                      }
                      className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                    >
                      {COUNTRIES.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="block">
                    <span className="font-mono text-[10px] tracking-wide text-slate">
                      TOWN / ZONE
                    </span>
                    <input
                      value={form.zone}
                      onChange={(e) =>
                        setForm((f) => ({ ...f, zone: e.target.value }))
                      }
                      className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                    />
                  </label>
                </>
              )}

              {session?.role === "volunteer" && (
                <>
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

                  <div className="grid grid-cols-2 gap-3">
                    <label className="block">
                      <span className="font-mono text-[10px] tracking-wide text-slate">
                        VEHICLE
                      </span>
                      <input
                        value={form.vehicleType}
                        onChange={(e) =>
                          setForm((f) => ({
                            ...f,
                            vehicleType: e.target.value,
                          }))
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
                          setForm((f) => ({
                            ...f,
                            capacity: e.target.value,
                          }))
                        }
                        className="mt-1.5 w-full rounded-md border border-line bg-night/40 px-3 py-2 text-sm focus:outline-none focus:border-amber"
                      />
                    </label>
                  </div>
                </>
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
        </div>

        <div className="shrink-0 border-t border-line bg-panel px-5 py-4">
          <button
            type="button"
            onClick={() => {
              onClose();
              logout();
              navigate("/");
            }}
            className="w-full inline-flex items-center justify-center gap-2 rounded-md border border-line px-4 py-2.5 text-sm text-slate hover:text-bone hover:border-crimson/40"
          >
            <LogOut size={15} />
            Sign out
          </button>
        </div>
      </aside>
    </div>
  );

  return createPortal(panel, document.body);
}

/** Shared account menu for signed-in and signed-out users. */
export default function UserProfileMenu() {
  const { session, logout } = useAuth();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [panel, setPanel] = useState(false);
  const menuRef = useRef(null);
  const menuId = useId();

  useEffect(() => {
    function onDoc(e) {
      if (!menuRef.current?.contains(e.target)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  function signOut() {
    setOpen(false);
    setPanel(false);
    logout();
    navigate("/");
  }

  return (
    <>
      <div className="relative" ref={menuRef}>
        <button
          type="button"
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((v) => !v)}
          className="inline-flex items-center gap-2 rounded-full border border-line bg-night/30 pl-1 pr-2.5 py-1 hover:border-amber/40 transition-colors"
        >
          <Avatar session={session} size={30} />
          <span className="hidden sm:block text-sm font-medium max-w-[120px] truncate">
            {session?.name || "Sign in"}
          </span>
          <ChevronDown size={14} className="text-slate" />
        </button>

        {open && (
          <div
            id={menuId}
            className="absolute right-0 mt-2 w-52 overflow-hidden rounded-xl border border-line bg-panel shadow-lg py-1.5 z-50"
          >
            {session ? (
              <>
                <button
                  type="button"
                  className="w-full px-3.5 py-2.5 text-left text-sm hover:bg-raised flex items-center gap-2"
                  onClick={() => {
                    setOpen(false);
                    setPanel(true);
                  }}
                >
                  <UserRound size={15} className="text-amber" />
                  Update profile
                </button>

                <button
                  type="button"
                  className="w-full border-t border-line px-3.5 py-2.5 text-left text-sm text-crimson hover:bg-raised flex items-center gap-2"
                  onClick={signOut}
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
                  setOpen(false);
                  navigate("/login");
                }}
              >
                <LogIn size={15} className="text-amber" />
                Sign in
              </button>
            )}
          </div>
        )}
      </div>

      <ProfilePanel open={panel} onClose={() => setPanel(false)} />
    </>
  );
}
