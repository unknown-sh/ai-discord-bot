import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import AdminDashboard from "./pages/AdminDashboard";
import AuditLog from "./pages/AuditLog";

import AuthProvider from "./components/AuthProvider";

function App() {
  return (
    <AuthProvider>
      <Router>
        <nav style={{ padding: 16, background: "#222", color: "#fff" }}>
          <Link to="/" style={{ color: "#fff", textDecoration: "none", fontWeight: 700, fontSize: 20 }}>
            AI Discord Bot Dashboard
          </Link>
          <span style={{ marginLeft: 24 }}>
            <Link to="/admin" style={{ color: "#fff", marginRight: 16 }}>Admin</Link>
            <Link to="/audit" style={{ color: "#fff" }}>Audit Log</Link>
          </span>
        </nav>
        <Routes>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/" element={
            <div style={{ fontFamily: 'sans-serif', padding: 32 }}>
              <h1>AI Discord Bot Dashboard</h1>
              <p>Welcome! This dashboard will let you manage bot config, memory, users, and more.</p>
              <p>Use the navigation above to access admin features and audit logs.</p>
            </div>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
