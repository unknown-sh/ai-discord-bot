import React from "react";
export default function ErrorMessage({ error }) {
  if (!error) return null;
  return (
    <div style={{ padding: 24, color: "#b00", background: "#fee", border: "1px solid #fbb", borderRadius: 6, marginBottom: 24 }}>
      <strong>Error:</strong> {typeof error === "string" ? error : error.message || String(error)}
    </div>
  );
}
