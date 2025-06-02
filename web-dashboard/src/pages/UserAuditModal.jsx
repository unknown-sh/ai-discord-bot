import React, { useEffect, useState } from "react";
import { fetchAuditLogs } from "../api/audit";

export default function UserAuditModal({ user, myRole, onClose, handleModalRoleChange }) {
  const [recentActions, setRecentActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchAuditLogs()
      .then(logs => {
        if (!mounted) return;
        const userLogs = logs.filter(l => (l.user_id === user.userId || l.username === user.username));
        userLogs.sort((a, b) => new Date(b.time || b.timestamp) - new Date(a.time || a.timestamp));
        setRecentActions(userLogs.slice(0, 5));
      })
      .catch(e => { if (mounted) setError(e); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [user]);

  const { showToast } = require("../components/Toast");
  function handleCopy(val, label) {
    navigator.clipboard.writeText(val);
    showToast(`${label} copied!`, "success");
  }

  return (
    <Modal onClose={onClose} ariaLabel="User Details">
      <h3 style={{ marginTop: 0, marginBottom: 18, fontWeight: 600, fontSize: 20 }}>User Details</h3>
      <div style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 14 }}>
        <img src={user.avatar || "https://cdn.discordapp.com/embed/avatars/0.png"} alt="avatar" width={40} height={40} style={{ borderRadius: 20 }} />
        <span style={{ fontWeight: 500, fontSize: 18 }}>{user.username}</span>
      </div>
      <div style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
        <b>User ID:</b> <span style={{ fontFamily: "monospace" }}>{user.userId}</span>
        <button
          onClick={() => handleCopy(user.userId, "User ID")}
          style={{ marginLeft: 8, fontSize: 13, padding: "2px 7px", borderRadius: 4, border: "1px solid #ddd", background: "#f6f6fa", cursor: "pointer" }}
          aria-label="Copy user ID to clipboard"
        >Copy</button>
      </div>
      <div style={{ marginBottom: 14 }}>
        <b>Role:</b> {myRole === "superadmin" ? (
          <select value={user.role} onChange={e => handleModalRoleChange(e.target.value)} style={{ marginLeft: 8 }}>
            <option value="user">user</option>
            <option value="admin">admin</option>
            <option value="superadmin">superadmin</option>
          </select>
        ) : (
          <span style={{ marginLeft: 8 }}>{user.role}</span>
        )}
      </div>
      <div style={{ marginBottom: 10 }}>
        <b>Recent Actions:</b>
        {loading ? (
          <span style={{ color: "#888", marginLeft: 8 }}>Loading...</span>
        ) : error ? (
          <span style={{ color: "#b00", marginLeft: 8 }}>Failed to load audit log</span>
        ) : recentActions.length === 0 ? (
          <span style={{ color: "#888", marginLeft: 8 }}>No recent actions found</span>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8, fontSize: 14 }}>
            <thead>
              <tr style={{ background: "#f4f4f8", color: "#333" }}>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>Time</th>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>Action</th>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>IP</th>
                <th style={{ padding: 6 }}></th>
              </tr>
            </thead>
            <tbody>
              {recentActions.map((log, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: 6, color: "#444" }}>{new Date(log.time || log.timestamp).toLocaleString()}</td>
                  <td style={{ padding: 6, fontFamily: "monospace", color: "#222", maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={log.action}>{log.action.length > 30 ? log.action.slice(0, 27) + "…" : log.action}</td>
                  <td style={{ padding: 6, color: "#888" }}>{log.ip || "-"}</td>
                  <td style={{ padding: 6 }}>
                    <button
                      onClick={() => handleCopy(log.action, "Action")}
                      aria-label="Copy action"
                      style={{ fontSize: 12, border: "1px solid #ddd", background: "#f6f6fa", borderRadius: 4, padding: "2px 6px", cursor: "pointer" }}
                    >Copy</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Modal>
  );
}
