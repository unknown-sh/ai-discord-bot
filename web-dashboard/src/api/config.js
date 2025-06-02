import axios from "axios";
import config from "../dashboard-config.js";
import { getDiscordHeaders } from "./auth.js";

// Fetch all config (keys/values, masking sensitive for non-superadmin)
export async function fetchConfig() {
  const headers = await getDiscordHeaders();
  const resp = await axios.get(`${config.apiBaseUrl}/show/config`, {
    withCredentials: true,
    headers,
  });
  // API returns { text: "Current config..." }, so parse text
  // Example line: KEY: value
  const lines = (resp.data.text || "").split(/\n/).slice(1); // skip header line
  return lines.filter(Boolean).map(line => {
    const [key, ...rest] = line.split(": ");
    return { key: key.trim(), value: rest.join(": ").trim() };
  });
}

// Set a config key
export async function setConfig(key, value) {
  const headers = await getDiscordHeaders();
  await axios.post(`${config.apiBaseUrl}/show/config/${key}`, { value }, {
    withCredentials: true,
    headers,
  });
}

// Delete a config key
export async function deleteConfig(key) {
  const headers = await getDiscordHeaders();
  await axios.delete(`${config.apiBaseUrl}/show/config/${key}`, {
    withCredentials: true,
    headers,
  });
}
