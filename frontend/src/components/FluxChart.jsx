import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const fluxVal = Math.pow(10, data.log_flux);
    return (
      <div style={{
        background: 'rgba(12, 16, 32, 0.95)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.5)'
      }}>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
          {new Date(data.timestamp).toLocaleTimeString()}
        </p>
        <p style={{ fontFamily: 'var(--font-display)', color: '#3b82f6', fontWeight: 600 }}>
          Flux: {fluxVal.toLocaleString(undefined, { maximumFractionDigits: 0 })} pfu
        </p>
        <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Vsw: {data.Vsw.toFixed(0)} km/s | Dst: {data.Dst.toFixed(0)} nT
        </p>
      </div>
    );
  }
  return null;
};

const FluxChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="chart-card">
      <div className="chart-header">
        <h3 className="chart-title">
          🛡️ INTERACTIVE ELECTRON FLUX TELEMETRY (&gt;2 MeV)
        </h3>
        <div className="chart-legend">
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></span>
            <span>Flux (&gt;2 MeV)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: 'var(--color-warning)' }}></span>
            <span>Elevated Risk Threshold (10³ pfu)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ backgroundColor: 'var(--color-danger)' }}></span>
            <span>High Hazard Threshold (10⁴ pfu)</span>
          </div>
        </div>
      </div>

      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="fluxGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={(t) => new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              stroke="var(--text-muted)"
              fontSize={11}
            />
            <YAxis 
              domain={[1.0, 5.5]} 
              ticks={[1.0, 2.0, 3.0, 4.0, 5.0]}
              tickFormatter={(val) => `10^${val}`}
              stroke="var(--text-muted)"
              fontSize={11}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Threshold reference lines */}
            <ReferenceLine y={3.0} stroke="var(--color-warning)" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'Elevated', fill: 'var(--color-warning)', fontSize: 10, position: 'insideTopLeft' }} />
            <ReferenceLine y={4.0} stroke="var(--color-danger)" strokeDasharray="4 4" strokeWidth={1} label={{ value: 'Critical Charging', fill: 'var(--color-danger)', fontSize: 10, position: 'insideTopLeft' }} />
            
            <Area 
              type="monotone" 
              dataKey="log_flux" 
              stroke="#3b82f6" 
              strokeWidth={2.5}
              fillOpacity={1} 
              fill="url(#fluxGlow)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default FluxChart;
