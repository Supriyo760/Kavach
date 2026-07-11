import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import HeaderBar from './components/HeaderBar';
import PrototypeBanner from './components/PrototypeBanner';
import Dashboard from './components/Dashboard';
import Footer from './components/Footer';
import { fetchDashboardData, fetchHistoryData, fetchRiskEvents, getReplayStatus, startReplay, stopReplay, stepReplay } from './api/kavachApi';

function App() {
  const [dashboardData, setDashboardData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [riskEvents, setRiskEvents] = useState([]);
  const [replayStatus, setReplayStatus] = useState({ active: false, current_index: 0, total_steps: 576 });

  // Fetch all dashboard feeds
  const refreshFeeds = async () => {
    try {
      const dbData = await fetchDashboardData();
      setDashboardData(dbData);

      const histData = await fetchHistoryData();
      setHistoryData(histData);

      const events = await fetchRiskEvents();
      setRiskEvents(events);

      const status = await getReplayStatus();
      setReplayStatus(status);
    } catch (err) {
      console.error('Error fetching feeds from FastAPI backend:', err);
    }
  };

  // Poll feeds every 4 seconds
  useEffect(() => {
    refreshFeeds();
    const interval = setInterval(refreshFeeds, 4000);
    return () => clearInterval(interval);
  }, [replayStatus.active]);

  const handleStartReplay = async () => {
    try {
      const res = await startReplay();
      refreshFeeds();
    } catch (err) {
      console.error('Error starting storm simulation:', err);
    }
  };

  const handleStopReplay = async () => {
    try {
      await stopReplay();
      refreshFeeds();
    } catch (err) {
      console.error('Error stopping storm simulation:', err);
    }
  };

  const handleStepReplay = async () => {
    try {
      await stepReplay();
      refreshFeeds();
    } catch (err) {
      console.error('Error stepping storm simulation:', err);
    }
  };

  return (
    <div className="app-container">
      {/* Side bar credits */}
      <Sidebar />

      {/* Main dashboard content panel */}
      <div className="main-content">
        {/* Prototype Header details */}
        <PrototypeBanner />
        <HeaderBar />
        
        {/* Main Dashboard body */}
        <Dashboard 
          dashboardData={dashboardData}
          historyData={historyData}
          riskEvents={riskEvents}
          replayStatus={replayStatus}
          onStartReplay={handleStartReplay}
          onStopReplay={handleStopReplay}
          onStepReplay={handleStepReplay}
        />
        
        {/* Copyright disclosures */}
        <Footer />
      </div>
    </div>
  );
}

export default App;
