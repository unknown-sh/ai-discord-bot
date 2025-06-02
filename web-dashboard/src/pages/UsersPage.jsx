import React, { useEffect, useState } from "react";
import { useAuth } from "../components/AuthProvider";
import { fetchUsers, setUserRole } from "../api/users";
import { useToast } from "../components/Toast";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import Table from "../components/Table";
import { Link } from "react-router-dom";

export default function UsersPage() {
  const toast = useToast();
  const { role: myRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editId, setEditId] = useState(null);
  const [editRole, setEditRole] = useState("");
  const [saving, setSaving] = useState(false);
  // Add missing search state variables
  const [searchUsername, setSearchUsername] = useState("");
  const [searchUserId, setSearchUserId] = useState("");
  const [searchRole, setSearchRole] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchUsers()
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  function startEdit(userId, role) {
    setEditId(userId);
    setEditRole(role);
  }
  async function handleSaveEdit() {
    setSaving(true);
    try {
      await setUserRole(editId, editRole);
      setUsers(us => us.map(u => u.userId === editId ? { ...u, role: editRole } : u));
      setEditId(null);
      toast.showToast("User role updated!", "success");
    } catch (e) {
      setError(e);
      toast.showToast("Failed to update user role", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ padding: 32 }}>
      <h2>User Management</h2>
      {loading ? <Loading text="Loading users..." /> : null}
      <ErrorMessage error={error} />
      <div style={{ marginBottom: 18, display: "flex", gap: 12 }}>
        <input
          type="text"
          placeholder="Search by username..."
          value={searchUsername}
          onChange={e => setSearchUsername(e.target.value)}
          style={{ padding: 6, width: 180 }}
        />
        <input
          type="text"
          placeholder="Search by user ID..."
          value={searchUserId}
          onChange={e => setSearchUserId(e.target.value)}
          style={{ padding: 6, width: 180 }}
        />
        <input
          type="text"
          placeholder="Search by role..."
          value={searchRole}
          onChange={e => setSearchRole(e.target.value)}
          style={{ padding: 6, width: 140 }}
        />
      </div>
      <Table
        columns={[
          { key: "userId", label: "User ID" },
          { key: "username", label: "Username" },
          { key: "role", label: "Role" },
          { key: "actions", label: "Actions" },
        ]}
        data={users.filter(row =>
          (!searchUsername || (row.username && row.username.toLowerCase().includes(searchUsername.toLowerCase()))) &&
          (!searchUserId || (row.userId && row.userId.toLowerCase().includes(searchUserId.toLowerCase()))) &&
          (!searchRole || (row.role && row.role.toLowerCase().includes(searchRole.toLowerCase())))
        ).map(row => ({
          userId: (
            <span
              role="button"
              style={{ cursor: "pointer", color: "#0070f3", textDecoration: "underline" }}
              onClick={() => setModalUser(row)}
              tabIndex={0}
              aria-label={`Open details for user ${row.username}`}
              onKeyDown={e => { if (e.key === "Enter" || e.key === " " || e.keyCode === 32) setModalUser(row); }}
            >
              {row.userId}
            </span>
          ),
          username: row.username,
          role: editId === row.userId ? (
            <select value={editRole} onChange={e => setEditRole(e.target.value)}>
              <option value="user">user</option>
              <option value="admin">admin</option>
              <option value="superadmin">superadmin</option>
            </select>
          ) : row.role,
          actions: (
            <>
              {myRole === "superadmin" && (
                editId === row.userId ? (
                  <>
                    <button onClick={handleSaveEdit} disabled={saving}>Save</button>
                    <button onClick={() => setEditId(null)} disabled={saving}>Cancel</button>
                  </>
                ) : (
                  <button onClick={() => startEdit(row.userId, row.role)} disabled={!!editId || saving}>Edit Role</button>
                )
              )}
            </>
          )
        }))}
      />
      {modalUser && (
        <UserAuditModal
          user={modalUser}
          myRole={myRole}
          onClose={() => setModalUser(null)}
          handleModalRoleChange={handleModalRoleChange}
        />
      )}



      <div style={{ marginTop: 32, color: "#888", fontSize: 14 }}>
        <p>Only superadmins can change user roles.</p>
      </div>
    </div>
  );
}
