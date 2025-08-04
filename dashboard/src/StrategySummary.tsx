import React from "react";

type StrategySummaryProps = {
  strategies: Array<{ name: string; allocation?: number; sharpe?: number; pnl?: number }>;
};

const StrategySummary: React.FC<StrategySummaryProps> = ({ strategies }) => {
  if (!strategies || strategies.length === 0) return null;
  return (
    <div style={{ marginTop: 24, background: "#181c24", borderRadius: 12, padding: 16 }}>
      <h3>Podsumowanie strategii</h3>
      <table style={{ width: "100%", color: "#fff", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#23283a" }}>
            <th style={{ padding: 8 }}>Strategia</th>
            <th style={{ padding: 8 }}>Alokacja</th>
            <th style={{ padding: 8 }}>Sharpe</th>
            <th style={{ padding: 8 }}>PnL</th>
          </tr>
        </thead>
        <tbody>
          {strategies.map((s, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #333" }}>
              <td style={{ padding: 8 }}>{s.name}</td>
              <td style={{ padding: 8 }}>{s.allocation !== undefined ? (s.allocation * 100).toFixed(1) + "%" : "---"}</td>
              <td style={{ padding: 8 }}>{s.sharpe !== undefined ? s.sharpe.toFixed(2) : "---"}</td>
              <td style={{ padding: 8 }}>{s.pnl !== undefined ? s.pnl.toFixed(2) : "---"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StrategySummary;
