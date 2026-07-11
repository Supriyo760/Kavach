"""
Evaluates forecasting performance using metrics:
- Root Mean Squared Error (RMSE)
- Prediction Efficiency (PE / Nash-Sutcliffe Efficiency)
- Heidke Skill Score (HSS) for threshold risk warnings
Generates calibration curves.
"""

import numpy as np
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import config

def compute_rmse(y_true, y_pred):
    """Compute Root Mean Squared Error."""
    return np.sqrt(mean_squared_error(y_true, y_pred))


def compute_prediction_efficiency(y_true, y_pred):
    """
    Prediction Efficiency (PE) / Nash-Sutcliffe Efficiency.
    Measures how much better predictions are than using the historical mean.
    PE = 1.0 is a perfect forecast. PE = 0.0 is equivalent to predicting the mean.
    """
    mean_true = np.mean(y_true)
    numerator = np.sum((y_true - y_pred) ** 2)
    denominator = np.sum((y_true - mean_true) ** 2)
    
    if denominator == 0:
        return 0.0
    return 1.0 - (numerator / denominator)


def compute_hss(y_true_labels, y_pred_labels):
    """
    Heidke Skill Score (HSS) for categorical warnings.
    Range: -inf to 1.0 (1.0 = perfect warning classification, 0.0 = no skill).
    Formula: HSS = (Hits + Correct Negatives - Expected) / (Total - Expected)
    """
    from sklearn.metrics import confusion_matrix
    
    classes = list(set(y_true_labels).union(set(y_pred_labels)))
    if len(classes) <= 1:
        return 1.0
        
    cm = confusion_matrix(y_true_labels, y_pred_labels, labels=classes)
    total = np.sum(cm)
    
    # Trace represents correct predictions
    correct = np.trace(cm)
    
    # Expected correct by random chance
    row_sums = np.sum(cm, axis=1)
    col_sums = np.sum(cm, axis=0)
    expected = np.sum(row_sums * col_sums) / total
    
    if total - expected == 0:
        return 0.0
        
    hss = (correct - expected) / (total - expected)
    return float(hss)


def generate_calibration_curve(y_true, y_pred, filepath="calibration_curve.png"):
    """
    Generates reliability / calibration plot comparing true vs predicted log flux.
    Saves the curve to Matplotlib image.
    """
    plt.figure(figsize=(6, 6))
    plt.scatter(y_pred, y_true, alpha=0.5, color='#3498DB', label='Forecasts')
    
    # Perfect calibration line
    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal Calibration')
    
    plt.xlabel('Predicted Log Flux (>2 MeV)')
    plt.ylabel('Observed Log Flux (>2 MeV)')
    plt.title('KAVACH Forecast Calibration Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
