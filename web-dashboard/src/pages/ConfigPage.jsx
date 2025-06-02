import React, { useEffect, useState } from "react";
import { useAuth } from "../components/AuthProvider";
import { fetchConfig, setConfig, deleteConfig } from "../api/config";
import { useToast } from "../components/Toast";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import Table from "../components/Table";

export default function ConfigPage() {
  const toast = useToast();
  const { role } = useAuth();
  const [config, setConfigState] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editKey, setEditKey] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchConfig()
      .then(setConfigState)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  function startEdit(key, value) {
    setEditKey(key);
    setEditValue(value);
  }
  async function handleSaveEdit() {
    setSaving(true);
    try {
      await setConfig(editKey, editValue);
      setConfigState(cfg => cfg.map(row => row.key === editKey ? { ...row, value: editValue } : row));
      setEditKey(null);
      toast.showToast("Config key updated!", "success");
    } catch (e) {
      setError(e);
    } finally {
      setSaving(false);
    }
  }
  async function handleDelete(key) {
    if (!window.confirm(`Delete config key "${key}"? This cannot be undone.`)) return;
    setSaving(true);
    try {
      await deleteConfig(key);
      setConfigState(cfg => cfg.filter(row => row.key !== key));
      toast.showToast("Config key deleted!", "success");
    } catch (e) {
      setError(e);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ padding: 32 }}>
      <h2>Config Management</h2>
      {loading ? <Loading text="Loading config..." /> : null}
      <ErrorMessage error={error} />
      <div style={{ marginBottom: 18 }}>
        <input
          type="text"
          placeholder="Search config by key or value..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: 6, width: 320, fontSize: 16 }}
        />
      </div>
      <Table
        columns={[
          { key: "key", label: "Key" },
          { key: "value", label: "Value" },
          { key: "actions", label: "Actions" },
        ]}
        data={config.filter(row =>
          !search ||
          row.key.toLowerCase().includes(search.toLowerCase()) ||
          (row.value && String(row.value).toLowerCase().includes(search.toLowerCase()))
        ).map(row => ({
          key: (
            <span
              role="button"
              style={{ cursor: "pointer", color: "#0070f3", textDecoration: "underline" }}
              onClick={() => setModalConfig(row)}
              tabIndex={0}
              aria-label={`Open details for config key ${row.key}`}
              onKeyDown={e => { if (e.key === "Enter" || e.key === " " || e.keyCode === 32) setModalConfig(row); }}
            >
              {row.key}
            </span>
          ),
          value: editKey === row.key ? (
            <input value={editValue} onChange={e => setEditValue(e.target.value)} style={{ width: 200 }} />
          ) : row.value,
          actions: (
            <>
              {editKey === row.key ? (
                <>
                  <button onClick={handleSaveEdit} disabled={saving}>Save</button>
                  <button onClick={() => setEditKey(null)} disabled={saving}>Cancel</button>
                </>
              ) : (
                <>
                  <button onClick={() => startEdit(row.key, row.value)} disabled={!!editKey || saving}>Edit</button>
                  {role === "superadmin" && (
                    <button onClick={() => handleDelete(row.key)} disabled={saving}>Delete</button>
                  )}
                </>
              )}
            </>
          )
        }))}
      />
      {modalConfig && (
        <ConfigAuditModal
          config={modalConfig}
          role={role}
          onClose={() => setModalConfig(null)}
        />
      )}



      <div style={{ marginTop: 32, color: "#888", fontSize: 14 }}>
        <p>Note: Sensitive values are masked. Only superadmins can delete config keys.</p>
      </div>
      <hr style={{ margin: "32px 0" }} />
      <h3>Add or Update Config Key</h3>
      <form
        onSubmit={async e => {
          e.preventDefault();
          if (!addKey.trim()) {
            setAddError("Key is required");
            return;
          }
          setAddError(null);
          setSaving(true);
          try {
            await setConfig(addKey.trim(), addValue);
            setAddSuccess(`Config key "${addKey.trim()}" set successfully.`);
            toast.showToast("Config key set!", "success");
            setAddKey("");
            setAddValue("");
            // Reload config table
            const cfg = await fetchConfig();
            setConfigState(cfg);
          } catch (err) {
            setAddError(err?.response?.data?.detail || String(err));
            toast.showToast("Failed to set config key", "error");
          } finally {
            setSaving(false);
            setTimeout(() => setAddSuccess(null), 2000);
          }
        }}
        style={{ marginTop: 16 }}
      >
        <input
          type="text"
          placeholder="Config key (e.g. AI_PROVIDER)"
          value={addKey}
          onChange={e => setAddKey(e.target.value)}
          style={{ marginRight: 8, padding: 6, width: 200 }}
          disabled={saving}
        />
        <input
          type="text"
          placeholder="Value"
          value={addValue}
          onChange={e => setAddValue(e.target.value)}
          style={{ marginRight: 8, padding: 6, width: 200 }}
          disabled={saving}
        />
        <button type="submit" disabled={saving || !addKey.trim()}>Set Config</button>
        {addError && <span style={{ color: "#b00", marginLeft: 16 }}>{addError}</span>}
        {addSuccess && <span style={{ color: "green", marginLeft: 16 }}>{addSuccess}</span>}
      </form>
    </div>
  );
}
