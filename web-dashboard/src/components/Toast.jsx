import React, { createContext, useContext, useState, useCallback } from "react";

const ToastContext = createContext();

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((msg, type = "info", duration = 3000) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(ts => [...ts, { id, msg, type }]);
    setTimeout(() => {
      setToasts(ts => ts.filter(t => t.id !== id));
    }, duration);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div style={{ position: "fixed", top: 24, right: 24, zIndex: 2000 }}>
        {toasts.map(t => (
          <div key={t.id} style={{
            background: t.type === "error" ? "#ffeded" : t.type === "success" ? "#eaffea" : "#f0f0f0",
            color: t.type === "error" ? "#b00" : t.type === "success" ? "#080" : "#222",
            border: "1px solid #ccc", borderLeft: `6px solid ${t.type === "error" ? "#e44" : t.type === "success" ? "#2a2" : "#888"}`,
            borderRadius: 6, padding: "14px 20px", marginBottom: 8, boxShadow: "0 2px 12px #0002", minWidth: 220, fontSize: 16
          }}>
            {t.msg}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
