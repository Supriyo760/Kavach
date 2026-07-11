"""
Generates realistic synthetic space weather data
simulating a St. Patrick's Day class geomagnetic storm.
Uses numpy random with seed for reproducibility.
This is used ONLY because real CDF files are not 
available in the prototype — real deployment reads 
actual GOES/Wind CDF archives via loader.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_storm_simulation(
    start_time="2025-03-17 00:00:00",
    duration_hours=48,
    cadence_minutes=5,
    seed=42
):
    """
    Generate full 48-hour storm dataset.
    
    Storm timeline:
    Hour 0-10:   Quiet conditions
    Hour 10-12:  Sudden commencement, Bz turns south
    Hour 12-20:  Storm onset, flux begins rising
    Hour 20-26:  Main phase peak, maximum flux
    Hour 26-36:  Early recovery
    Hour 36-48:  Full recovery
    
    Returns pandas DataFrame with DatetimeIndex
    at 5-minute cadence.
    """
    np.random.seed(seed)
    
    n_points = int(duration_hours * 60 / cadence_minutes)
    times = pd.date_range(
        start=start_time, 
        periods=n_points, 
        freq=f"{cadence_minutes}min"
    )
    hours = np.linspace(0, duration_hours, n_points)
    
    # ── SOLAR WIND SPEED ──────────────────────────────────
    # Quiet: 420 km/s, ramp to 720 km/s at hour 10
    # Peak: 750 km/s at hour 18, decay to 520 km/s
    Vsw_base = np.where(
        hours < 10,
        420 + 5 * np.random.randn(n_points),
        np.where(
            hours < 18,
            420 + (750-420) * (hours-10)/8 
            + 10 * np.random.randn(n_points),
            np.where(
                hours < 36,
                750 - (750-550) * (hours-18)/18 
                + 15 * np.random.randn(n_points),
                550 - (550-480) * (hours-36)/12 
                + 8 * np.random.randn(n_points)
            )
        )
    )
    Vsw = np.clip(Vsw_base, 300, 900)
    
    # ── IMF BZ ────────────────────────────────────────────
    # Quiet: fluctuating ±5 nT
    # Storm: sudden southward to -18 nT at hour 11
    # Main: sustained -12 to -20 nT
    # Recovery: northward return
    Bz_base = np.where(
        hours < 11,
        2 * np.random.randn(n_points),
        np.where(
            hours < 14,
            -18 + 3 * np.random.randn(n_points),
            np.where(
                hours < 26,
                -14 + 4 * np.random.randn(n_points) 
                - 2 * np.sin((hours-14)/12 * np.pi),
                np.where(
                    hours < 36,
                    -14 + (14+8) * (hours-26)/10 
                    + 3 * np.random.randn(n_points),
                    5 + 3 * np.random.randn(n_points)
                )
            )
        )
    )
    Bz = np.clip(Bz_base, -30, 15)
    
    # ── IMF BT ────────────────────────────────────────────
    Bt = np.abs(Bz) + 3 + 2 * np.random.randn(n_points)
    Bt = np.clip(Bt, 1, 35)
    
    # ── PROTON DENSITY ───────────────────────────────────
    Np_base = np.where(
        hours < 10,
        5 + 1 * np.random.randn(n_points),
        np.where(
            hours < 14,
            18 + 3 * np.random.randn(n_points),
            np.where(
                hours < 30,
                10 + 2 * np.random.randn(n_points),
                6 + 1 * np.random.randn(n_points)
            )
        )
    )
    Np = np.clip(Np_base, 0.5, 40)
    
    # ── KP INDEX (3-hourly, interpolated) ────────────────
    Kp_3h = np.where(
        hours < 10, 1.5,
        np.where(hours < 14, 1.5 + (7-1.5)*(hours-10)/4,
        np.where(hours < 24, 7.5,
        np.where(hours < 36, 7.5 - (7.5-3)*(hours-24)/12,
        2.5)))
    )
    Kp = np.clip(Kp_3h + 0.2*np.random.randn(n_points), 
                 0, 9)
    
    # ── DST INDEX ────────────────────────────────────────
    Dst_base = np.where(
        hours < 10, -8 + 2*np.random.randn(n_points),
        np.where(
            hours < 20, 
            -8 - 170*(hours-10)/10 
            + 5*np.random.randn(n_points),
            np.where(
                hours < 30,
                -178 + 120*(hours-20)/10 
                + 8*np.random.randn(n_points),
                np.where(
                    hours < 48,
                    -58 + 50*(hours-30)/18 
                    + 4*np.random.randn(n_points),
                    -8 + 2*np.random.randn(n_points)
                )
            )
        )
    )
    Dst = np.clip(Dst_base, -220, 20)
    
    # ── ELECTRON FLUX (>2 MeV, pfu) ──────────────────────
    # Quiet: 200-400 pfu (log ~2.3-2.6)
    # Storm onset lag: flux rises 8-12h after Bz southward
    # Peak: 30000-70000 pfu (log ~4.5-4.85)
    # Recovery: slow decay
    log_flux_base = np.where(
        hours < 12,
        2.4 + 0.05*np.random.randn(n_points),
        np.where(
            hours < 22,
            2.4 + 2.2*(hours-12)/10 
            + 0.1*np.random.randn(n_points),
            np.where(
                hours < 28,
                4.6 + 0.15*np.random.randn(n_points),
                np.where(
                    hours < 40,
                    4.6 - 1.8*(hours-28)/12 
                    + 0.1*np.random.randn(n_points),
                    2.8 - 0.3*(hours-40)/8 
                    + 0.08*np.random.randn(n_points)
                )
            )
        )
    )
    log_flux_base = np.clip(log_flux_base, 1.5, 5.2)
    flux = 10**log_flux_base
    
    # ── ADD DATA GAPS ─────────────────────────────────────
    gap_positions = [45, 130, 280, 410]
    gap_lengths = [2, 3, 1, 2]
    for pos, length in zip(gap_positions, gap_lengths):
        if pos + length < n_points:
            flux[pos:pos+length] = np.nan
            Bz[pos:pos+length] = np.nan
            Vsw[pos:pos+length] = np.nan
    
    # ── BUILD DATAFRAME ───────────────────────────────────
    df = pd.DataFrame({
        'flux': flux,
        'Vsw': Vsw,
        'Bz': Bz,
        'Bt': Bt,
        'Np': Np,
        'Kp': Kp,
        'Dst': Dst
    }, index=times)
    
    return df


def get_current_conditions(df, current_idx=None):
    """
    Returns current conditions at a given index.
    Default: index at hour 30 (storm onset scenario)
    showing elevated conditions for demo.
    """
    if current_idx is None:
        # Default to storm onset period for impressive demo
        current_idx = int(len(df) * 0.35)
    return df.iloc[current_idx]
