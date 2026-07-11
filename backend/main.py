"""
FastAPI Application Bootstrap.
Initializes the database, configures CORS, and registers router endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from data.database import init_db, get_engine, store_dataframe
from data.simulator import generate_storm_simulation
import os

app = FastAPI(
    title="KAVACH — Space Weather Forecasting Risk API",
    description="Forecasts geostationary orbit >2 MeV electron flux and detects magnetospheric hazard regimes.",
    version="1.0.0"
)

# Configure CORS for React dashboard on port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prototype mode, allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def startup_event():
    """Initializes Database tables and loads initial storm dataset."""
    print("Bootstrap: Initializing TimescaleDB...")
    try:
        engine = init_db()
        
        # Check if database has solar wind records, if not populate with simulator data
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT count(*) FROM solar_wind"))
            count = result.scalar()
            
            if count == 0:
                print("Bootstrap: Database is empty. Pre-populating with storm simulation data...")
                df = generate_storm_simulation()
                # Store solar_wind readings
                sw_cols = ['Vsw', 'Bz', 'Bt', 'Np', 'Kp', 'Dst']
                df_sw = df[sw_cols].copy()
                df_sw['coupling_fn'] = df_sw['Vsw'] * np.maximum(0, -df_sw['Bz'])
                df_sw['Pdyn'] = 1.6726e-6 * df_sw['Np'] * df_sw['Vsw']**2
                # ULF power proxy variance over 30 mins
                df_sw['ulf_proxy'] = df_sw['Vsw'].rolling(window=6, min_periods=1).var().fillna(100.0)
                
                df_sw.to_sql('solar_wind', engine, if_exists='append', index=True, index_label='timestamp')
                
                # Store electron_flux readings
                df_flux = pd.DataFrame({
                    'flux_raw': df['flux'],
                    'log_flux': np.log10(np.clip(df['flux'], 1e-3, None)),
                    'source': 'GOES'
                }, index=df.index)
                df_flux.to_sql('electron_flux', engine, if_exists='append', index=True, index_label='timestamp')
                print("Bootstrap: Pre-population complete.")
            else:
                print(f"Bootstrap: Database already has {count} solar wind records.")
    except Exception as e:
        print(f"Bootstrap: Error initializing database: {e}")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "KAVACH Risk API",
        "leader": "Yashika Soni",
        "team": "DigiIndia"
    }

# Helper imports for startup script
import pandas as pd
import numpy as np
