import React from 'react';

interface SummaryPanelProps {
  pnl?: number;
  winrate?: number;
  drawdown?: number;
  openTrades?: number;
}

const SummaryPanel: React.FC<SummaryPanelProps> = ({ pnl = 0, winrate = 0, drawdown = 0, openTrades = 0 }) => {
  return (
    <div style={{
      display: 'flex',
      gap: 32,
      justifyContent: 'center',
      margin: '24px 0',
      padding: '16px',
      background: '#181c24',
      color: '#fff',
      borderRadius: 10,
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
    }}>
      <div>
        <div style={{fontSize: 18, fontWeight: 600}}>💰 PnL</div>
        <div style={{fontSize: 22, color: pnl >= 0 ? '#4caf50' : '#e53935'}}>{pnl.toFixed(2)}</div>
      </div>
      <div>
        <div style={{fontSize: 18, fontWeight: 600}}>🏆 Winrate</div>
        <div style={{fontSize: 22}}>{(winrate * 100).toFixed(1)}%</div>
      </div>
      <div>
        <div style={{fontSize: 18, fontWeight: 600}}>📉 Drawdown</div>
        <div style={{fontSize: 22, color: '#e53935'}}>{drawdown.toFixed(2)}</div>
      </div>
      <div>
        <div style={{fontSize: 18, fontWeight: 600}}>📊 Open Trades</div>
        <div style={{fontSize: 22}}>{openTrades}</div>
      </div>
    </div>
  );
};

export default SummaryPanel;
