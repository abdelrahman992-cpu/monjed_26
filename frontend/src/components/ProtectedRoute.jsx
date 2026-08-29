import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../lib/auth.jsx";

/**
 * @param {{ role?: string, roles?: string[], loginTo?: string }} props
 * - role: single required role
 * - roles: any of these roles allowed
 * - if neither set, any signed-in session is enough
 */
export default function ProtectedRoute({
  role,
  roles,
  loginTo = "/login",
}) {
  const { session } = useAuth();
  const location = useLocation();

  if (!session) {
    return (
      <Navigate to={loginTo} replace state={{ from: location.pathname }} />
    );
  }

  const allowed = roles || (role ? [role] : null);
  if (allowed && !allowed.includes(session.role)) {
    // Wrong role — send volunteers/admins to their home, citizens to map
    const fallback =
      session.role === "admin"
        ? "/admin"
        : session.role === "volunteer"
          ? "/volunteer/dashboard"
          : "/map";
    return <Navigate to={fallback} replace />;
  }

  return <Outlet />;
}
