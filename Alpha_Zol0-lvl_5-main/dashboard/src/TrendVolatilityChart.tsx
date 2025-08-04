import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Props type
type TrendVolatilityChartProps = {
  data: Array<{
    timestamp: string;
    trend: number | null;
    volatility: number | null;
  }>;
};

// Helper: format time as HH:mm
function formatTime(ts: string) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

const TrendVolatilityChart: React.FC<TrendVolatilityChartProps> = ({ data }) => {
  if (!data || data.length === 0) return null;

  // Sort by timestamp ascending, take last 30
  const sorted = [...data]
    .filter((d) => d.volatility !== null)
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .slice(-30);

  // Only render trend if it's a number
  const hasTrend = sorted.some((d) => typeof d.trend === "number" && !isNaN(d.trend));

  return (
    <div style={{ width: "100%", height: 320, background: "#181c24", padding: 16, borderRadius: 12 }}>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={sorted} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
          <CartesianGrid stroke="#333" strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatTime}
            stroke="#aaa"
            tick={{ fontSize: 12 }}
          />
          <YAxis stroke="#aaa" tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: "#222", border: "none" }}
            labelFormatter={(v) => `Czas: ${formatTime(v as string)}`}
          />
          <Legend wrapperStyle={{ color: "#fff" }} />
          {hasTrend && (
            <Line
              type="monotone"
              dataKey="trend"
              name="Trend"
              stroke="#00bcd4"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
              connectNulls
            />
          )}
          <Line
            type="monotone"
            dataKey="volatility"
            name="Volatility"
            stroke="#ff9800"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendVolatilityChart;
