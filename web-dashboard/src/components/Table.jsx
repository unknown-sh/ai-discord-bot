import React from "react";
export default function Table({ columns, data }) {
  return (
    <div style={{ width: "100%", overflowX: "auto", marginBottom: 32 }}>
      <table
        style={{ width: "100%", borderCollapse: "collapse", minWidth: 480 }}
        role="table"
        aria-label="Data table"
      >
        <thead>
          <tr>
            {columns.map(col => (
              <th
                key={col.key}
                style={{
                  borderBottom: "2px solid #444",
                  textAlign: "left",
                  padding: 10,
                  background: "#f4f4f8",
                  color: "#222",
                  fontWeight: 700,
                  fontSize: 16
                }}
                scope="col"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={columns.length} style={{ textAlign: "center", color: "#888", padding: 16 }}>No data found.</td></tr>
          ) : data.map((row, i) => (
            <tr
              key={i}
              tabIndex={0}
              style={{ outline: "none", transition: "background 0.2s" }}
              onFocus={e => e.currentTarget.style.background = "#e6f3ff"}
              onBlur={e => e.currentTarget.style.background = ""}
              aria-rowindex={i+2}
            >
              {columns.map(col => (
                <td
                  key={col.key}
                  style={{
                    padding: 10,
                    borderBottom: "1px solid #ddd",
                    background: "#fff",
                    color: "#222",
                    fontSize: 15
                  }}
                  aria-colindex={columns.indexOf(col)+1}
                >
                  {row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

