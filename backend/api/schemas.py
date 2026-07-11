"""
Pydantic schemas defining the request and response structures for the FastAPI Risk API.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class SolarWindSchema(BaseModel):
    timestamp: datetime
    Vsw: float
    Bz: float
    Bt: float
    Np: float
    coupling_fn: float
    Pdyn: float
    ulf_proxy: float
    Kp: float
    Dst: float

class ElectronFluxSchema(BaseModel):
    timestamp: datetime
    flux_raw: float
    log_flux: float
    source: str

class HorizonForecastSchema(BaseModel):
    horizon_label: str
    p10: float
    p50: float
    p90: float
    flux_p10: float
    flux_p50: float
    flux_p90: float
    risk_level: str

class DriverImportanceSchema(BaseModel):
    driver_name: str
    importance: float

class ExplanationsSchema(BaseModel):
    horizon: str
    drivers: Dict[str, float]

class RegimeStateSchema(BaseModel):
    regime: str
    label: str
    color: str
    hex_color: str
    weight_ml: float
    weight_physics: float
    description: str
    dst_current: float
    kp_current: float

class RiskEventSchema(BaseModel):
    timestamp: datetime
    event_type: str
    risk_level: str
    description: str

class DashboardStateSchema(BaseModel):
    timestamp: datetime
    current_conditions: dict
    forecasts: Dict[str, HorizonForecastSchema]
    regime: RegimeStateSchema
    explanations: Dict[str, Dict[str, float]]
    agreement_score: float
    charging_risk_active: bool

class ReplayControlSchema(BaseModel):
    active: bool
    current_index: int
    total_steps: int
    speed_ms: int
