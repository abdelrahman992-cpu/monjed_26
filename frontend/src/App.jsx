import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./lib/auth.jsx";
import { ThemeProvider } from "./lib/theme.jsx";
import { NavLoadProvider } from "./components/PageLoader.jsx";
import AppLayout from "./components/AppLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Landing from "./pages/Landing.jsx";
import MapPage from "./pages/Map.jsx";
import ReportPage from "./pages/Report.jsx";
import HelpPage from "./pages/Help.jsx";
import TrendsPage from "./pages/Trends.jsx";
import LoginPage from "./pages/Login.jsx";
import AboutPage from "./pages/About.jsx";
import ContactPage from "./pages/Contact.jsx";
import VolunteerAuthPage from "./pages/Volunteer.jsx";
import VolunteerDashboardPage from "./pages/VolunteerDashboard.jsx";
import AdminLoginPage from "./pages/AdminLogin.jsx";
import AdminPage from "./pages/Admin.jsx";
import NotFoundPage from "./pages/NotFound.jsx";

const MEMBER_ROLES = ["user", "citizen", "volunteer", "admin"];

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NavLoadProvider>
          <Routes>
            <Route path="/" element={<Landing />} />

            <Route element={<ProtectedRoute role="volunteer" loginTo="/volunteer" />}>
              <Route
                path="/volunteer/dashboard"
                element={<VolunteerDashboardPage />}
              />
            </Route>
            <Route element={<ProtectedRoute role="admin" loginTo="/volunteer" />}>
              <Route path="/admin" element={<AdminPage />} />
            </Route>

            <Route element={<AppLayout />}>
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/volunteer" element={<VolunteerAuthPage />} />
              <Route path="/admin/login" element={<AdminLoginPage />} />

              <Route element={<ProtectedRoute roles={MEMBER_ROLES} />}>
                <Route path="/map" element={<MapPage />} />
                <Route path="/report" element={<ReportPage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="/trends" element={<TrendsPage />} />
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </NavLoadProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
