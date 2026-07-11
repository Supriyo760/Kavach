import os

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://kavach:kavach2026@localhost:5432/kavach_db"
)

# MLflow
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI", 
    "sqlite:///mlflow/mlflow.db"
)
MLFLOW_EXPERIMENT_NAME = "kavach_electron_flux"

# Physical constants
PROTON_MASS_KG = 1.6726e-27  # kg
NPA_CONVERSION = 1.6726e-6   # for Pdyn in nPa

# L-shell grid
L_MIN = 3.0
L_MAX = 7.0
L_GEO = 6.6
L_POINTS = 41

# Forecast horizons (in 5-min samples)
HORIZON_30MIN = 6
HORIZON_6H = 72
HORIZON_12H = 144

# Risk thresholds (pfu)
THRESHOLD_YELLOW = 1000.0   # >1000 pfu = elevated
THRESHOLD_RED = 10000.0     # >10000 pfu = high risk

# Deep dielectric charging threshold
CHARGING_THRESHOLD_PFU = 10000.0

# Regime thresholds
DST_STORM_ONSET = -20.0    # nT
DST_MAIN_PHASE = -50.0     # nT
KP_ACTIVE = 3.0

# Model
INPUT_WINDOW_HOURS = 24
INPUT_SAMPLES = 288  # 24h × 12 samples/hour at 5-min cadence
LOG_FLUX_MIN = 1.0
LOG_FLUX_MAX = 5.5

# Feature columns
FEATURE_COLS = [
    'Vsw', 'Bz', 'Bt', 'Np',
    'coupling_fn', 'Pdyn', 'ulf_proxy',
    'log_flux',
    'flux_lag_12', 'flux_lag_24', 
    'flux_lag_48', 'flux_lag_72'
]

TARGET_COL = 'log_flux'
