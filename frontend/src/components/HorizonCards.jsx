import React from 'react';
import { ArrowUpRight, ArrowDownRight, Equal } from 'lucide-react';

const HorizonCards = ({ forecasts, currentFlux }) => {
  if (!forecasts) return null;

  const horizonKeys = [
    { key: '30min', label: '30 MINUTE HORIZON' },
    { key: '6h', label: '6 HOUR HORIZON' },
    { key: '12h', label: '12 HOUR HORIZON' }
  ];

  return (
    <div className="horizon-cards-grid">
      {horizonKeys.map(({ key, label }) => {
        const fc = forecasts[key];
        if (!fc) return null;

        const trendIcon = fc.flux_p50 > currentFlux * 1.2 ? (
          <ArrowUpRight color="#ef4444" size={16} />
        ) : fc.flux_p50 < currentFlux * 0.8 ? (
          <ArrowDownRight color="#10b981" size={16} />
        ) : (
          <Equal color="#9ca3af" size={16} />
        );

        return (
          <div className={`horizon-card ${fc.risk_level}`} key={key}>
            <div className="horizon-header">
              <span className="horizon-title">{label}</span>
              <span className={`risk-badge ${fc.risk_level}`}>{fc.risk_level}</span>
            </div>
            <div className="horizon-value-section">
              <div className="horizon-value" style={{ fontFamily: 'var(--font-display)' }}>
                {fc.flux_p50.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span className="horizon-unit">pfu</span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '2px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  {trendIcon} Trend
                </span>
              </div>
            </div>
            <div className="horizon-bounds">
              <div>
                <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-muted)' }}>MIN BOUND (p10)</span>
                <span className="bound-val">{fc.flux_p10.toLocaleString(undefined, { maximumFractionDigits: 0 })} pfu</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-muted)' }}>MAX BOUND (p90)</span>
                <span className="bound-val">{fc.flux_p90.toLocaleString(undefined, { maximumFractionDigits: 0 })} pfu</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default HorizonCards;
