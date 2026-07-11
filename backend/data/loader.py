"""
Reads real GOES and Wind/OMNI CDF files.
Used in real deployment — prototype uses simulator.py instead.
Included here to show complete implementation.
"""

import cdflib
import spacepy.pycdf as pycdf
import pandas as pd
import numpy as np
from config import FEATURE_COLS

class GOESFluxLoader:
    """
    Reads GOES >2 MeV electron flux from CDF archives.
    Handles both EPEAD (GOES-13/15) and 
    MPS-HI (GOES-16/17/18) sensor formats.
    """
    
    # Variable names differ by sensor generation
    EPEAD_FLUX_VAR = 'E2_flux_ic'      # GOES-13/15
    MPSHI_FLUX_VAR = 'AvgDiffElectronFlux'  # GOES-16+
    
    def load_cdf(self, filepath, sensor='mpshi'):
        """
        Load GOES CDF file.
        
        Args:
            filepath: path to .cdf file
            sensor: 'epead' for GOES-13/15, 
                    'mpshi' for GOES-16/17/18
        
        Returns:
            pd.Series with DatetimeIndex, 
            name='flux', units pfu
        """
        try:
            cdf = cdflib.CDF(filepath)
            
            # Get epoch
            epoch = cdf.varget('Epoch')
            times = cdflib.cdfepoch.to_datetime(epoch)
            times = pd.to_datetime(times)
            
            # Get flux variable by sensor type
            flux_var = (self.MPSHI_FLUX_VAR 
                       if sensor == 'mpshi' 
                       else self.EPEAD_FLUX_VAR)
            
            flux = cdf.varget(flux_var).astype(float)
            
            # Handle multi-dimensional (take first channel)
            if flux.ndim > 1:
                flux = flux[:, 0]
            
            # Replace fill values
            flux[flux <= 0] = np.nan
            flux[flux > 1e8] = np.nan  # unphysical
            
            series = pd.Series(
                flux, index=times, name='flux'
            )
            return series.sort_index()
            
        except Exception as e:
            print(f"CDF load error: {e}")
            print("Falling back to synthetic data")
            return None
    
    def cross_calibrate_epead_to_mpshi(
        self, epead_series, mpshi_series
    ):
        """
        Cross-calibrate EPEAD to MPS-HI scale using 
        overlap period (2017-2018).
        Compute scaling factor from overlap statistics.
        Apply to EPEAD series before concatenating.
        Returns unified calibrated series.
        """
        overlap_start = '2017-01-01'
        overlap_end = '2018-12-31'
        
        epead_overlap = epead_series[overlap_start:overlap_end]
        mpshi_overlap = mpshi_series[overlap_start:overlap_end]
        
        # Align on common times
        common = pd.concat(
            [epead_overlap.rename('epead'), 
             mpshi_overlap.rename('mpshi')], 
            axis=1
        ).dropna()
        
        if len(common) > 100:
            # Compute ratio in log space
            scale = (
                np.log10(common['mpshi']).mean() - 
                np.log10(common['epead']).mean()
            )
            epead_calibrated = epead_series * (10**scale)
        else:
            print("Insufficient overlap for calibration")
            epead_calibrated = epead_series
        
        # Concatenate: EPEAD before overlap, MPS-HI after
        combined = pd.concat([
            epead_calibrated[:overlap_start],
            mpshi_series[overlap_start:]
        ]).sort_index()
        
        return combined


class WindOMNILoader:
    """
    Reads Wind spacecraft and OMNI merged solar wind data.
    OMNI is preferred — already time-shifted to bow shock.
    """
    
    OMNI_VARS = {
        'Vsw': 'V',           # Solar wind speed km/s
        'Bz': 'BZ_GSM',       # IMF Bz GSM nT
        'Bt': 'F',            # Total field nT
        'Np': 'proton_density' # Proton density cm⁻³
    }
    
    def load_omni_cdf(self, filepath):
        """
        Load OMNI CDF file.
        Returns DataFrame with Vsw, Bz, Bt, Np columns.
        """
        try:
            cdf = cdflib.CDF(filepath)
            epoch = cdf.varget('Epoch')
            times = pd.to_datetime(
                cdflib.cdfepoch.to_datetime(epoch)
            )
            
            df = pd.DataFrame(index=times)
            for col, var in self.OMNI_VARS.items():
                try:
                    data = cdf.varget(var).astype(float)
                    # Replace standard fill values
                    data[data > 9e30] = np.nan
                    data[data < -9e10] = np.nan
                    df[col] = data
                except:
                    df[col] = np.nan
            
            return df.sort_index()
            
        except Exception as e:
            print(f"OMNI load error: {e}")
            return None
