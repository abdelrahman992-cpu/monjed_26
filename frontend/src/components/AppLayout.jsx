import { Outlet, Link, NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";
import MonjedLogo from "./MonjedLogo.jsx";
import BackNav from "./BackNav.jsx";
import UserProfileMenu from "./UserProfileMenu.jsx";

const MEMBER_NAV = [
  { to: "/map", label: "Map" },
  { to: "/report", label: "Report" },
  { to: "/help", label: "Request help" },
];

const AUTH_PATHS = ["/login", "/volunteer", "/admin/login"];

function logoHome(session) {
  if (!session) return "/";
  if (session.role === "admin") return "/admin";
  if (session.role === "volunteer") return "/volunteer/dashboard";
  return "/map";
}

/** Public + member shell — logo left, tools centered, profile right. */
export default function AppLayout() {
  const { session, isSignedIn } = useAuth();
  const location = useLocation();

  const showMemberNav =
    isSignedIn &&
    (session?.role === "user" ||
      session?.role === "citizen" ||
      location.pathname.startsWith("/map") ||
      location.pathname.startsWith("/report") ||
      location.pathname.startsWith("/help") ||
      location.pathname.startsWith("/trends"));

  const hideAuthMenu = !isSignedIn && AUTH_PATHS.includes(location.pathname);

  return (
    <div className="min-h-screen bg-night text-bone flex flex-col">
      <header className="sticky top-0 z-40 border-b border-line bg-panel/90 backdrop-blur">
        <div className="mx-auto max-w-6xl px-5 sm:px-8">
          <div className="relative grid grid-cols-[1fr_auto_1fr] items-center h-14 gap-2">
            <Link
              to={logoHome(session)}
              className="justify-self-start shrink-0"
              aria-label="MONJED"
            >
              <MonjedLogo size="sm" tone="dark" />
            </Link>

            {showMemberNav ? (
              <nav className="justify-self-center flex items-center gap-1 sm:gap-5 text-sm text-mist">
                {MEMBER_NAV.map((l) => (
                  <NavLink
                    key={l.to}
                    to={l.to}
                    className={({ isActive }) =>
                      `px-2 sm:px-1 py-1 rounded-md transition-colors whitespace-nowrap ${
                        isActive
                          ? "text-bone font-semibold"
                          : "hover:text-bone"
                      }`
                    }
                  >
                    {l.label}
                  </NavLink>
                ))}
              </nav>
            ) : (
              <span />
            )}

            <div className="justify-self-end flex items-center gap-3">
              {!hideAuthMenu && <UserProfileMenu />}
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 pt-4">
          <BackNav />
        </div>
        <Outlet />
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto max-w-6xl px-5 sm:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 font-mono text-[10px] tracking-[0.12em] text-slate">
          <span>FLOOD AND EARTHQUAKE SCORES ARE NEVER BLENDED</span>
          <span>LIVE API: FLOOD RISK · COMMUNITY REPORT ANALYZE</span>
        </div>
      </footer>
    </div>
  );
}
