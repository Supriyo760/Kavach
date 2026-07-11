"""
Training script orchestrating data loading, features preprocessing,
model fitting, and MLflow tracking.
"""

import os
import pandas as pd
from data.simulator import generate_storm_simulation
from data.cleaner import full_cleaning_pipeline, standardize_features
from data.features import build_feature_matrix
from models.ml_engine import MLEngine
import config

def run_training_pipeline():
    """
    Simulates loading historical data, processing it, 
    training the ML model (MLEngine), and logging metrics/artifacts to MLflow.
    """
    print("Starting KAVACH training pipeline...")
    
    # 1. Load data
    df_raw = generate_storm_simulation(seed=100) # Use a different seed for training data
    
    # 2. Clean data
    df_cleaned = full_cleaning_pipeline(df_raw)
    
    # 3. Engineer features
    df_features = build_feature_matrix(df_cleaned)
    
    # Split into train/validation sets (80/20 time-based split)
    split_idx = int(len(df_features) * 0.8)
    train_df = df_features.iloc[:split_idx]
    val_df = df_features.iloc[split_idx:]
    
    # Scale features
    train_df_scaled, scaler = standardize_features(train_df, config.FEATURE_COLS, fit=True)
    val_df_scaled, _ = standardize_features(val_df, config.FEATURE_COLS, scaler=scaler, fit=False)
    
    # 4. Train MLEngine and log to MLflow
    engine = MLEngine(prototype_mode=True)
    engine.train_with_mlflow(
        train_df_scaled, 
        val_df_scaled, 
        feature_cols=config.FEATURE_COLS,
        target_col=config.TARGET_COL,
        epochs=10
    )
    
    print("Training pipeline completed successfully.")

if __name__ == "__main__":
    run_training_pipeline()
