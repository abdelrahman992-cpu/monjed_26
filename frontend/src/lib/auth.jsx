import { createContext, useContext, useMemo, useState } from "react";
import {
  applyProfileToSession,
  clearSession,
  getLinkedVolunteerId,
  getSession,
  linkVolunteerId,
  setSession,
  toClientSession,
} from "./storage.js";
import {
  loginAdmin as apiLoginAdmin,
  loginUser as apiLoginUser,
  registerUser as apiRegisterUser,
  registerVolunteer as apiRegisterVolunteer,
  setVolunteerAvailability as apiSetAvailability,
  getUserProfile as apiGetUserProfile,
  updateUserProfile as apiUpdateUserProfile,
  toE164,
} from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSessionState] = useState(() => getSession());

  const value = useMemo(() => {
    function persist(next) {
      setSession(next);
      setSessionState(next);
    }

    return {
      session,
      isSignedIn: !!session,
      isUser: session?.role === "user" || session?.role === "citizen",
      isAdmin: session?.role === "admin",
      isVolunteer: session?.role === "volunteer",

      async loginAsUser(identifier, password) {
        const auth = await apiLoginUser({
          identifier: String(identifier || "").trim(),
          password,
        });
        const next = toClientSession(auth);
        persist(next);
        return next;
      },

      async signupUser(profile) {
        const display_name = String(profile.name || "").trim();
        const email = String(profile.email || "").trim().toLowerCase();
        const password = String(profile.password || "");
        if (display_name.length < 2) {
          throw new Error("Full name is required (at least 2 characters).");
        }
        if (!email.includes("@")) {
          throw new Error("A valid email is required.");
        }
        if (password.length < 8) {
          throw new Error("Password must be at least 8 characters.");
        }

        const phoneRaw = String(profile.phone || "").trim();
        const phone = phoneRaw ? toE164(phoneRaw) : null;
        if (phoneRaw && !phone) {
          throw new Error(
            "Phone must be international format, e.g. +254712345678 (or leave it blank)."
          );
        }

        const payload = {
          display_name,
          email,
          password,
          role: "citizen",
          preferred_language: profile.preferred_language || "en",
          accessibility_needs: profile.accessibility_needs || [],
          notification_consent: profile.notification_consent !== false,
        };
        if (phone) payload.phone = phone;
        if (profile.countryCode || profile.zone_id) {
          payload.zone_id = profile.countryCode || profile.zone_id;
        }
        if (profile.country) payload.country = profile.country;

        const auth = await apiRegisterUser(payload);
        const next = toClientSession(auth, {
          zone: profile.zone || "",
          countryCode: profile.countryCode || "",
        });
        persist(next);
        return next;
      },

      async loginAsVolunteer(identifier, password) {
        const auth = await apiLoginUser({
          identifier: String(identifier || "").trim(),
          password,
        });
        if (auth?.user?.role !== "volunteer") {
          throw new Error("This account is not a volunteer account.");
        }
        const userId = auth.user.user_id;
        const volunteerId = getLinkedVolunteerId(userId);
        const next = toClientSession(auth, {
          volunteer_id: volunteerId,
          available: true,
        });
        persist(next);
        return next;
      },

      async signupVolunteer(profile) {
        const phone = toE164(profile.phone);
        const auth = await apiRegisterUser({
          display_name: profile.name,
          email: String(profile.email || "").trim().toLowerCase(),
          password: profile.password,
          phone: phone || undefined,
          role: "volunteer",
          zone_id: profile.zone_id || profile.country || undefined,
          country: profile.country || undefined,
          preferred_language: "en",
          notification_consent: true,
        });

        const skillMap = {
          "First aid": "medical_support",
          Driving: "transportation",
          "Boat / water rescue": "rescue_support",
          Translation: "general_support",
          Logistics: "general_support",
          "Shelter setup": "evacuation",
        };
        const skills = (profile.skills || [])
          .map((s) => skillMap[s] || "general_support")
          .filter((v, i, a) => a.indexOf(v) === i);

        const volunteer = await apiRegisterVolunteer({
          name: profile.name,
          zone_id: profile.zone_id || profile.country || "KE",
          available: true,
          responder_level: "volunteer",
          vehicle_type: profile.vehicleType === "none" ? null : profile.vehicleType,
          capacity: Number(profile.capacity) || 1,
          skills,
        });

        linkVolunteerId(auth.user.user_id, volunteer.volunteer_id);

        const next = toClientSession(auth, {
          volunteer_id: volunteer.volunteer_id,
          available: volunteer.available,
          vehicleType: volunteer.vehicle_type,
          capacity: volunteer.capacity,
          skills: volunteer.skills,
        });
        persist(next);
        return next;
      },

      async loginAsAdmin(identifier, password) {
        const auth = await apiLoginAdmin({
          identifier: String(identifier || "").trim(),
          password,
        });
        const next = toClientSession(auth);
        persist(next);
        return next;
      },

      async refreshProfile() {
        if (!session?.id) return null;
        const profile = await apiGetUserProfile(session.id);
        const next = applyProfileToSession(session, profile);
        persist(next);
        return next;
      },

      async updateProfile(patch) {
        if (!session?.id) return null;
        const body = {};
        if (patch.name != null) body.display_name = patch.name;
        if (patch.title != null) body.role_title = patch.title;
        if (patch.organization != null) body.organization = patch.organization;
        if (patch.email != null) body.work_email = patch.email;
        if (patch.phone != null) {
          const e164 = toE164(patch.phone);
          if (e164) body.phone = e164;
        }
        if (patch.zone_id != null) body.zone_id = patch.zone_id;
        if (patch.country != null) body.country = patch.country;
        if (patch.preferred_language != null) {
          body.preferred_language = patch.preferred_language;
        }
        if (patch.notification_consent != null) {
          body.notification_consent = patch.notification_consent;
        }
        if (patch.accessibility_needs != null) {
          body.accessibility_needs = patch.accessibility_needs;
        }

        const profile = await apiUpdateUserProfile(session.id, body);
        const localExtras = {};
        if (patch.avatar != null) localExtras.avatar = patch.avatar;
        if (patch.zone != null) localExtras.zone = patch.zone;
        if (patch.vehicleType != null) localExtras.vehicleType = patch.vehicleType;
        if (patch.capacity != null) localExtras.capacity = patch.capacity;

        const next = {
          ...applyProfileToSession(session, profile),
          ...localExtras,
        };
        persist(next);
        return next;
      },

      async updateAdminProfile(profile) {
        if (!session?.id) return null;
        const body = {};
        if (profile.name != null) body.display_name = profile.name;
        if (profile.title != null) body.role_title = profile.title;
        if (profile.organization != null) body.organization = profile.organization;
        if (profile.email != null) body.work_email = profile.email;
        if (profile.phone != null) {
          const e164 = toE164(profile.phone);
          if (e164) body.phone = e164;
        }
        if (profile.country != null) body.country = profile.country;
        if (profile.zone != null) body.zone_id = profile.zone_id || session.zone_id;

        const apiProfile = await apiUpdateUserProfile(session.id, body);
        const next = applyProfileToSession(session, apiProfile);
        if (profile.zone != null) next.zone = profile.zone;
        persist(next);
        return next;
      },

      logout() {
        clearSession();
        setSessionState(null);
      },

      async setAvailability(available) {
        if (session?.role !== "volunteer") return;
        const volunteerId = session.volunteer_id || session.id;
        const updated = await apiSetAvailability(volunteerId, available);
        const next = {
          ...session,
          available: updated.available,
          volunteer_id: updated.volunteer_id || volunteerId,
        };
        persist(next);
      },
    };
  }, [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
