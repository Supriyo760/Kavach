import React, { useState, useEffect } from 'react';

const HeaderBar = () => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="header-bar">
      <div className="header-title">
        <h1>🛡️ OPERATIONAL FLUX PREDICTION CONSOLE</h1>
      </div>
      <div className="header-status">
        <div className="time-ticker">
          SYSTEM UTC: {time.toUTCString().replace('GMT', 'UTC')}
        </div>
        <div className="conn-status">
          <span className="pulse-dot"></span>
          <span>TELEMETRY LINK: ONLINE</span>
        </div>
      </div>
    </div>
  );
};

export default HeaderBar;
