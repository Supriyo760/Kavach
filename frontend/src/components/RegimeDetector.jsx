import React from 'react';
import { Compass } from 'lucide-react';

const RegimeDetector = ({ regime, agreementScore }) => {
  if (!regime) return null;

  const { label, color, hex_color, weight_ml, weight_physics, description, dst_current, kp_current } = regime;

  return (
    <div className={`regime-card ${regime.regime}`}>
      <div className="regime-header">
        <h3 className="chart-title" style={{ gap: '6px' }}>
          <Compass size={18} /> REGIME DETECTOR
        </h3>
        <span 
          className="regime-indicator" 
          style={{ 
            color: hex_color, 
            background: `rgba(${color === 'red' ? '239, 68, 68' : color === 'orange' ? '245, 158, 11' : color === 'purple' ? '155, 89, 182' : '16, 185, 129'}, 0.15)`,
            boxShadow: `0 0 10px rgba(${color === 'red' ? '239, 68, 68' : color === 'orange' ? '245, 158, 11' : color === 'purple' ? '155, 89, 182' : '16, 185, 129'}, 0.2)`
          }}
        >
          {label}
        </span>
      </div>

      <p className="regime-description">
        {description}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '10px' }}>
        {/* Dynamic Weights */}
        <div className="weight-row">
          <div className="weight-label">
            <span>MLEngine Weight (TFT)</span>
            <span style={{ fontWeight: 600 }}>{(weight_ml * 100).toFixed(0)}%</span>
          </div>
          <div className="weight-bar-bg">
            <div className="weight-bar-fill" style={{ width: `${weight_ml * 100}%` }} />
          </div>
        </div>

        <div className="weight-row">
          <div className="weight-label">
            <span>PhysicsEngine Weight (Diffusion Solver)</span>
            <span style={{ fontWeight: 600 }}>{(weight_physics * 100).toFixed(0)}%</span>
          </div>
          <div className="weight-bar-bg">
            <div className="weight-bar-fill physics" style={{ width: `${weight_physics * 100}%` }} />
          </div>
        </div>

        {/* Agreement Score & Environmental index */}
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0 0 0', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '13px', color: 'var(--text-secondary)' }}>
          <div>
            <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-muted)' }}>ENGINE AGREEMENT</span>
            <span style={{ fontWeight: 600, fontFamily: 'var(--font-display)', color: agreementScore > 0.85 ? 'var(--color-nominal)' : 'var(--color-warning)' }}>
              {(agreementScore * 100).toFixed(0)}% Match
            </span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-muted)' }}>MAGNETOSPHERIC DRIVERS</span>
            <span style={{ fontWeight: 600 }}>
              Dst: {dst_current.toFixed(0)} nT | Kp: {kp_current.toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegimeDetector;
