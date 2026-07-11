"""
Complete data cleaning pipeline using pandas, NumPy, SciPy.
"""

import numpy as np
import pandas as pd
from scipy.signal import medfilt
from scipy.interpolate import interp1d

def despike(series, window=5, n_sigma=4):
    """
    Rolling median despiking using SciPy medfilt.
    
    1. Apply median filter with kernel_size=window
    2. Compute residuals from median
    3. Compute std of residuals
    4. Replace |residual| > n_sigma * std with median
    
    Uses SciPy medfilt for efficient median filtering.
    """
    values = series.values.copy().astype(float)
    
    # Handle NaN for median filter
    valid_mask = ~np.isnan(values)
    if valid_mask.sum() < window:
        return series
    
    # Replace NaN with interpolated values temporarily
    temp = pd.Series(values).interpolate().values
    
    # Apply SciPy median filter
    from scipy.signal import medfilt
    median_filtered = medfilt(temp, kernel_size=window)
    
    # Compute residuals
    residuals = values - median_filtered
    std_resid = np.nanstd(residuals)
    
    if std_resid == 0:
        return series
    
    # Replace spikes with median
    spike_mask = np.abs(residuals) > n_sigma * std_resid
    values[spike_mask & valid_mask] = (
        median_filtered[spike_mask & valid_mask]
    )
    
    return pd.Series(values, index=series.index, 
                     name=series.name)


def log_transform(flux_series):
    """
    Log10 transform using NumPy.
    Clips to minimum 1e-3 to prevent log(0).
    Physical justification: flux spans 5-6 orders 
    of magnitude; log transform makes distribution 
    approximately normal and stabilizes MSE loss.
    """
    clipped = np.clip(flux_series.values, 1e-3, None)
    log_flux = np.log10(clipped)
    return pd.Series(
        log_flux, 
        index=flux_series.index, 
        name='log_flux'
    )


def fill_gaps(
    series, 
    max_gap_minutes=60, 
    cadence_minutes=5
):
    """
    Linear interpolation for short gaps using SciPy.
    Gaps longer than max_gap_minutes left as NaN.
    
    Uses scipy.interpolate.interp1d for interpolation.
    """
    max_gap_samples = int(max_gap_minutes / cadence_minutes)
    
    values = series.values.copy().astype(float)
    is_nan = np.isnan(values)
    
    if not is_nan.any():
        return series
    
    # Find gap sizes
    filled = values.copy()
    i = 0
    while i < len(values):
        if is_nan[i]:
            # Find end of gap
            j = i
            while j < len(values) and is_nan[j]:
                j += 1
            gap_size = j - i
            
            # Only fill short gaps
            if gap_size <= max_gap_samples:
                if i > 0 and j < len(values):
                    # Linear interpolation using SciPy
                    x_known = [i-1, j]
                    y_known = [values[i-1], values[j]]
                    f_interp = interp1d(
                        x_known, y_known, 
                        kind='linear'
                    )
                    x_fill = np.arange(i, j)
                    filled[i:j] = f_interp(x_fill)
            i = j
        else:
            i += 1
    
    return pd.Series(
        filled, index=series.index, name=series.name
    )


def resample_to_cadence(df, cadence='5min'):
    """
    Resample all columns to common 5-minute cadence 
    using pandas resample.mean()
    """
    return df.resample(cadence).mean()


def standardize_features(df, feature_cols, 
                          scaler=None, fit=True):
    """
    Z-score normalization using scikit-learn 
    StandardScaler.
    
    If fit=True: fit scaler on df (training data only)
    If fit=False: apply existing scaler (val/test data)
    
    Returns (normalized_df, scaler)
    CRITICAL: Never fit on validation or test data.
    """
    from sklearn.preprocessing import StandardScaler
    
    if scaler is None:
        scaler = StandardScaler()
    
    df_out = df.copy()
    
    if fit:
        df_out[feature_cols] = scaler.fit_transform(
            df[feature_cols].values
        )
    else:
        df_out[feature_cols] = scaler.transform(
            df[feature_cols].values
        )
    
    return df_out, scaler


def full_cleaning_pipeline(df):
    """
    Complete pipeline:
    1. Resample to 5-min cadence
    2. Despike flux
    3. Fill gaps (all columns)
    4. Log transform flux
    5. Return cleaned DataFrame
    """
    # Step 1: Resample
    df = resample_to_cadence(df)
    
    # Step 2: Despike flux
    if 'flux' in df.columns:
        df['flux'] = despike(df['flux'])
    
    # Step 3: Fill gaps
    for col in df.columns:
        df[col] = fill_gaps(df[col])
    
    # Step 4: Log transform
    if 'flux' in df.columns:
        df['log_flux'] = log_transform(df['flux'])
    
    return df
