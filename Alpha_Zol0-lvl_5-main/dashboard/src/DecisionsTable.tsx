import React from "react";

type DecisionsTableProps = {
  data: Array<{
    timestamp: string;
    decision: string;
    trend?: string | number | null;
    volatility?: number | null;
    strategy?: string;
  }>;
};

function formatTime(ts: string) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const DecisionsTable: React.FC<DecisionsTableProps> = ({ data }) => {
  if (!data || data.length === 0) return null;
  const sorted = [...data].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 20);
  return (
    <div style={{ marginTop: 24, background: "#181c24", borderRadius: 12, padding: 16 }}>
      <h3>Ostatnie decyzje</h3>
      <table style={{ width: "100%", color: "#fff", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#23283a" }}>
            <th style={{ padding: 8 }}>Czas</th>
            <th style={{ padding: 8 }}>Decyzja</th>
            <th style={{ padding: 8 }}>Trend</th>
            <th style={{ padding: 8 }}>Volatility</th>
            <th style={{ padding: 8 }}>Strategia</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((d, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #333" }}>
              <td style={{ padding: 8 }}>{formatTime(d.timestamp)}</td>
              <td style={{ padding: 8 }}>{d.decision}</td>
              <td style={{ padding: 8 }}>{d.trend ?? "---"}</td>
              <td style={{ padding: 8 }}>{d.volatility ?? "---"}</td>
              <td style={{ padding: 8 }}>{d.strategy ?? "---"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DecisionsTable;
