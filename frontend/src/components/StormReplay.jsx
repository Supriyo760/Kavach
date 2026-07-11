import React from 'react';
import { Play, Square, SkipForward, Info } from 'lucide-react';

const StormReplay = ({ status, onStart, onStop, onStep }) => {
  const { active, current_index, total_steps } = status;
  
  // Convert current index to hours (5-minute cadence)
  const currentHour = ((current_index * 5) / 60).toFixed(1);
  const totalHours = ((total_steps * 5) / 60).toFixed(1);

  return (
    <div className="replay-card">
      <h3 className="chart-title">
        🌩️ GEOMAGNETIC STORM REPLAY CONTROLLER
      </h3>
      
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
        Run a high-fidelity simulation of the historic St. Patrick's Day geomagnetic storm. 
        Enables testing of KAVACH's dynamic regime detector and forecasting weights.
      </p>

      <div className="replay-controls">
        {!active ? (
          <button className="btn btn-primary" onClick={onStart}>
            <Play size={16} /> Start Simulation
          </button>
        ) : (
          <>
            <button className="btn btn-secondary" onClick={onStop}>
              <Square size={16} /> Terminate
            </button>
            <button className="btn btn-outline" onClick={onStep}>
              <SkipForward size={16} /> Step +5 Min
            </button>
          </>
        )}
      </div>

      <div className="replay-status-text" style={{ borderLeftColor: active ? '#ef4444' : '#2563eb' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
          <Info size={14} /> STATUS: {active ? 'SIMULATION ACTIVE' : 'NOMINAL MONITORING'}
        </div>
        {active && (
          <div style={{ marginTop: '6px', color: 'var(--text-secondary)' }}>
            Timeline Index: {current_index} / {total_steps} (Storm Hour {currentHour} of {totalHours}h)
          </div>
        )}
      </div>
    </div>
  );
};

export default StormReplay;
