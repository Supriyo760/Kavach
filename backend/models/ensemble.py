"""
Ensemble module fusing ML and physics-based predictions.
Weights are dynamic and determined by the current magnetospheric regime.
Computes final quantile forecasts (p10, p50, p90) and engine agreement score.
"""

import numpy as np
from config import LOG_FLUX_MIN, LOG_FLUX_MAX

class EnsembleEngine:
    """
    Fuses MLEngine and PhysicsEngine forecasts using RegimeDetector states.
    """
    
    def fuse(self, ml_forecasts, physics_forecasts, regime_state):
        """
        Args:
            ml_forecasts: dict of HorizonForecast objects from MLEngine
            physics_forecasts: dict of float values from PhysicsEngine
            regime_state: RegimeState object with engine weights
            
        Returns:
            dict of fused forecast records with keys:
            ['p10', 'p50', 'p90', 'risk_level', 'agreement_score']
        """
        w_ml = regime_state.weight_ml
        w_phys = regime_state.weight_physics
        
        fused = {}
        for horizon in ['30min', '6h', '12h']:
            ml_fc = ml_forecasts[horizon]
            phys_val = physics_forecasts[horizon]
            
            # Weighted average of p50 predictions
            p50_fused = w_ml * ml_fc.p50 + w_phys * phys_val
            
            # Compute agreement score between engines
            # Normalized difference in log space (0 = complete disagreement, 1 = identical predictions)
            max_diff = LOG_FLUX_MAX - LOG_FLUX_MIN
            diff = abs(ml_fc.p50 - phys_val)
            agreement = max(0.0, 1.0 - (diff / max_diff))
            
            # Uncertainty bounds fusion:
            # During MAIN_PHASE, we widen the uncertainty interval.
            # During QUIET, we narrow/maintain standard intervals.
            uncertainty_scale = 1.2 if regime_state.regime == 'main_phase' else 1.0
            
            p10_width = (ml_fc.p50 - ml_fc.p10) * uncertainty_scale
            p90_width = (ml_fc.p90 - ml_fc.p50) * uncertainty_scale
            
            p10_fused = np.clip(p50_fused - p10_width, LOG_FLUX_MIN, LOG_FLUX_MAX)
            p90_fused = np.clip(p50_fused + p90_width, LOG_FLUX_MIN, LOG_FLUX_MAX)
            
            # Compute risk level based on the raw flux values (pfu) corresponding to p50
            raw_flux_p50 = 10 ** p50_fused
            if raw_flux_p50 >= 10000.0:
                risk = "RED"
            elif raw_flux_p50 >= 1000.0:
                risk = "YELLOW"
            else:
                risk = "GREEN"
                
            fused[horizon] = {
                'p10': float(p10_fused),
                'p50': float(p50_fused),
                'p90': float(p90_fused),
                'risk_level': risk,
                'ml_weight': w_ml,
                'physics_weight': w_phys,
                'agreement_score': float(agreement)
            }
            
        return fused
