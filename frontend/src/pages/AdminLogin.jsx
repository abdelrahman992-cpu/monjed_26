import { Navigate } from "react-router-dom";

/** Staff login lives on /volunteer — keep this route as a redirect. */
export default function AdminLoginPage() {
  return <Navigate to="/volunteer" replace state={{ mode: "staff" }} />;
}
