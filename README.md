# KAVACH — Space Weather Forecasting Prototype

**KAVACH** = Kinetic-particle AI for Vigilant Anticipation of Charging Hazards.
Developed for **ISRO Bharatiya Antariksh Hackathon 2026, Problem Statement 14**.

**Team:** DigiIndia
**Leader:** Yashika Soni

KAVACH is a full-stack prototype that forecasts >2 MeV electron flux at geostationary orbit (GEO) at three horizons simultaneously:
1. **30 minutes ahead** (T + 30 min)
2. **6 hours ahead** (T + 6 hr)
3. **12 hours ahead** (T + 12 hr)

The system models magnetospheric storm dynamics and alerts operators of potential deep dielectric charging hazards.

---

## Tech Stack
- **Data Layer:** `cdflib` / `SpacePy` (CDF readers), `pandas`, `NumPy`, `SciPy`
- **Forecasting Core:** `PyTorch` (TFT via Darts/PyTorch Forecasting), `scikit-learn`, `SHAP`
- **Visualization:** `Matplotlib` (static curves), `Plotly` (interactive dashboard plots)
- **Tracking:** `MLflow` (model versioning and experiments)
- **Application & Storage:** `FastAPI` (REST API), `PostgreSQL + TimescaleDB` (time-series hypertable)
- **Frontend Dashboard:** `React` + `Vite` (Sleek Dark Mode Operator Console)
- **Containerization:** `Docker` + `docker-compose`

---

## Getting Started

### Prerequisites
- Docker and docker-compose installed.
- Python 3.10+ (for local exploration/testing).

### Running KAVACH via Docker
1. Clone the project.
2. In the root directory `kavach/`, start the stack:
   ```bash
   docker-compose up --build -d
   ```
3. Access the dashboard:
   - **Frontend Operator Dashboard:** [http://localhost:5173](http://localhost:5173)
   - **FastAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **MLflow Tracking UI:** [http://localhost:5000](http://localhost:5000)

---

## Project Structure
```
kavach/
├── docker-compose.yml
├── .env
├── README.md
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── data/
│   │   ├── simulator.py      # St. Patrick's Day storm simulator
│   │   ├── loader.py         # CDF reader (cdflib/SpacePy)
│   │   ├── cleaner.py        # Despiking, log-transform, gaps
│   │   ├── features.py       # Physics-informed features
│   │   └── database.py       # TimescaleDB connection
│   ├── models/
│   │   ├── ml_engine.py      # TFT model via PyTorch + Darts
│   │   ├── physics_engine.py # Radial diffusion ODE solver
│   │   ├── ensemble.py       # Regime-weighted forecast fusion
│   │   ├── regime.py         # Magnetospheric regime detector
│   │   ├── baseline.py       # Persistence + linear regression baselines
│   │   └── shap_explainer.py # SHAP explainability layer
│   ├── training/
│   │   ├── trainer.py        # MLflow training loop
│   │   └── evaluator.py      # Metrics (RMSE, PE, HSS)
│   ├── api/
│   │   ├── routes.py         # FastAPI endpoints
│   │   └── schemas.py        # Pydantic schemas
│   └── notebooks/            # Jupyter notebooks for R&D
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── api/
        │   └── kavachApi.js
        ├── components/       # UI Dashboard components
        └── styles/
            └── kavach.css    # Modern Dark UI styles
```
