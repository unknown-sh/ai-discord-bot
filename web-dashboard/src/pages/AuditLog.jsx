import React, { useEffect, useState } from "react";
import { fetchAuditLogs } from "../api/audit";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import Table from "../components/Table";
import { Link } from "react-router-dom";

function toCSV(logs) {
  const header = ["Time", "User", "Action", "IP", "User-Agent"];
  const rows = logs.map(log => [
    new Date(log.time || log.timestamp).toLocaleString(),
    log.username || log.user_id,
    log.action,
    log.ip || "-",
    (log.user_agent || "-").replace(/\n/g, " ")
  ]);
  return [header, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, "\"\"")}"`).join(",")).join("\n");
}

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ user: "", action: "" });
  const [page, setPage] = useState(1);
  const [modalLog, setModalLog] = useState(null); // <-- Add this line
  const pageSize = 25;

  useEffect(() => {
    setLoading(true);
    fetchAuditLogs()
      .then(setLogs)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  // Advanced filtering: user, action, IP, date range
  function advancedFilter(logs, filter) {
    return logs.filter(log => {
      // User
      if (filter.user && !((log.username || log.user_id || "").toLowerCase().includes(filter.user.toLowerCase()))) return false;
      // Action
      if (filter.action && !(log.action || "").toLowerCase().includes(filter.action.toLowerCase())) return false;
      // IP
      if (filter.ip && !(log.ip || "").includes(filter.ip)) return false;
      // Date range
      if (filter.startDate) {
        const logDate = new Date(log.time || log.timestamp);
        if (logDate < new Date(filter.startDate)) return false;
      }
      if (filter.endDate) {
        const logDate = new Date(log.time || log.timestamp);
        // Add 1 day to include the end date
        if (logDate > new Date(new Date(filter.endDate).getTime() + 24*60*60*1000)) return false;
      }
      return true;
    });
  }
  const filtered = advancedFilter(logs, filter);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageLogs = filtered.slice((page-1)*pageSize, page*pageSize);

  function handleExportCSV() {
    const csv = toCSV(filtered);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "audit-log.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Audit Log</h2>
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="Filter by user..."
          value={filter.user}
          onChange={e => { setFilter(f => ({ ...f, user: e.target.value })); setPage(1); }}
          style={{ padding: 6, fontSize: 15, width: 160 }}
        />
        <input
          type="text"
          placeholder="Filter by action..."
          value={filter.action}
          onChange={e => { setFilter(f => ({ ...f, action: e.target.value })); setPage(1); }}
          style={{ padding: 6, fontSize: 15, width: 140 }}
        />
        <input
          type="text"
          placeholder="Filter by IP..."
          value={filter.ip || ""}
          onChange={e => { setFilter(f => ({ ...f, ip: e.target.value })); setPage(1); }}
          style={{ padding: 6, fontSize: 15, width: 120 }}
        />
        <label style={{ fontSize: 15 }}>
          From:
          <input
            type="date"
            value={filter.startDate || ""}
            onChange={e => { setFilter(f => ({ ...f, startDate: e.target.value })); setPage(1); }}
            style={{ marginLeft: 4, marginRight: 8 }}
          />
        </label>
        <label style={{ fontSize: 15 }}>
          To:
          <input
            type="date"
            value={filter.endDate || ""}
            onChange={e => { setFilter(f => ({ ...f, endDate: e.target.value })); setPage(1); }}
            style={{ marginLeft: 4 }}
          />
        </label>
        <button onClick={handleExportCSV} style={{ marginLeft: 16, padding: "6px 16px", fontSize: 15 }}>Export CSV</button>
      </div>
      {loading ? <Loading text="Loading audit log..." /> : null}
      <ErrorMessage error={error} />
      <Table
        columns={[
          { key: "time", label: "Time" },
          { key: "user", label: "User" },
          { key: "action", label: "Action" },
          { key: "ip", label: "IP" },
          { key: "user_agent", label: "User-Agent" },
        ]}
        data={pageLogs.map((log, idx) => ({
          time: new Date(log.time || log.timestamp).toLocaleString(),
          user: log.username || log.user_id,
          action: log.action,
          ip: log.ip || "-",
          user_agent: log.user_agent || "-",
          _raw: log,
          _rowIndex: idx
        }))}
        onRowClick={row => setModalLog(row._raw)}
      />

      {modalLog && (
        <Modal onClose={() => setModalLog(null)} ariaLabel="Audit Log Details">
          <h3 style={{ marginTop: 0, marginBottom: 16 }}>Audit Log Entry Details</h3>
          <div style={{ marginBottom: 12 }}>
            <b>Time:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{new Date(modalLog.time || modalLog.timestamp).toLocaleString()}</span>
            <button
              onClick={() => navigator.clipboard.writeText(new Date(modalLog.time || modalLog.timestamp).toLocaleString())}
              style={{ marginLeft: 8, fontSize: 13 }}
              aria-label="Copy timestamp"
            >Copy</button>
          </div>
          <div style={{ marginBottom: 12 }}>
            <b>User:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{modalLog.username || modalLog.user_id}</span>
            <button
              onClick={() => navigator.clipboard.writeText(modalLog.username || modalLog.user_id)}
              style={{ marginLeft: 8, fontSize: 13 }}
              aria-label="Copy user"
            >Copy</button>
          </div>
          <div style={{ marginBottom: 12 }}>
            <b>Action:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{modalLog.action}</span>
            <button
              onClick={() => navigator.clipboard.writeText(modalLog.action)}
              style={{ marginLeft: 8, fontSize: 13 }}
              aria-label="Copy action"
            >Copy</button>
          </div>
          <div style={{ marginBottom: 12 }}>
            <b>IP:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{modalLog.ip || "-"}</span>
            <button
              onClick={() => navigator.clipboard.writeText(modalLog.ip || "-")}
              style={{ marginLeft: 8, fontSize: 13 }}
              aria-label="Copy IP"
            >Copy</button>
          </div>
          <div style={{ marginBottom: 12 }}>
            <b>User-Agent:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{modalLog.user_agent || "-"}</span>
            <button
              onClick={() => navigator.clipboard.writeText(modalLog.user_agent || "-")}
              style={{ marginLeft: 8, fontSize: 13 }}
              aria-label="Copy user-agent"
            >Copy</button>
          </div>
          {modalLog.details && (
            <div style={{ marginBottom: 12 }}>
              <b>Details:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{JSON.stringify(modalLog.details)}</span>
              <button
                onClick={() => navigator.clipboard.writeText(JSON.stringify(modalLog.details))}
                style={{ marginLeft: 8, fontSize: 13 }}
                aria-label="Copy details"
              >Copy</button>
            </div>
          )}
          {/* Show all other fields for completeness */}
          {Object.entries(modalLog).filter(([k]) => !["time","timestamp","username","user_id","action","ip","user_agent","details"].includes(k)).map(([k, v]) => (
            <div style={{ marginBottom: 12 }} key={k}>
              <b>{k}:</b> <span style={{ fontFamily: "monospace", background: "#f6f6fa", padding: "2px 6px", borderRadius: 4 }}>{String(v)}</span>
              <button
                onClick={() => navigator.clipboard.writeText(String(v))}
                style={{ marginLeft: 8, fontSize: 13 }}
                aria-label={`Copy ${k}`}
              >Copy</button>
            </div>
          ))}
        </Modal>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <button disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Prev</button>
        <span>Page {page} of {totalPages}</span>
        <button disabled={page >= totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))}>Next</button>
      </div>
      <div style={{ marginTop: 18, color: "#888", fontSize: 14 }}>
        Showing {pageLogs.length} of {filtered.length} filtered entries ({logs.length} total log entries loaded)
      </div>
    </div>
  );
}
