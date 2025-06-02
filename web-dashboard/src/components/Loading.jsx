import React from "react";
export default function Loading({ text = "Loading..." }) {
  return <div style={{ padding: 32, fontSize: 20, color: "#888" }}>{text}</div>;
}
