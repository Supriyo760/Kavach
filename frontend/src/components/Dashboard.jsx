import React from 'react';
import AlertBanner from './AlertBanner';
import StatCards from './StatCards';
import HorizonCards from './HorizonCards';
import FluxChart from './FluxChart';
import RegimeDetector from './RegimeDetector';
import DriverPanel from './DriverPanel';
import StormReplay from './StormReplay';
import RiskEventLog from './RiskEventLog';

const Dashboard = ({ 
  dashboardData, 
  historyData, 
  riskEvents, 
  replayStatus,
  onStartReplay,
  onStopReplay,
  onStepReplay
}) => {
  if (!dashboardData) {
    return (
      <div style={{ display: 'flex', flexGrow: 1, justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="pulse-dot" style={{ margin: '0 auto 16px auto', width: '20px', height: '20px' }}></div>
          <p style={{ fontFamily: 'var(--font-display)', fontWeight: 600, letterSpacing: '1px' }}>INITIALIZING OPERATIONAL LINK...</p>
        </div>
      </div>
    );
  }

  const { current_conditions, forecasts, regime, explanations, agreement_score, charging_risk_active } = dashboardData;

  return (
    <div className="dashboard-viewport">
      {/* Alert banner for active hazards */}
      <AlertBanner chargingRiskActive={charging_risk_active} regime={regime?.regime} />

      {/* Real-time environmental metrics */}
      <StatCards currentConditions={current_conditions} />

      {/* Forecast Horizons */}
      <HorizonCards forecasts={forecasts} currentFlux={current_conditions?.flux || 100} />

      {/* Main Grid: Chart and Regime Detector */}
      <div className="dashboard-grid-main">
        <FluxChart data={historyData} />
        <RegimeDetector regime={regime} agreementScore={agreement_score} />
      </div>

      {/* Explainability Section */}
      <DriverPanel explanations={explanations} />

      {/* Bottom Grid: Storm Replay Controls and Historical Event Logs */}
      <div className="dashboard-grid-secondary">
        <StormReplay 
          status={replayStatus} 
          onStart={onStartReplay} 
          onStop={onStopReplay} 
          onStep={onStepReplay} 
        />
        <RiskEventLog events={riskEvents} />
      </div>
    </div>
  );
};

export default Dashboard;
