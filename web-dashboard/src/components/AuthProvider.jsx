// src/components/AuthProvider.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { getCurrentDiscordUser } from "../api/auth";
import Loading from "./Loading";

const AuthContext = createContext({ user: null, role: null, loading: true });

export function useAuth() {
  return useContext(AuthContext);
}

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getCurrentDiscordUser().then(u => {
      if (!cancelled) {
        setUser(u);
        setRole(u ? u.role : null);
      }
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  // Remove redirect effect and show login button instead

  function handleLogin() {
    const currentUrl = window.location.href;
    const loginPath = "/api/login/discord";
    window.location.href = `${window.location.origin}${loginPath}?redirect=${encodeURIComponent(currentUrl)}`;
  }

  return (
    <AuthContext.Provider value={{ user, role, loading }}>
      {loading ? (
        <Loading text="Checking authentication…" />
      ) : !user ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: 'var(--bg)', color: 'var(--text)' }}>
          <h2 style={{ color: 'var(--text)' }}>Login Required</h2>
          <button
            onClick={handleLogin}
            style={{
              background: 'var(--primary)', color: 'white', border: 'none', borderRadius: 6, padding: '12px 28px', fontSize: 18, fontWeight: 600, cursor: 'pointer', marginTop: 16, boxShadow: '0 2px 8px #0001', display: 'flex', alignItems: 'center', gap: 10
            }}
            aria-label="Login with Discord"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: 8 }}>
              <path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.0371A19.7363 19.7363 0 003.677 4.3698a.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276c-.598.3428-1.2205.6447-1.8733.8923a.0766.0766 0 00-.0406.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6603a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1835 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1835 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z" fill="white"/>
            </svg>
            Login with Discord
          </button>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
}
