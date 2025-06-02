// src/api/audit.js
import axios from "axios";
import config from "../dashboard-config.js";
import { getDiscordHeaders } from "./auth.js";

export async function fetchAuditLogs() {
  const headers = await getDiscordHeaders();
  const resp = await axios.get(`${config.apiBaseUrl}/audit/logs`, {
    withCredentials: true,
    headers,
  });
  return resp.data.logs || resp.data || [];
}
