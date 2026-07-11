"""
Baseline models for space weather forecasting.
Provides a Persistence model and a Linear Regression model.
Used for model validation and Prediction Efficiency (PE) comparison.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import config

class PersistenceBaseline:
    """
    Persistence model: Forecast(t + H) = Actual(t)
    """
    def predict(self, current_log_flux):
        return {
            '30min': current_log_flux,
            '6h': current_log_flux,
            '12h': current_log_flux
        }


class LinearBaseline:
    """
    Linear Regression model using scikit-learn.
    Fits on recent feature history to predict future horizons.
    """
    def __init__(self):
        self.models = {
            '30min': LinearRegression(),
            '6h': LinearRegression(),
            '12h': LinearRegression()
        }
        self.is_trained = False

    def train(self, feature_df, target_col='log_flux'):
        """Fits the linear regression models for each horizon."""
        if len(feature_df) < 150:
            return
            
        X = feature_df[config.FEATURE_COLS].values
        y_raw = feature_df[target_col].values
        
        # Horizons in samples
        h_30m = config.HORIZON_30MIN
        h_6h = config.HORIZON_6H
        h_12h = config.HORIZON_12H
        
        # Fit 30 min
        self.models['30min'].fit(X[:-h_30m], y_raw[h_30m:])
        # Fit 6h
        self.models['6h'].fit(X[:-h_6h], y_raw[h_6h:])
        # Fit 12h
        self.models['12h'].fit(X[:-h_12h], y_raw[h_12h:])
        
        self.is_trained = True

    def predict(self, feature_window_df):
        """Generates predictions for current feature window."""
        current_features = feature_window_df[config.FEATURE_COLS].iloc[-1].values.reshape(1, -1)
        current_log_flux = float(feature_window_df['log_flux'].iloc[-1])
        
        if not self.is_trained:
            # Fallback to persistence
            return {
                '30min': current_log_flux,
                '6h': current_log_flux,
                '12h': current_log_flux
            }
            
        return {
            '30min': float(self.models['30min'].predict(current_features)[0]),
            '6h': float(self.models['6h'].predict(current_features)[0]),
            '12h': float(self.models['12h'].predict(current_features)[0])
        }
