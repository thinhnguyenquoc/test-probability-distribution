import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import lognorm, gamma, expon

# Unified Color Palette
COLORS = {
    'Lognormal': '#1f77b4',      # Blue
    'Gamma': '#2ca02c',          # Green
    'TLF': '#41b6c4',            # Teal
    'SPL': '#ff7f0e',            # Orange
    'Exponential': '#d62728',    # Red
    'Empirical': '#8c564b'       # Brown
}

# Model Definitions
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

def main():
    print("Loading data...")
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'COUNT': 'trips'})
    
    # Global aggregation
    bins = np.linspace(0, df['distance'].max(), 51)
    centers = 0.5 * (bins[:-1] + bins[1:])
    h, _ = np.histogram(df['distance'], bins=bins, weights=df['trips'])
    mask = h > 0
    r_data, h_data = centers[mask], h[mask]
    y_prob = h_data / np.sum(h_data)
    
    # Models to fit
    models = {
        'Lognormal': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'TLF': (tlf_dist, [1.0, 2.0, 20.0], [(0.1, 20), (0.1, 10), (1, 100)]),
        'SPL': (spl_dist, [1.0, 2.0], [(0.1, 20), (0.1, 15)]),
        'Exponential': (exp_dist, [5.0], [(0.1, 100)])
    }
    
    fits = {}
    print("Fitting models...")
    for name, (dist_f, p0, bnds) in models.items():
        res = minimize(get_nll, p0, args=(r_data, h_data, dist_f), method='L-BFGS-B', bounds=bnds)
        if res.success:
            p_opt = dist_f(r_data, *res.x)
            p_opt /= np.sum(p_opt)
            fits[name] = p_opt
    
    # Plotting
    print("Generating combined plot...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # (A) Histogram / PDF (Linear)
    ax = axes[0]
    ax.bar(r_data, y_prob, width=(bins[1]-bins[0])*0.8, color=COLORS['Empirical'], alpha=0.3, label='Dữ liệu thực tế')
    for name, y_fit in fits.items():
        ax.plot(r_data, y_fit, color=COLORS[name], linewidth=2, label=name)
    ax.set_xlabel('Khoảng cách $r$ (km)')
    ax.set_ylabel('Xác suất $P(r)$')
    ax.set_title('(A) Histogram (PDF Linear)')
    ax.legend(fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.6)

    # (B) Log-Log Plot
    ax = axes[1]
    ax.loglog(r_data, y_prob, 'o', color=COLORS['Empirical'], alpha=0.5, markersize=4, label='Dữ liệu thực tế')
    for name, y_fit in fits.items():
        ax.loglog(r_data, y_fit, color=COLORS[name], linewidth=2, label=name)
    ax.set_xlabel('$\log r$')
    ax.set_ylabel('$\log P(r)$')
    ax.set_title('(B) Log-Log PDF')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    
    # (C) CCDF
    ax = axes[2]
    ccdf_data = 1 - np.cumsum(y_prob)
    ax.loglog(r_data, ccdf_data, 'o', color=COLORS['Empirical'], alpha=0.5, markersize=4, label='Dữ liệu thực tế')
    for name, y_fit in fits.items():
        ccdf_fit = 1 - np.cumsum(y_fit)
        # Ensure it doesn't drop to 0 for log plot
        ccdf_fit = np.clip(ccdf_fit, 1e-10, None)
        ax.loglog(r_data, ccdf_fit, color=COLORS[name], linewidth=2, label=name)
    ax.set_xlabel('$\log r$')
    ax.set_ylabel('$\log P(R > r)$')
    ax.set_title('(C) CCDF (Log-Log)')
    ax.grid(True, which="both", ls="-", alpha=0.2)

    plt.tight_layout()
    plt.savefig('global_distributions_combined.png', dpi=300)
    print("Plot saved to global_distributions_combined.png")

if __name__ == "__main__":
    main()
