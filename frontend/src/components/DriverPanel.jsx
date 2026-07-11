import React from 'react';

const DriverPanel = ({ explanations }) => {
  if (!explanations) return null;

  const horizons = [
    { key: '30min', label: '30 MIN HORIZON DRIVERS' },
    { key: '6h', label: '6 HOUR HORIZON DRIVERS' },
    { key: '12h', label: '12 HOUR HORIZON DRIVERS' }
  ];

  const getDriverColor = (name) => {
    switch (name) {
      case 'Solar Wind Speed': return '#60a5fa';
      case 'IMF Bz (Southward)': return '#ef4444';
      case 'Dynamic Pressure': return '#f59e0b';
      case 'ULF Wave Power': return '#a78bfa';
      default: return '#9ca3af';
    }
  };

  return (
    <div className="driver-panel">
      <h3 className="chart-title" style={{ marginBottom: '16px' }}>
        🧠 SOLAR WIND DRIVER ATTENTION (SHAP EXPLAINABILITY)
      </h3>
      <div className="driver-grid">
        {horizons.map(({ key, label }) => {
          const drivers = explanations[key];
          if (!drivers) return null;

          return (
            <div className="driver-col" key={key}>
              <h4>{label}</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(drivers).map(([name, val]) => (
                  <div className="driver-contrib-row" key={name}>
                    <div className="driver-contrib-label">
                      <span>{name}</span>
                      <span style={{ fontWeight: 600 }}>{(val * 100).toFixed(0)}%</span>
                    </div>
                    <div className="driver-contrib-bar-bg">
                      <div 
                        className="driver-contrib-bar-fill"
                        style={{ 
                          width: `${val * 100}%`,
                          backgroundColor: getDriverColor(name)
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DriverPanel;
