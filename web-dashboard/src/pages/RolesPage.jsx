import React, { useEffect, useState } from "react";
import { fetchRoles } from "../api/roles";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import Table from "../components/Table";

export default function RolesPage() {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchRoles()
      .then(setRoles)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: 32 }}>
      <h2>Role Management</h2>
      {loading ? <Loading text="Loading roles..." /> : null}
      <ErrorMessage error={error} />
      <Table
        columns={[
          { key: "role", label: "Role" },
          { key: "description", label: "Description" },
        ]}
        data={roles}
      />
      <div style={{ marginTop: 32, color: "#888", fontSize: 14 }}>
        <p>Role management is currently read-only. Only superadmins can change roles via the Users page.</p>
      </div>
    </div>
  );
}
