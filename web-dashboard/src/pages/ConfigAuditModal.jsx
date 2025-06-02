import React, { useEffect, useState } from "react";
import { fetchAuditLogs } from "../api/audit";

export default function ConfigAuditModal({ config, role, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchAuditLogs()
      .then(logs => {
        if (!mounted) return;
        // Filter audit logs for this config key (by key or details)
        const key = config.key;
        const keyLogs = logs.filter(l => {
          // Try to match config key in action or details
          if ((l.action || "").toLowerCase().includes(key.toLowerCase())) return true;
          if (l.details && typeof l.details === "object") {
            if (l.details.key === key) return true;
            if (l.details.config_key === key) return true;
          }
          return false;
        });
        keyLogs.sort((a, b) => new Date(b.time || b.timestamp) - new Date(a.time || a.timestamp));
        setHistory(keyLogs.slice(0, 5));
      })
      .catch(e => { if (mounted) setError(e); })
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [config]);

  const { showToast } = require("../components/Toast");
  function handleCopy(val, label) {
    navigator.clipboard.writeText(val);
    showToast(`${label} copied!`, "success");
  }

  return (
    <Modal onClose={onClose} ariaLabel="Config Key Details">
      <h3 style={{ marginTop: 0, marginBottom: 18, fontWeight: 600, fontSize: 20 }}>Config Key Details</h3>
      <div style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
        <b>Key:</b> <span style={{ fontFamily: "monospace" }}>{config.key}</span>
        <button
          onClick={() => handleCopy(config.key, "Key")}
          style={{ marginLeft: 8, fontSize: 13, padding: "2px 7px", borderRadius: 4, border: "1px solid #ddd", background: "#f6f6fa", cursor: "pointer" }}
          aria-label="Copy key to clipboard"
        >Copy</button>
      </div>
      <div style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
        <b>Value:</b> {role === "superadmin" ? (
          <span style={{ fontFamily: "monospace", maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={config.value}>{String(config.value).length > 36 ? String(config.value).slice(0,33) + "…" : String(config.value)}</span>
        ) : (
          <span style={{ fontFamily: "monospace" }}>{String(config.value).replace(/./g, "*")}</span>
        )}
        <button
          onClick={() => handleCopy(config.value, "Value")}
          style={{ marginLeft: 8, fontSize: 13, padding: "2px 7px", borderRadius: 4, border: "1px solid #ddd", background: "#f6f6fa", cursor: "pointer" }}
          aria-label="Copy value to clipboard"
        >Copy</button>
      </div>
      <div style={{ marginBottom: 14 }}>
        <b>Description:</b> <span style={{ color: "#666" }}>[description placeholder]</span>
      </div>
      <div style={{ marginBottom: 10 }}>
        <b>Audit/History:</b>
        {loading ? (
          <span style={{ color: "#888", marginLeft: 8 }}>Loading...</span>
        ) : error ? (
          <span style={{ color: "#b00", marginLeft: 8 }}>Failed to load audit log</span>
        ) : history.length === 0 ? (
          <span style={{ color: "#888", marginLeft: 8 }}>No recent changes found</span>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 8, fontSize: 14 }}>
            <thead>
              <tr style={{ background: "#f4f4f8", color: "#333" }}>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>Time</th>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>Action</th>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>User</th>
                <th style={{ padding: 6, textAlign: "left", fontWeight: 600 }}>Old → New</th>
                <th style={{ padding: 6 }}></th>
              </tr>
            </thead>
            <tbody>
              {history.map((log, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: 6, color: "#444" }}>{new Date(log.time || log.timestamp).toLocaleString()}</td>
                  <td style={{ padding: 6, fontFamily: "monospace", color: "#222", maxWidth: 120, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={log.action}>{log.action.length > 24 ? log.action.slice(0, 21) + "…" : log.action}</td>
                  <td style={{ padding: 6, color: "#888" }}>{log.username || log.user_id || "-"}</td>
                  <td style={{ padding: 6, color: "#888" }}>
                    {log.details && (log.details.old_value !== undefined || log.details.new_value !== undefined) ? (
                      <span>
                        {log.details.old_value !== undefined && <span style={{ fontFamily: "monospace", color: "#a44" }}>{String(log.details.old_value).length > 12 ? String(log.details.old_value).slice(0,10) + "…" : log.details.old_value}</span>}
                        {log.details.old_value !== undefined && log.details.new_value !== undefined && <span> → </span>}
                        {log.details.new_value !== undefined && <span style={{ fontFamily: "monospace", color: "#080" }}>{String(log.details.new_value).length > 12 ? String(log.details.new_value).slice(0,10) + "…" : log.details.new_value}</span>}
                      </span>
                    ) : <span>-</span>}
                  </td>
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
