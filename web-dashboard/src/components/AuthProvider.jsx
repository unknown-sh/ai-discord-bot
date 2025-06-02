// src/components/AuthProvider.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { getCurrentDiscordUser } from "../api/auth";

const AuthContext = createContext({ user: null, loading: true });

export function useAuth() {
  return useContext(AuthContext);
}

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    getCurrentDiscordUser().then(u => {
      if (!cancelled) setUser(u);
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  // If not loading and not authenticated, redirect to backend login (Discord OAuth2)
  useEffect(() => {
    if (!loading && !user) {
      // Use backend endpoint that starts the OAuth2 flow
      window.location.href = `${window.location.origin}/api/login/discord?redirect=${encodeURIComponent(window.location.href)}`;
    }
  }, [loading, user]);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {loading ? <div>Checking authentication…</div> : children}
    </AuthContext.Provider>
  );
}
