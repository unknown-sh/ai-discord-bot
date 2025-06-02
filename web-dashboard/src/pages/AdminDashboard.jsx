import { useAuth } from "../components/AuthProvider";
import UserBadge from "../components/UserBadge";
import React from "react";
import { Link } from "react-router-dom";

export default function AdminDashboard() {
  const { user, role } = useAuth();
  return (
    <div style={{ padding: 32 }}>
      <h1>Admin Dashboard</h1>
      <div style={{ marginBottom: 24 }}>
        <UserBadge user={user} />
        <span style={{ marginLeft: 16, fontSize: 16, color: "#888" }}>
          Welcome, {user ? user.username : "..."}! Your role: <b>{role}</b>
        </span>
      </div>
      <div style={{ marginBottom: 32 }}>
        <p>Use the quick links below to manage the Discord bot system:</p>
      </div>
      <ul style={{ fontSize: 18, listStyle: "none", padding: 0 }}>
        <li><Link to="/config">Config Management</Link></li>
        <li><Link to="/users">User Management</Link></li>
        <li><Link to="/roles">Role Management</Link></li>
        <li><Link to="/audit">Audit Log</Link></li>
      </ul>
      <div style={{ marginTop: 32, color: "#aaa", fontSize: 14 }}>
        <p>Note: Some actions may require superadmin privileges.</p>
      </div>
    </div>
  );
}
