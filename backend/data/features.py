"""
Physics-informed feature engineering.
Each feature has a specific physical mechanism 
connecting it to >2 MeV electron flux at GEO.
"""

import numpy as np
import pandas as pd


def compute_coupling_function(Vsw, Bz):
    """
    IMF coupling function.
    Formula: Vsw × max(0, -Bz)
    
    Physical meaning: rate of solar wind energy 
    injection into magnetosphere via dayside 
    magnetic reconnection. Only southward Bz 
    (negative values) drives reconnection.
    
    Reference: Newell et al. (2007) JGR
    """
    Bz_south = np.maximum(0, -Bz)
    return Vsw * Bz_south


def compute_dynamic_pressure(Np, Vsw):
    """
    Solar wind dynamic pressure in nanoPascals.
    Formula: rho × V² / 2 = 1.6726e-6 × Np × Vsw²
    
    Physical meaning: how hard solar wind compresses 
    Earth's magnetopause. High Pdyn → magnetopause 
    moves inward → electrons at L>6.6 lost via 
    magnetopause shadowing.
    
    Units: Np [cm⁻³], Vsw [km/s] → Pdyn [nPa]
    """
    # Convert units: 1 cm⁻³ × (1 km/s)² → nPa 
    # factor = proton_mass_kg × 1e6 (cm³→m³) × 
    #          1e6 (km²/s²→m²/s²) × 1e9 (Pa→nPa)
    # = 1.6726e-27 × 1e21 = 1.6726e-6
    return 1.6726e-6 * Np * Vsw**2


def compute_ulf_proxy(
    Vsw, 
    window_minutes=30, 
    cadence_minutes=5
):
    """
    ULF wave power proxy.
    
    Formula: rolling variance of Vsw over 30-min window
    
    Physical mechanism: Solar wind speed fluctuations 
    in the 1-10 mHz (15-45 min period) frequency band 
    generate ULF magnetic waves inside the magnetosphere 
    via field-line resonances. These waves resonantly 
    interact with drifting electrons, violating their 
    third adiabatic invariant and causing radial 
    diffusion — transporting electrons inward to GEO 
    and accelerating them to relativistic energies.
    
    Reference: Mathie & Mann (2001) JGR — 
    "On the solar wind control of Pc5 ULF pulsation 
    power at mid-latitudes: Implications for MeV 
    electron acceleration in the outer radiation belt"
    """
    window_samples = int(window_minutes / cadence_minutes)
    if isinstance(Vsw, pd.Series):
        return Vsw.rolling(
            window=window_samples, 
            min_periods=1
        ).var()
    else:
        series = pd.Series(Vsw)
        return series.rolling(
            window=window_samples, 
            min_periods=1
        ).var().values


def compute_lagged_flux(log_flux_series, lags=[12,24,48,72]):
    """
    Lagged flux history features.
    
    At 5-min cadence:
    lag=12 → 1 hour ago
    lag=24 → 2 hours ago
    lag=48 → 4 hours ago
    lag=72 → 6 hours ago
    
    Physical justification: electron flux has strong 
    autocorrelation; past flux constrains future flux 
    and captures storm development shape.
    """
    lag_df = pd.DataFrame(index=log_flux_series.index)
    for lag in lags:
        lag_df[f'flux_lag_{lag}'] = (
            log_flux_series.shift(lag)
        )
    return lag_df


def build_feature_matrix(df):
    """
    Build complete feature matrix.
    
    Input df must have columns:
    flux, Vsw, Bz, Bt, Np, Kp, Dst
    
    Output df adds:
    log_flux, coupling_fn, Pdyn, ulf_proxy,
    flux_lag_12, flux_lag_24, flux_lag_48, flux_lag_72
    
    Drops NaN rows from lag computation.
    """
    df = df.copy()
    
    # Ensure log flux exists
    if 'log_flux' not in df.columns:
        from cleaner import log_transform
        df['log_flux'] = log_transform(df['flux'])
    
    # Physics features
    df['coupling_fn'] = compute_coupling_function(
        df['Vsw'], df['Bz']
    )
    df['Pdyn'] = compute_dynamic_pressure(
        df['Np'], df['Vsw']
    )
    df['ulf_proxy'] = compute_ulf_proxy(df['Vsw'])
    
    # Lagged flux features
    lag_df = compute_lagged_flux(df['log_flux'])
    df = pd.concat([df, lag_df], axis=1)
    
    # Drop NaN rows (from lag computation)
    df = df.dropna(subset=[
        'log_flux', 'coupling_fn', 
        'Pdyn', 'ulf_proxy',
        'flux_lag_12', 'flux_lag_24', 
        'flux_lag_48', 'flux_lag_72'
    ])
    
    return df
