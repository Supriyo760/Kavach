import React from 'react';
import { Wind, Activity, ShieldAlert, Cpu } from 'lucide-react';

const StatCards = ({ currentConditions }) => {
  if (!currentConditions) return null;

  const { Vsw, Bz, Bt, Np, Kp, Dst, flux, log_flux } = currentConditions;

  const stats = [
    {
      label: 'SOLAR WIND SPEED',
      value: `${Vsw.toFixed(0)}`,
      unit: 'km/s',
      icon: <Wind size={16} className="text-secondary" />,
      color: Vsw > 600 ? '#ef4444' : Vsw > 500 ? '#f59e0b' : '#10b981',
    },
    {
      label: 'IMF Bz (GSM)',
      value: `${Bz.toFixed(1)}`,
      unit: 'nT',
      icon: <Activity size={16} className="text-secondary" />,
      color: Bz < -10 ? '#ef4444' : Bz < -5 ? '#f59e0b' : '#10b981',
    },
    {
      label: 'PROTON DENSITY',
      value: `${Np.toFixed(1)}`,
      unit: 'cm⁻³',
      icon: <Wind size={16} className="text-secondary" />,
      color: Np > 15 ? '#f59e0b' : '#10b981',
    },
    {
      label: 'Dst INDEX',
      value: `${Dst.toFixed(0)}`,
      unit: 'nT',
      icon: <ShieldAlert size={16} className="text-secondary" />,
      color: Dst < -100 ? '#ef4444' : Dst < -50 ? '#f59e0b' : '#10b981',
    },
    {
      label: 'Kp INDEX',
      value: `${Kp.toFixed(1)}`,
      unit: '',
      icon: <ShieldAlert size={16} className="text-secondary" />,
      color: Kp > 6 ? '#ef4444' : Kp > 4 ? '#f59e0b' : '#10b981',
    },
    {
      label: 'CURRENT ELECTRON FLUX',
      value: `${flux.toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
      unit: `pfu (10^${log_flux.toFixed(2)})`,
      icon: <Cpu size={16} className="text-secondary" />,
      color: flux > 10000 ? '#ef4444' : flux > 1000 ? '#f59e0b' : '#10b981',
    },
  ];

  return (
    <div className="stat-cards-grid">
      {stats.map((stat, index) => (
        <div className="stat-card" key={index}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span className="stat-label">{stat.label}</span>
            {stat.icon}
          </div>
          <div className="stat-value" style={{ color: stat.color, fontFamily: 'var(--font-display)' }}>
            {stat.value}
            <span style={{ fontSize: '12px', marginLeft: '6px', fontWeight: '500', color: 'var(--text-secondary)' }}>{stat.unit}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatCards;
