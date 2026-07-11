import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <p>KAVACH — Kinetic-particle AI for Vigilant Anticipation of Charging Hazards. Built for ISRO's Bharatiya Antariksh Hackathon 2026.</p>
      <p style={{ marginTop: '4px', fontSize: '11px', color: 'var(--text-muted)' }}>
        Disclaimer: This dashboard is a simulation prototype of geostationary orbit electron flux and charging warning telemetry.
      </p>
    </footer>
  );
};

export default Footer;
