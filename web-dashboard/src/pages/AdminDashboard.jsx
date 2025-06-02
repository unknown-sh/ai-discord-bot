import React from "react";
import { Link } from "react-router-dom";

function AdminDashboard() {
  return (
    <div style={{ padding: 32 }}>
      <h1>Admin Dashboard</h1>
      <ul style={{ fontSize: 18 }}>
        <li><Link to="/audit">Audit Log</Link></li>
        {/* Add more admin links here, e.g. user/role management, config, etc. */}
      </ul>
    </div>
  );
}

export default AdminDashboard;
