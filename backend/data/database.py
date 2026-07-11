"""
TimescaleDB connection and table setup.
Uses SQLAlchemy for ORM and TimescaleDB 
hypertable for time-series optimization.
"""

from sqlalchemy import (
    create_engine, Column, Float, 
    DateTime, String, text
)
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.pool import NullPool
import pandas as pd
from config import DATABASE_URL

Base = declarative_base()

class SolarWindReading(Base):
    __tablename__ = 'solar_wind'
    timestamp = Column(DateTime, primary_key=True)
    Vsw = Column(Float)
    Bz = Column(Float)
    Bt = Column(Float)
    Np = Column(Float)
    coupling_fn = Column(Float)
    Pdyn = Column(Float)
    ulf_proxy = Column(Float)
    Kp = Column(Float)
    Dst = Column(Float)

class ElectronFluxReading(Base):
    __tablename__ = 'electron_flux'
    timestamp = Column(DateTime, primary_key=True)
    flux_raw = Column(Float)
    log_flux = Column(Float)
    source = Column(String)  # 'GOES' or 'GRASP'

class ForecastRecord(Base):
    __tablename__ = 'forecasts'
    timestamp = Column(DateTime, primary_key=True)
    horizon = Column(String, primary_key=True)
    p10 = Column(Float)
    p50 = Column(Float)
    p90 = Column(Float)
    risk_level = Column(String)
    ml_weight = Column(Float)
    physics_weight = Column(Float)
    agreement_score = Column(Float)

class RiskEvent(Base):
    __tablename__ = 'risk_events'
    timestamp = Column(DateTime, primary_key=True)
    event_type = Column(String)
    risk_level = Column(String)
    description = Column(String)


def get_engine():
    return create_engine(
        DATABASE_URL, 
        poolclass=NullPool,
        echo=False
    )


def init_db():
    """
    Initialize database tables.
    Convert to TimescaleDB hypertables for 
    time-series optimization.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    # Create TimescaleDB hypertables
    hypertable_queries = [
        "SELECT create_hypertable('solar_wind', "
        "'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('electron_flux', "
        "'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('forecasts', "
        "'timestamp', if_not_exists => TRUE);",
        "SELECT create_hypertable('risk_events', "
        "'timestamp', if_not_exists => TRUE);"
    ]
    
    with engine.connect() as conn:
        for query in hypertable_queries:
            try:
                conn.execute(text(query))
                conn.commit()
            except Exception as e:
                print(f"Hypertable note: {e}")
    
    print("Database initialized successfully")
    return engine


def store_dataframe(df, table_name, engine):
    """Store pandas DataFrame to TimescaleDB."""
    df.to_sql(
        table_name, 
        engine, 
        if_exists='append', 
        index=True,
        index_label='timestamp'
    )


def fetch_recent(table_name, hours=48, engine=None):
    """
    Fetch recent records using TimescaleDB 
    time_bucket for efficiency.
    """
    if engine is None:
        engine = get_engine()
    
    query = f"""
        SELECT * FROM {table_name}
        WHERE timestamp >= NOW() - INTERVAL '{hours} hours'
        ORDER BY timestamp ASC
    """
    return pd.read_sql(query, engine, 
                       index_col='timestamp',
                       parse_dates=['timestamp'])
