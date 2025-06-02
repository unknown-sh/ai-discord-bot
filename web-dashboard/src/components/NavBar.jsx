import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "./AuthProvider";
import UserBadge from "./UserBadge";

export default function NavBar() {
  const { user, role, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  // Detect dark mode for contrast
  const theme = document.body.dataset.theme || "light";
  const linkColor = theme === "dark" ? "#7ecbff" : "#0070f3";
  const bgColor = theme === "dark" ? "#23252a" : "#fff";
  const textColor = theme === "dark" ? "#f3f3f3" : "#222";
  const borderColor = theme === "dark" ? "#333" : "#e0e0e0";

  if (loading) return <Loading text="Loading user..." />;

  const navLinks = (
    <>
      <Link to="/admin" style={{ color: linkColor, textDecoration: "none" }} tabIndex={0} aria-label="Admin Page">Admin</Link>
      <Link to="/audit" style={{ color: linkColor, textDecoration: "none" }} tabIndex={0} aria-label="Audit Log">Audit Log</Link>
      <Link to="/config" style={{ color: linkColor, textDecoration: "none" }} tabIndex={0} aria-label="Config Page">Config</Link>
      <Link to="/users" style={{ color: linkColor, textDecoration: "none" }} tabIndex={0} aria-label="Users Page">Users</Link>
      <Link to="/roles" style={{ color: linkColor, textDecoration: "none" }} tabIndex={0} aria-label="Roles Page">Roles</Link>
    </>
  );

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "12px 0",
        borderBottom: `1px solid ${borderColor}`,
        marginBottom: 18,
        background: bgColor,
        color: textColor,
        position: "relative",
        zIndex: 100,
      }}
      aria-label="Main navigation"
    >
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <Link to="/" style={{ fontWeight: 700, fontSize: 20, color: textColor, textDecoration: "none" }} tabIndex={0} aria-label="Dashboard Home">
          AI Bot Dashboard
        </Link>
        <div className="nav-links-desktop" style={{ display: "flex", gap: 18 }}>
          {navLinks}
        </div>
      </div>
      <div className="nav-user" style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <button
          className="nav-hamburger"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          onClick={() => setMenuOpen(m => !m)}
          style={{
            background: "none", border: "none", fontSize: 28, display: "none", cursor: "pointer", color: linkColor,
            marginRight: 8,
          }}
        >
          {menuOpen ? "✕" : "☰"}
        </button>
        <UserBadge user={user} role={role} />
      </div>
      {/* Mobile menu overlay */}
      {menuOpen && (
        <div
          style={{
            position: "fixed", left: 0, top: 0, width: "100vw", height: "100vh",
            background: "rgba(0,0,0,0.42)", zIndex: 2000, display: "flex", flexDirection: "column",
            alignItems: "flex-start", padding: 0, margin: 0,
          }}
        >
          <div
            style={{ background: bgColor, color: textColor, width: 220, minHeight: "100vh", boxShadow: "2px 0 12px #0002", padding: 24 }}
          >
            <button
              onClick={() => setMenuOpen(false)}
              style={{ background: "none", border: "none", fontSize: 28, cursor: "pointer", color: linkColor, marginBottom: 12 }}
              aria-label="Close menu"
            >✕</button>
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              {navLinks}
            </div>
          </div>
        </div>
      )}
      <style>{`
        @media (max-width: 700px) {
          .nav-links-desktop { display: none !important; }
          .nav-hamburger { display: inline !important; }
        }
        @media (min-width: 701px) {
          .nav-links-desktop { display: flex !important; }
          .nav-hamburger { display: none !important; }
        }
      `}</style>
    </nav>
  );
}
