import React, { useEffect, useState } from 'react';

type ClosedPosition = {
  symbol: string;
  side?: string;
  entry_price?: number;
  exit_price?: number;
  profit?: number;
  timestamp?: string;
};

const API_URL = import.meta.env.VITE_API_URL;

const ClosedPositionsTable: React.FC = () => {
  const [closed, setClosed] = useState<ClosedPosition[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchClosed = () => {
      setLoading(true);
      setError(null);
      fetch(`${API_URL}/positions/closed`)
        .then(res => res.ok ? res.json() : Promise.reject(res))
        .then((data: ClosedPosition[]) => {
          if (isMounted) {
            setClosed(data);
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
    fetchClosed();
    const interval = setInterval(fetchClosed, 10000);
    return () => { isMounted = false; clearInterval(interval); };
  }, []);

  if (loading) return <div>Ładowanie historii pozycji...</div>;
  if (error) return <div style={{color: 'red'}}>{error}</div>;
  if (!closed || !Array.isArray(closed) || !closed.length) return <div>Brak zamkniętych pozycji.</div>;

  return (
    <div style={{margin: '16px 0'}}>
      <h3>Zamknięte pozycje</h3>
      <table style={{width: '100%', background: '#222', color: '#fff', borderCollapse: 'collapse'}}>
        <thead>
          <tr>
            <th style={{border: '1px solid #444', padding: 4}}>Symbol</th>
            <th style={{border: '1px solid #444', padding: 4}}>Pozycja</th>
            <th style={{border: '1px solid #444', padding: 4}}>Szczegóły</th>
          </tr>
        </thead>
        <tbody>
          {closed.filter(Boolean).map((pos, i) => (
            <tr key={i}>
              <td style={{border: '1px solid #444', padding: 4}}>{pos.symbol}</td>
              <td style={{border: '1px solid #444', padding: 4}}>{pos.side ?? '---'}</td>
              <td style={{border: '1px solid #444', padding: 4}}>
                <pre style={{margin: 0, color: '#aaa', fontSize: 12}}>{JSON.stringify(pos, null, 2)}</pre>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ClosedPositionsTable;
