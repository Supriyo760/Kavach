"""
Physics Engine solving the 1D Fokker-Planck radial diffusion equation.
Models phase space density (PSD) transport and loss in the outer radiation belt.
Uses SciPy ODE solver for integration.
"""

import numpy as np
import scipy.integrate as integrate
import config

class PhysicsEngine:
    """
    Solves: df/dt = L^2 * d/dL ( (DLL / L^2) * df/dL ) - f/tau
    where f is Phase Space Density (PSD), L is L-shell, and DLL is diffusion coeff.
    """
    
    def __init__(self):
        self.L_grid = np.linspace(config.L_MIN, config.L_MAX, config.L_POINTS)
        self.dL = self.L_grid[1] - self.L_grid[0]
        
    def _compute_dll(self, L, Kp):
        """
        Brautigam and Albert (2000) model for ULF-driven radial diffusion.
        DLL = DLL_magnetic + DLL_electric
        """
        # DLL magnetic power law
        log_dll_mag = 0.038 * Kp - 9.6
        dll_mag = (10 ** log_dll_mag) * (L ** 10)
        
        # DLL electric power law
        log_dll_elec = 0.097 * Kp - 9.1
        dll_elec = (10 ** log_dll_elec) * (L ** 6)
        
        return dll_mag + dll_elec

    def _compute_losses(self, L, Pdyn):
        """
        Models electron lifetimes (tau).
        Quiet lifetimes ~ 3 days (2.592e5 sec).
        Under high dynamic pressure, magnetopause shadowing occurs for L > L_mp.
        """
        # Magnetopause location estimation (Shue et al. 1998)
        L_mp = 11.5 - 0.5 * Pdyn
        L_mp = np.clip(L_mp, 4.0, 10.0)
        
        tau = np.ones_like(L) * (3.0 * 24.0 * 3600.0)  # 3 days nominal lifetime
        
        # Shadowing region has rapid losses (tau ~ 10 mins)
        shadow_mask = L > L_mp
        tau[shadow_mask] = 600.0  # 10 minutes loss timescale
        
        return tau

    def _drift_diffusion_equation(self, t, f, Kp, Pdyn, f_inner, f_outer):
        """Discretized PDE derivatives for solve_ivp."""
        dfdt = np.zeros_like(f)
        N = len(self.L_grid)
        
        # Compute DLL and tau across grid
        dll = self._compute_dll(self.L_grid, Kp)
        tau = self._compute_losses(self.L_grid, Pdyn)
        
        # Boundary conditions
        dfdt[0] = 0   # Inner boundary f(L_min) = f_inner (fixed/slow-varying)
        dfdt[-1] = 0  # Outer boundary f(L_max) = f_outer (driven by magnetosphere coupling)
        
        # Interior points central finite difference
        for i in range(1, N - 1):
            L = self.L_grid[i]
            
            # Gradients of DLL/L^2
            term_left = dll[i] / (L ** 2)
            
            # Numerical spatial derivative: d/dL ( (DLL/L^2) * df/dL )
            # We estimate (df/dL) at boundaries between grid points
            df_dL_plus = (f[i+1] - f[i]) / self.dL
            df_dL_minus = (f[i] - f[i-1]) / self.dL
            
            dll_over_L2_plus = 0.5 * (dll[i+1]/(self.L_grid[i+1]**2) + dll[i]/(L**2))
            dll_over_L2_minus = 0.5 * (dll[i]/(L**2) + dll[i-1]/(self.L_grid[i-1]**2))
            
            pde_term = (dll_over_L2_plus * df_dL_plus - dll_over_L2_minus * df_dL_minus) / self.dL
            
            # PSD transport
            dfdt[i] = (L ** 2) * pde_term - f[i] / tau[i]
            
        return dfdt

    def solve_diffusion(self, Kp, Pdyn, coupling_fn, current_log_flux, dt_hours=6):
        """
        Solves radial diffusion for a given time step.
        Returns the forecasted log flux at L_GEO = 6.6.
        """
        # Formulate boundaries in PSD (which scales with flux)
        f_inner = 10 ** 2.2  # Quiet conditions inner boundary
        f_outer = 10 ** (config.LOG_FLUX_MIN + (config.LOG_FLUX_MAX - config.LOG_FLUX_MIN) * (coupling_fn / 2500.0))
        f_outer = np.clip(f_outer, 10**config.LOG_FLUX_MIN, 10**config.LOG_FLUX_MAX)
        
        # Initial condition: flat interpolation between boundaries initialized with current GEO flux
        f_init = np.zeros(config.L_POINTS)
        for i, L in enumerate(self.L_grid):
            if L <= config.L_GEO:
                # Interpolate from inner to GEO
                frac = (L - config.L_MIN) / (config.L_GEO - config.L_MIN)
                f_init[i] = f_inner + frac * (10**current_log_flux - f_inner)
            else:
                # Interpolate from GEO to outer
                frac = (L - config.L_GEO) / (config.L_MAX - config.L_GEO)
                f_init[i] = 10**current_log_flux + frac * (f_outer - 10**current_log_flux)
                
        # ODE Solver
        t_span = (0.0, dt_hours * 3600.0)
        sol = integrate.solve_ivp(
            self._drift_diffusion_equation,
            t_span,
            f_init,
            args=(Kp, Pdyn, f_inner, f_outer),
            method='RK45',
            t_eval=[t_span[1]]
        )
        
        f_final = sol.y[:, -1]
        
        # Interpolate final PSD to get value at L_GEO (6.6)
        f_geo = np.interp(config.L_GEO, self.L_grid, f_final)
        
        # Convert back to log flux
        log_flux_geo = np.log10(np.clip(f_geo, 1.0, 10**config.LOG_FLUX_MAX))
        return float(log_flux_geo)

    def predict(self, feature_window_df):
        """
        Generate physics-based forecasts for all three horizons.
        """
        current_log_flux = float(feature_window_df['log_flux'].iloc[-1])
        Kp = float(feature_window_df['Kp'].iloc[-1])
        Pdyn = float(feature_window_df['Pdyn'].iloc[-1] if 'Pdyn' in feature_window_df.columns else 2.0)
        coupling_fn = float(feature_window_df['coupling_fn'].iloc[-1] if 'coupling_fn' in feature_window_df.columns else 0.0)
        
        # 30 min (0.5 hour ahead)
        log_flux_30min = self.solve_diffusion(Kp, Pdyn, coupling_fn, current_log_flux, dt_hours=0.5)
        # 6 hours ahead
        log_flux_6h = self.solve_diffusion(Kp, Pdyn, coupling_fn, current_log_flux, dt_hours=6.0)
        # 12 hours ahead
        log_flux_12h = self.solve_diffusion(Kp, Pdyn, coupling_fn, current_log_flux, dt_hours=12.0)
        
        return {
            '30min': log_flux_30min,
            '6h': log_flux_6h,
            '12h': log_flux_12h
        }
