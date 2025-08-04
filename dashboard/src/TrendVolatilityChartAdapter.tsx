import TrendVolatilityChart from "./TrendVolatilityChart";

// Adapter: converts trend string to number (if possible), omits non-numeric trends
function trendToNumber(trend: unknown): number | null {
  if (typeof trend === "number") return trend;
  if (typeof trend === "string") {
    // Try to parse float
    const num = parseFloat(trend);
    if (!isNaN(num)) return num;
    // Optionally: map known string trends to numbers
    if (trend === "UP") return 1;
    if (trend === "DOWN") return -1;
    if (trend === "SIDE" || trend === "SIDEWAYS") return 0;
  }
  return null;
}

export default function TrendVolatilityChartAdapter({ data }: { data: Array<{ timestamp: string, trend: unknown, volatility: number }> }) {
  if (!data || data.length === 0) return null;
  // Map trend to number or null
  const mapped = data.map(d => ({
    ...d,
    trend: trendToNumber(d.trend),
    volatility: typeof d.volatility === "number" ? d.volatility : null,
  }));
  return <TrendVolatilityChart data={mapped} />;
}
