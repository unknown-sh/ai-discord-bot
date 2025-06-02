import axios from "axios";
import config from "../dashboard-config.js";
import { getDiscordHeaders } from "./auth.js";

// Fetch all user roles (userId, username, role)
export async function fetchUsers() {
  const headers = await getDiscordHeaders();
  const resp = await axios.get(`${config.apiBaseUrl}/acl/all`, {
    withCredentials: true,
    headers,
  });
  // API returns a list of { user_id, username, role }
  return (resp.data || []).map(u => ({
    userId: u.user_id,
    username: u.username,
    role: u.role,
  }));
}

// Set user role
export async function setUserRole(userId, role) {
  const headers = await getDiscordHeaders();
  await axios.post(`${config.apiBaseUrl}/acl/set`, {
    user_id: userId,
    role,
  }, {
    withCredentials: true,
    headers,
  });
}
