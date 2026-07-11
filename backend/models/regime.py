"""
Magnetospheric regime detector.
Classifies current state every 5 minutes.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class RegimeState:
    regime: str
    label: str
    color: str
    hex_color: str
    weight_ml: float
    weight_physics: float
    description: str
    dst_current: float
    kp_current: float


class RegimeDetector:
    """
    Classifies magnetospheric state using Dst and Kp.
    
    States (in detection priority order):
    1. MAIN_PHASE  — Dst < -50 nT
    2. RECOVERY    — Dst was < -50, now rising
    3. STORM_ONSET — Dst dropping fast OR Kp rising fast
    4. QUIET       — Default
    """
    
    def __init__(self):
        self._dst_history = []
        self._kp_history = []
        self._was_in_main_phase = False
    
    def update(self, Dst: float, Kp: float):
        """Update history buffers."""
        self._dst_history.append(Dst)
        self._kp_history.append(Kp)
        
        # Keep last 72 samples (6 hours at 5-min cadence)
        if len(self._dst_history) > 72:
            self._dst_history.pop(0)
        if len(self._kp_history) > 72:
            self._kp_history.pop(0)
        
        if Dst < -50:
            self._was_in_main_phase = True
    
    def detect(self, Dst: float, Kp: float) -> RegimeState:
        """
        Detect current regime.
        
        MAIN_PHASE: Dst < -50 nT
        RECOVERY: previously in main phase AND Dst rising
        STORM_ONSET: Dst dropping >15 nT/hr OR 
                     Kp increased >1.5 in last 3h
        QUIET: none of the above
        """
        self.update(Dst, Kp)
        
        # MAIN PHASE
        if Dst < -50:
            return RegimeState(
                regime='main_phase',
                label='Main phase',
                color='red',
                hex_color='#E74C3C',
                weight_ml=0.40,
                weight_physics=0.60,
                description=(
                    "Radial diffusion + injection dominant. "
                    "Physics engine weighted higher. "
                    "Uncertainty band widened."
                ),
                dst_current=Dst,
                kp_current=Kp
            )
        
        # RECOVERY
        if (self._was_in_main_phase and 
            len(self._dst_history) > 6 and
            Dst > np.mean(self._dst_history[-6:])):
            return RegimeState(
                regime='recovery',
                label='Recovery',
                color='purple',
                hex_color='#9B59B6',
                weight_ml=0.55,
                weight_physics=0.45,
                description=(
                    "Ring current decay dominant. "
                    "Electron flux may continue rising "
                    "after storm peak."
                ),
                dst_current=Dst,
                kp_current=Kp
            )
        
        # STORM ONSET
        dst_rate = 0
        kp_rise = 0
        
        if len(self._dst_history) >= 12:
            # Rate over last 1 hour (12 samples)
            dst_rate = (
                self._dst_history[-1] - 
                self._dst_history[-12]
            ) / 1.0  # nT per hour
        
        if len(self._kp_history) >= 36:
            # Kp change over last 3 hours (36 samples)
            kp_rise = (
                self._kp_history[-1] - 
                self._kp_history[-36]
            )
        
        if dst_rate < -15 or kp_rise > 1.5:
            return RegimeState(
                regime='storm_onset',
                label='Storm onset',
                color='orange',
                hex_color='#F39C12',
                weight_ml=0.50,
                weight_physics=0.50,
                description=(
                    "Rapid Dst decrease detected. "
                    "Equal weighting of engines. "
                    "Enhanced monitoring active."
                ),
                dst_current=Dst,
                kp_current=Kp
            )
        
        # QUIET (default)
        if Dst > -20:
            self._was_in_main_phase = False
        
        return RegimeState(
            regime='quiet',
            label='Quiet',
            color='green',
            hex_color='#27AE60',
            weight_ml=0.70,
            weight_physics=0.30,
            description=(
                "Nominal conditions. "
                "ML engine dominant. "
                "High forecast confidence."
            ),
            dst_current=Dst,
            kp_current=Kp
        )
