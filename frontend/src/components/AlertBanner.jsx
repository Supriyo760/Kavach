import React from 'react';
import { AlertOctagon, AlertTriangle } from 'lucide-react';

const AlertBanner = ({ chargingRiskActive, regime }) => {
  if (!chargingRiskActive && regime !== 'main_phase') return null;

  return (
    <div className="alerts-container" style={{ padding: '0 32px', marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {chargingRiskActive && (
        <div className="alert-banner danger">
          <AlertOctagon className="icon" />
          <div>
            <strong>CRITICAL ERROR: DEEP DIELECTRIC CHARGING HAZARD DETECTED</strong>
            <p style={{ fontSize: '13px', marginTop: '2px', opacity: 0.9 }}>
              GEO &gt;2 MeV electron flux is projected to exceed the critical charging threshold of 10,000 pfu. Operational precaution advised for satellite subsystem gates.
            </p>
          </div>
        </div>
      )}

      {regime === 'main_phase' && (
        <div className="alert-banner warning">
          <AlertTriangle className="icon" />
          <div>
            <strong>GEOMAGNETIC STORM WARNING: MAIN PHASE INITIALIZED</strong>
            <p style={{ fontSize: '13px', marginTop: '2px', opacity: 0.9 }}>
              Magnetosphere is highly compressed (Dst &lt; -50 nT). Enhanced radial diffusion and magnetopause shadowing active. Model uncertainty intervals widened.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertBanner;
