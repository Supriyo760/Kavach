import React from 'react';
import { Shield, Home, Cpu, Database, Settings } from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="logo-section">
        <Shield className="logo-icon" color="#3b82f6" />
        <span className="logo-title">KAVACH</span>
      </div>

      <div className="sidebar-menu">
        <a className="menu-item active">
          <Home size={18} />
          <span>Forecast Console</span>
        </a>
        <a className="menu-item" href={import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api', '/docs') : "http://localhost:8000/docs"} target="_blank" rel="noreferrer">
          <Database size={18} />
          <span>FastAPI Docs</span>
        </a>
        <a className="menu-item" href={import.meta.env.VITE_MLFLOW_URL || "http://localhost:5000"} target="_blank" rel="noreferrer">
          <Cpu size={18} />
          <span>MLflow server</span>
        </a>
        <a className="menu-item">
          <Settings size={18} />
          <span>Console Settings</span>
        </a>
      </div>

      <div className="team-credits">
        <h4>DEVELOPED BY</h4>
        <p>Team DigiIndia</p>
        <span>Leader: Yashika Soni</span>
        <div style={{ marginTop: '8px', fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600 }}>
          ISRO BHARATIYA ANTARIKSH HACKATHON 2026
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
