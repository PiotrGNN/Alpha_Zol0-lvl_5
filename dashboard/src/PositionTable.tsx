import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Type definitions for position objects returned by the API
interface PositionDetails {
  [key: string]: any;
}

// API base URL from environment (configured via Vite)
const API_URL = import.meta.env.VITE_API_URL;

/**
 * PositionTable component
 *
 * Displays a list of open positions fetched from the backend. Users can
 * export positions to CSV, close individual positions and view a mini chart
 * of a selected position's value history. Alerts are shown when a position
 * has a large unrealized PnL. All API calls poll periodically to keep
 * information fresh without overwhelming the server.
 */
const PositionTable: React.FC = () => {
  const [positions, setPositions] = useState<Record<string, PositionDetails>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [alert, setAlert] = useState<string | null>(null);
  const [selected, setSelected] = useState<(PositionDetails & { symbol: string }) | null>(null);
  const [history, setHistory] = useState<any[]>([]);

  // Fetch open positions periodically
  useEffect(() => {
    let isMounted = true;
    const fetchPositions = () => {
      setLoading(true);
      setError(null);
      fetch(`${API_URL}/positions`)
        .then(res => (res.ok ? res.json() : Promise.reject(res)))
        .then((data: Record<string, PositionDetails>) => {
          if (isMounted) {
            setPositions(data || {});
            setLoading(false);
          }
        })
        .catch(() => {
          if (isMounted) {
            setError('Błąd API');
            setLoading(false);
          }
        });
    };
    fetchPositions();
    const interval = setInterval(fetchPositions, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Fetch position history for the selected symbol
  useEffect(() => {
    if (!selected) return;
    let isMounted = true;
    const fetchHistory = () => {
      fetch(`${API_URL}/positions/${selected.symbol}/history`)
        .then(res => (res.ok ? res.json() : Promise.reject(res)))
        .then((data: any[]) => {
          if (isMounted) setHistory(data || []);
        })
        .catch(() => {
          if (isMounted) setHistory([]);
        });
    };
    fetchHistory();
    const interval = setInterval(fetchHistory, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selected]);

  // Export positions to CSV
  const exportCSV = () => {
    const symbols = Object.keys(positions);
    const rows: string[][] = [
      ['symbol', 'side', 'details'],
      ...symbols.map(sym => [
        sym,
        positions[sym]?.side ?? '',
        JSON.stringify(positions[sym])
      ])
    ];
    const csv = rows
      .map(r => r.map(x => '"' + String(x).replace('"', '""') + '"').join(','))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'positions.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  // Close a position via the API
  const closePosition = (sym: string) => {
    fetch(`${API_URL}/positions/${sym}/close`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        const message = data.status === 'closed'
          ? `Pozycja ${sym} zamknięta!`
          : data.error || 'Błąd zamykania';
        setAlert(message);
        setTimeout(() => setAlert(null), 4000);
      })
      .catch(() => {
        setAlert('Błąd zamykania pozycji');
        setTimeout(() => setAlert(null), 4000);
      });
  };

  // Alert when a position has large unrealized PnL
  useEffect(() => {
    const symbols = Object.keys(positions);
    for (const sym of symbols) {
      const pos = positions[sym];
      if (pos && pos.unrealized_pnl && pos.unrealized_pnl > 100) {
        setAlert(`Uwaga: duży PnL na ${sym}: ${pos.unrealized_pnl}`);
        setTimeout(() => setAlert(null), 4000);
      }
    }
  }, [positions]);

  // Render states: loading, error, empty list
  if (loading) return <div>Ładowanie pozycji...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  const symbols = Object.keys(positions);
  if (!symbols.length) return <div>Brak otwartych pozycji.</div>;

  return (
    <div style={{ margin: '16px 0' }}>
      <h3>
        Pozycje <button onClick={exportCSV} style={{ marginLeft: 8 }}>Eksport do CSV</button>
      </h3>
      {alert && (
        <div
          style={{
            background: '#ff0',
            color: '#000',
            padding: 8,
            marginBottom: 8,
            borderRadius: 4
          }}
        >
          {alert}
        </div>
      )}
      <table
        style={{
          width: '100%',
          background: '#222',
          color: '#fff',
          borderCollapse: 'collapse'
        }}
      >
        <thead>
          <tr>
            <th style={{ border: '1px solid #444', padding: 4 }}>Symbol</th>
            <th style={{ border: '1px solid #444', padding: 4 }}>Pozycja</th>
            <th style={{ border: '1px solid #444', padding: 4 }}>Szczegóły</th>
            <th style={{ border: '1px solid #444', padding: 4 }}>Akcje</th>
          </tr>
        </thead>
        <tbody>
          {symbols.map(sym => (
            <tr
              key={sym}
              style={{ cursor: 'pointer' }}
              onClick={() => setSelected({ symbol: sym, ...positions[sym] })}
            >
              <td style={{ border: '1px solid #444', padding: 4 }}>{sym}</td>
              <td style={{ border: '1px solid #444', padding: 4 }}>{positions[sym]?.side ?? '---'}</td>
              <td style={{ border: '1px solid #444', padding: 4 }}>
                <pre style={{ margin: 0, color: '#aaa', fontSize: 12 }}>
                  {JSON.stringify(positions[sym], null, 2)}
                </pre>
              </td>
              <td style={{ border: '1px solid #444', padding: 4 }}>
                <button
                  onClick={e => {
                    e.stopPropagation();
                    closePosition(sym);
                  }}
                >
                  Zamknij
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Details and history chart for selected position */}
      {selected && (
        <div
          style={{
            background: '#222',
            color: '#fff',
            padding: 16,
            marginTop: 16,
            borderRadius: 8
          }}
        >
          <h4>
            Szczegóły pozycji: {selected.symbol}{' '}
            <button onClick={() => setSelected(null)} style={{ marginLeft: 8 }}>
              Zamknij
            </button>
          </h4>
          <pre style={{ color: '#aaa', fontSize: 14 }}>
            {JSON.stringify(selected, null, 2)}
          </pre>
          {/* Chart of position value over time */}
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                <XAxis dataKey="timestamp" tick={false} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#82ca9d" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default PositionTable;