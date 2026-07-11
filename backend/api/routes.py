"""
API endpoints for serving KAVACH forecasting metrics and managing storm replay.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from api.schemas import DashboardStateSchema, HorizonForecastSchema, RegimeStateSchema, RiskEventSchema, ReplayControlSchema
from data.database import get_engine, fetch_recent
from data.simulator import generate_storm_simulation
from data.features import build_feature_matrix
from models.regime import RegimeDetector
from models.ml_engine import MLEngine
from models.physics_engine import PhysicsEngine
from models.ensemble import EnsembleEngine
from models.shap_explainer import SHAPExplainerWrapper
import config

router = APIRouter()

# Global State for Storm Replay Simulation
class StormReplayState:
    def __init__(self):
        self.active = False
        self.current_index = 0
        self.df = None
        self.feature_df = None
        self.total_points = 0
        self.start_time = None
        
    def initialize(self):
        # Generate full St. Patrick's Day storm dataset (48 hours at 5-min cadence = 576 points)
        self.df = generate_storm_simulation()
        self.feature_df = build_feature_matrix(self.df)
        self.total_points = len(self.feature_df)
        self.current_index = 72  # Start past the lag window (6 hours)
        self.start_time = self.feature_df.index[0]

replay_state = StormReplayState()
replay_state.initialize()

# Instantiate forecasting engines
ml_engine = MLEngine(prototype_mode=True)
physics_engine = PhysicsEngine()
ensemble_engine = EnsembleEngine()
shap_explainer = SHAPExplainerWrapper(ml_engine)
regime_detector = RegimeDetector()

# Initialize regime detector history with early storm data
for idx in range(72):
    row = replay_state.feature_df.iloc[idx]
    regime_detector.update(row['Dst'], row['Kp'])


@router.get("/dashboard")
def get_dashboard_state():
    """
    Returns the real-time operational dashboard state.
    Calculates forecasts using fused ML + Physics models.
    """
    # Fetch current operational frame based on replay state or real-time simulation
    if replay_state.active:
        idx = replay_state.current_index
        current_time = replay_state.feature_df.index[idx]
        feature_window = replay_state.feature_df.iloc[idx - 72 : idx + 1] # 6 hour history
    else:
        # Loop simulator dataset continuously if not in interactive replay
        time_elapsed = int((datetime.now() - datetime(2026, 1, 1)).total_seconds() / 300)
        idx = (72 + time_elapsed) % (replay_state.total_points - 1)
        current_time = datetime.now()
        feature_window = replay_state.feature_df.iloc[idx - 72 : idx + 1]
    
    current_row = feature_window.iloc[-1]
    
    # 1. Run Regime Detector
    regime_state = regime_detector.detect(current_row['Dst'], current_row['Kp'])
    
    # 2. Run forecasting engines
    ml_fc = ml_engine.predict(feature_window)
    phys_fc = physics_engine.predict(feature_window)
    
    # 3. Fuse forecasts using Ensemble
    fused_fc = ensemble_engine.fuse(ml_fc, phys_fc, regime_state)
    
    # 4. Compute explainability (SHAP values)
    shap_vals = shap_explainer.compute_shap_values(feature_window)
    
    # Format current conditions
    curr_cond = {
        'timestamp': current_time.isoformat(),
        'Vsw': float(current_row['Vsw']),
        'Bz': float(current_row['Bz']),
        'Bt': float(current_row['Bt']),
        'Np': float(current_row['Np']),
        'Kp': float(current_row['Kp']),
        'Dst': float(current_row['Dst']),
        'flux': float(current_row['flux'] if not np.isnan(current_row['flux']) else 10**current_row['log_flux']),
        'log_flux': float(current_row['log_flux'])
    }
    
    # Build horizon outputs
    horizons = {}
    for h_key, h_name in [('30min', 'T + 30 min'), ('6h', 'T + 6 hr'), ('12h', 'T + 12 hr')]:
        val = fused_fc[h_key]
        horizons[h_key] = HorizonForecastSchema(
            horizon_label=h_name,
            p10=val['p10'],
            p50=val['p50'],
            p90=val['p90'],
            flux_p10=float(10 ** val['p10']),
            flux_p50=float(10 ** val['p50']),
            flux_p90=float(10 ** val['p90']),
            risk_level=val['risk_level']
        )
        
    agreement = float(np.mean([fused_fc[h]['agreement_score'] for h in ['30min', '6h', '12h']]))
    charging_risk = any(horizons[h].flux_p50 >= config.CHARGING_THRESHOLD_PFU for h in ['30min', '6h', '12h'])
    
    return {
        'timestamp': current_time.isoformat(),
        'current_conditions': curr_cond,
        'forecasts': horizons,
        'regime': regime_state,
        'explanations': shap_vals,
        'agreement_score': agreement,
        'charging_risk_active': charging_risk
    }


@router.get("/history")
def get_historical_series():
    """
    Returns time series of the past 24 hours of solar wind, actual flux, and predicted flux
    for Plotly charting.
    """
    if replay_state.active:
        idx = replay_state.current_index
        # Return storm window up to current index
        history_df = replay_state.feature_df.iloc[max(0, idx - 288) : idx + 1]
    else:
        time_elapsed = int((datetime.now() - datetime(2026, 1, 1)).total_seconds() / 300)
        idx = (72 + time_elapsed) % (replay_state.total_points - 1)
        history_df = replay_state.feature_df.iloc[max(0, idx - 288) : idx + 1]
        
    res = []
    for t, row in history_df.iterrows():
        # Handle nan values for JSON compatibility
        flux_val = float(row['flux']) if not np.isnan(row['flux']) else float(10**row['log_flux'])
        res.append({
            'timestamp': t.isoformat(),
            'Vsw': float(row['Vsw']),
            'Bz': float(row['Bz']),
            'Bt': float(row['Bt']),
            'Np': float(row['Np']),
            'Kp': float(row['Kp']),
            'Dst': float(row['Dst']),
            'flux': flux_val,
            'log_flux': float(row['log_flux'])
        })
    return res


@router.get("/risk-events", response_model=List[RiskEventSchema])
def get_risk_events():
    """
    Generates historical event warnings based on the current timeline.
    """
    events = []
    idx_limit = replay_state.current_index if replay_state.active else replay_state.total_points - 1
    
    # Scan through simulated timeline to find threshold crossings
    history_df = replay_state.feature_df.iloc[72:idx_limit]
    
    under_storm_warning = False
    under_charging_warning = False
    
    for t, row in history_df.iterrows():
        flux_val = 10 ** row['log_flux']
        
        # Check geomagnetic storm onset
        if row['Dst'] < -50 and not under_storm_warning:
            events.append(RiskEventSchema(
                timestamp=t,
                event_type="GEOMAGNETIC_STORM",
                risk_level="RED",
                description=f"Severe geomagnetic storm main phase detected. Dst drop at {row['Dst']:.1f} nT."
            ))
            under_storm_warning = True
        elif row['Dst'] >= -20:
            under_storm_warning = False
            
        # Check dielectric charging warning
        if flux_val >= config.CHARGING_THRESHOLD_PFU and not under_charging_warning:
            events.append(RiskEventSchema(
                timestamp=t,
                event_type="DEEP_DIELECTRIC_CHARGING",
                risk_level="RED",
                description=f"Critical: GEO electron flux >2 MeV exceeded dielectric charging hazard threshold: {flux_val:.0f} pfu."
            ))
            under_charging_warning = True
        elif flux_val < config.THRESHOLD_YELLOW:
            under_charging_warning = False
            
    # Sort events latest first
    events.reverse()
    return events


@router.get("/replay", response_model=ReplayControlSchema)
def get_replay_status():
    return ReplayControlSchema(
        active=replay_state.active,
        current_index=replay_state.current_index,
        total_steps=replay_state.total_points,
        speed_ms=1000
    )


@router.post("/replay/start")
def start_replay():
    replay_state.active = True
    replay_state.current_index = 72  # Reset to post-lag window
    return {"status": "started", "index": replay_state.current_index}


@router.post("/replay/stop")
def stop_replay():
    replay_state.active = False
    return {"status": "stopped"}


@router.post("/replay/step")
def step_replay():
    if not replay_state.active:
        raise HTTPException(status_code=400, detail="Storm Replay is not active. Start it first.")
    
    replay_state.current_index += 1
    if replay_state.current_index >= replay_state.total_points:
        replay_state.current_index = 72  # Loop back
        
    return {
        "status": "stepped",
        "current_index": replay_state.current_index,
        "time": replay_state.feature_df.index[replay_state.current_index].isoformat()
    }
