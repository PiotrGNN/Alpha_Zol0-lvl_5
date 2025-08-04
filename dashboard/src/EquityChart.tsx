import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

type EquityChartProps = {
  data: Array<{ timestamp: string; equity: number }>;
};

function formatTime(ts: string) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const EquityChart: React.FC<EquityChartProps> = ({ data }) => {
  if (!data || data.length === 0) return null;
  const sorted = [...data].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()).slice(-50);
  return (
    <div style={{ width: "100%", height: 320, background: "#181c24", padding: 16, borderRadius: 12, marginTop: 24 }}>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={sorted} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
          <CartesianGrid stroke="#333" strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tickFormatter={formatTime} stroke="#aaa" tick={{ fontSize: 12 }} />
          <YAxis stroke="#aaa" tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ background: "#222", border: "none" }} labelFormatter={v => `Czas: ${formatTime(v as string)}`} />
          <Legend wrapperStyle={{ color: "#fff" }} />
          <Line type="monotone" dataKey="equity" name="Equity" stroke="#4caf50" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EquityChart;
