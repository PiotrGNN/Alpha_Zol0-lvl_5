import React, { useEffect, useState } from 'react';
import TrendVolatilityChartAdapter from './TrendVolatilityChartAdapter';
import EquityChart from './EquityChart';
import PnLChart from './PnLChart';
import DecisionsTable from './DecisionsTable';
import StatusIndicator from './StatusIndicator';
import StrategySummary from './StrategySummary';
import PositionTable from './PositionTable';
import ClosedPositionsTable from './ClosedPositionsTable';

const API_URL = import.meta.env.VITE_API_URL;

type StrategyData = {
  strategy?: string;
  cooldown?: string;
  modes?: string;
  params?: string;
  strategies?: string[];
};

type PerformanceData = {
  pnl?: number;
  winrate?: number;
  drawdown?: number;
  open_trades?: number;
  trades?: number;
  sharpe?: number;
  sortino?: number;
};

type Metric = {
  timestamp: string;
  trend?: string;
  volatility?: number;
  tick?: number;
};

type Decision = {
  timestamp: string;
  decision: string;
  symbol?: string;
  price?: number;
  volume?: number;
  [key: string]: string | number | undefined;
};

type Status = {
  api?: boolean;
  bot?: boolean;
};

const DashboardStatus: React.FC = () => {
  const [strategyData, setStrategyData] = useState<StrategyData | null>(null);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [metricsData, setMetricsData] = useState<Metric[] | null>(null);
  type EquityPoint = {
    timestamp: string;
    equity: number;
    [key: string]: string | number;
  };
  const [equityData, setEquityData] = useState<EquityPoint[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [status, setStatus] = useState<Status | null>(null);
  type ErrorState = {
    strategy: string | null;
    performance: string | null;
    metrics: string | null;
    equity: string | null;
    decisions: string | null;
    status: string | null;
  };
  const [error, setError] = useState<ErrorState>({
    strategy: null,
    performance: null,
    metrics: null,
    equity: null,
    decisions: null,
    status: null
  });

  useEffect(() => {
    let isMounted = true;
    const fetchEquity = () => {
      setError((e) => ({ ...e, equity: null }));
      fetch(`${API_URL}/equity`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted && Array.isArray(data)) {
            setEquityData(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setEquityData([]);
            setError((e) => ({ ...e, equity: 'Błąd API' }));
          }
        });
    };
    fetchEquity();
    const interval = setInterval(fetchEquity, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchDecisions = () => {
      setError((e) => ({ ...e, decisions: null }));
      fetch(`${API_URL}/decisions?limit=20`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted && Array.isArray(data)) {
            setDecisions(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setDecisions([]);
            setError((e) => ({ ...e, decisions: 'Błąd API' }));
          }
        });
    };
    fetchDecisions();
    const interval = setInterval(fetchDecisions, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchStatus = () => {
      setError((e) => ({ ...e, status: null }));
      fetch(`${API_URL}/status`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted) {
            setStatus(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setStatus(null);
            setError((e) => ({ ...e, status: 'Błąd API' }));
          }
        });
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchStrategy = () => {
      setError((e) => ({ ...e, strategy: null }));
      fetch(`${API_URL}/strategy`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted) {
            setStrategyData(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setStrategyData(null);
            setError((e) => ({ ...e, strategy: 'Błąd API' }));
          }
        });
    };
    fetchStrategy();
    const interval = setInterval(fetchStrategy, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchPerformance = () => {
      setError((e) => ({ ...e, performance: null }));
      fetch(`${API_URL}/performance`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted) {
            setPerformanceData(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setPerformanceData(null);
            setError((e) => ({ ...e, performance: 'Błąd API' }));
          }
        });
    };
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const fetchMetrics = () => {
      setError((e) => ({ ...e, metrics: null }));
      fetch(`${API_URL}/metrics`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then(data => {
          if (isMounted) {
            setMetricsData(data);
          }
        })
        .catch(() => {
          if (isMounted) {
            setMetricsData(null);
            setError((e) => ({ ...e, metrics: 'Błąd API' }));
          }
        });
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  const showValue = (val: string | number | undefined | null) => (val === null || val === undefined || val === '' ? '---' : val);
  const tradesCount = decisions && decisions.length > 0
    ? decisions.filter(d => d.decision && ["BUY", "SELL", "buy", "sell"].includes(d.decision)).length
    : 0;
  const lastMetric = metricsData && metricsData.length > 0 ? metricsData[metricsData.length - 1] : null;

  return (
    <div style={{ padding: 24, color: '#fff', background: '#181c24', minHeight: '100vh' }}>
      <h2>Status Dashboard</h2>
      <div style={{ marginBottom: 16 }}>
        <StatusIndicator status={!!status?.api} label="API" />
        <StatusIndicator status={!!status?.bot} label="Bot" />
      </div>
      <div style={{ marginBottom: 8 }}>
        <strong>Strategia:</strong> {error.strategy ? error.strategy : showValue(strategyData?.strategy)}
        {' | '}<strong>Cooldown:</strong> {error.strategy ? error.strategy : showValue(strategyData?.cooldown)}
        {' | '}<strong>Tryby:</strong> {showValue(strategyData?.modes)}
        {' | '}<strong>Parametry:</strong> {showValue(strategyData?.params)}
      </div>
      <div style={{ marginBottom: 8 }}>
        <strong>PnL:</strong> {error.performance ? error.performance : showValue(performanceData?.pnl)}
        {' | '}<strong>Winrate:</strong> {error.performance ? error.performance : showValue(performanceData?.winrate)}
        {' | '}<strong>Drawdown:</strong> {error.performance ? error.performance : showValue(performanceData?.drawdown)}
        {' | '}<strong>Open Trades:</strong> {error.performance ? error.performance : showValue(performanceData?.open_trades)}
        {' | '}<strong>Trades:</strong> {tradesCount}
        {' | '}<strong>Sharpe:</strong> {showValue(performanceData?.sharpe)}
        {' | '}<strong>Sortino:</strong> {showValue(performanceData?.sortino)}
      </div>
      <div style={{ marginBottom: 8 }}>
        <strong>Metryki:</strong> {error.metrics ? error.metrics : (metricsData && metricsData.length > 0 ? `${metricsData.length} punktów` : '---')}
        {' | '}<strong>Ostatni tick:</strong> {lastMetric ? showValue(lastMetric.tick) : '---'}
        {' | '}<strong>Ostatnia zmienność:</strong> {lastMetric ? showValue(lastMetric.volatility) : '---'}
      </div>
      {metricsData && metricsData.length > 0 ? (
        <TrendVolatilityChartAdapter
          data={metricsData.slice(-30).filter(Boolean).map(m => ({
            timestamp: m.timestamp,
            trend: m.trend ?? '',
            volatility: m.volatility ?? 0
          }))}
        />
      ) : (
        <div style={{ color: '#888', marginBottom: 8 }}>Brak danych do wykresu trendu/zmienności.</div>
      )}
      {equityData && equityData.length > 0 ? (
        <EquityChart data={equityData.slice(-30)} />
      ) : (
        <div style={{ color: '#888', marginBottom: 8 }}>Brak danych do wykresu equity.</div>
      )}
      {performanceData && performanceData.pnl !== undefined && metricsData && metricsData.length > 0 ? (
        <PnLChart
          data={metricsData.slice(-30)
            .filter(m => m && typeof m.volatility === 'number')
            .map(m => ({
              timestamp: m.timestamp,
              pnl: m.volatility as number
            }))}
        />
      ) : (
        <div style={{ color: '#888', marginBottom: 8 }}>Brak danych do wykresu PnL.</div>
      )}
      {decisions && decisions.length > 0 ? (
        <DecisionsTable data={decisions} />
      ) : (
        <div style={{ color: '#888', marginBottom: 8 }}>Brak decyzji do wyświetlenia.</div>
      )}
      {strategyData && strategyData.strategies ? (
        <StrategySummary strategies={strategyData.strategies.map(name => ({ name }))} />
      ) : null}
      {/* Widget podglądu pozycji */}
      <PositionTable />
      {/* Widget historii zamkniętych pozycji */}
      <ClosedPositionsTable />
    </div>
  );
};

export default DashboardStatus;
