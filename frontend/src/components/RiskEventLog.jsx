import React from 'react';
import { ShieldAlert } from 'lucide-react';

const RiskEventLog = ({ events }) => {
  return (
    <div className="event-log-card">
      <h3 className="chart-title">
        <ShieldAlert size={18} /> OPERATIONAL HAZARD LOGS
      </h3>
      <div className="event-list">
        {events && events.length > 0 ? (
          events.map((event, index) => (
            <div className="event-item" key={index}>
              <div className="event-meta">
                <span className="event-type" style={{ color: event.risk_level === 'RED' ? 'var(--color-danger)' : 'var(--color-warning)' }}>
                  ⚠️ {event.event_type.replace('_', ' ')}
                </span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="event-desc">{event.description}</p>
            </div>
          ))
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '150px', color: 'var(--text-muted)', fontSize: '13px' }}>
            No active anomalies or storm events recorded.
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskEventLog;
