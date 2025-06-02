// src/api/auth.js
// Discord OAuth2 + Supabase role enforcement utility
import axios from "axios";
import config from "../dashboard-config.js";

// Returns a promise that resolves to { userId, username, avatar, role } or null if not authed or not superadmin
export async function getCurrentDiscordUser() {
  // Backend endpoint must implement /auth/me or similar, returning Discord user info
  try {
    const resp = await axios.get(`${config.apiBaseUrl}/auth/me`, { withCredentials: true });
    const { id, username, avatar, role } = resp.data;
    if (!id || !username) return null;
    if (role !== "superadmin") return null; // Only allow superadmin
    return { userId: id, username, avatar, role };
  } catch {
    return null;
  }
}

// Returns headers for API calls, or throws if not authed/superadmin
export async function getDiscordHeaders() {
  const user = await getCurrentDiscordUser();
  if (!user) throw new Error("Not authenticated as Discord superadmin");
  return {
    "X-Discord-User-ID": user.userId,
    "X-Discord-Username": user.username,
  };
}
