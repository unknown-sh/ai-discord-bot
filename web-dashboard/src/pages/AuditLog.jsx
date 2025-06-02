import React, { useEffect, useState } from "react";
import { fetchAuditLogs } from "../api/audit";

function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAuditLogs()
      .then(setLogs)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading audit log...</div>;
  if (error) return <div style={{color: 'red'}}>Error loading audit log: {String(error)}</div>;

  return (
    <div style={{ padding: 24 }}>
      <h2>Audit Log</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ borderBottom: '1px solid #ccc' }}>Time</th>
            <th style={{ borderBottom: '1px solid #ccc' }}>User</th>
            <th style={{ borderBottom: '1px solid #ccc' }}>Action</th>
            <th style={{ borderBottom: '1px solid #ccc' }}>IP</th>
            <th style={{ borderBottom: '1px solid #ccc' }}>User-Agent</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr><td colSpan={5} style={{ textAlign: 'center', color: '#888' }}>No audit entries found.</td></tr>
          ) : logs.map((log, i) => (
            <tr key={i}>
              <td>{new Date(log.time || log.timestamp).toLocaleString()}</td>
              <td>{log.username || log.user_id}</td>
              <td>{log.action}</td>
              <td>{log.ip || '-'}</td>
              <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.user_agent || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AuditLog;
