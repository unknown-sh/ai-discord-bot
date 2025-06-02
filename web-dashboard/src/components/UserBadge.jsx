import React from "react";
export default function UserBadge({ user }) {
  if (!user) return null;
  return (
    <span style={{ fontSize: 16, background: "#222", color: "#fff", borderRadius: 12, padding: "2px 10px", marginLeft: 8 }}>
      <img src={`https://cdn.discordapp.com/avatars/${user.userId}/${user.avatar}.png`} alt="avatar" style={{ width: 20, height: 20, borderRadius: "50%", verticalAlign: "middle", marginRight: 6 }} />
      {user.username} <span style={{ color: "#0ff", fontWeight: 600 }}>({user.role})</span>
    </span>
  );
}
