import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Distributions
def exp_dist(r, l): return np.exp(-r / l) if l > 0 else np.inf * np.ones_like(r)
def lognormal_dist(r, mu, sigma): return (1.0/(r*sigma)) * np.exp(-(np.log(r)-mu)**2/(2*sigma**2)) if sigma > 0 else np.inf * np.ones_like(r)
def gamma_dist(r, alpha, l): return (r**(alpha-1)) * np.exp(-r/l) if l > 0 and alpha > 0 else np.inf * np.ones_like(r)
def spl_dist(r, r0, beta): return (r+r0)**(-beta) if r0 > 0 and beta > 0 else np.inf * np.ones_like(r)
def tlf_dist(r, r0, beta, kappa): return (r+r0)**(-beta) * np.exp(-r/kappa) if r0 > 0 and beta > 0 and kappa > 0 else np.inf * np.ones_like(r)

def get_nll(params, r, h, dist_f):
    p = dist_f(r, *params)
    if np.any(p <= 0) or np.any(np.isinf(p)): return 1e18
    p /= np.sum(p)
    return -np.sum(h * np.log(p))

def calculate_residuals(r, h, p_model, N):
    # p_model is normalized probability vector
    expected = N * p_model
    # Standardized residual
    # Avoid zero division
    denom = np.sqrt(N * p_model * (1 - p_model))
    resid = (h - expected) / np.where(denom > 0, denom, 1e-10)
    return resid

def main():
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'COUNT': 'trips'})
    
    # We analyze the Global scale (Singapore-wide) for a clear trend
    N = df['trips'].sum()
    bins = np.linspace(0, df['distance'].max(), 50)
    centers = 0.5 * (bins[:-1] + bins[1:])
    h, _ = np.histogram(df['distance'], bins=bins, weights=df['trips'])
    mask = h > 0
    r_fit, h_fit = centers[mask], h[mask]
    
    models = {
        'Lognormal': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)], 'blue'),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)], 'green'),
        'SPL': (spl_dist, [1.0, 3.0], [(0.1, 20), (0.1, 15)], 'red')
    }
    
    plt.figure(figsize=(12, 6))
    
    for name, (dist_f, p0, bnds, color) in models.items():
        res = minimize(get_nll, p0, args=(r_fit, h_fit, dist_f), method='L-BFGS-B', bounds=bnds)
        if res.success:
            p_opt = dist_f(r_fit, *res.x)
            p_opt /= np.sum(p_opt)
            residuals = calculate_residuals(r_fit, h_fit, p_opt, np.sum(h_fit))
            
            plt.plot(r_fit, residuals, marker='o', linestyle='-', label=name, color=color, alpha=0.7)
            
            # Print average abs residual for reference
            print(f"{name} Mean Abs Residual: {np.mean(np.abs(residuals)):.2f}")

    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel('Distance (km)')
    plt.ylabel('Standardized Residuals')
    plt.title('Residual Analysis across Scales (Global Scale)')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.savefig('residual_analysis_plot.png')
    print("Residual plot saved as residual_analysis_plot.png")

if __name__ == "__main__":
    main()
