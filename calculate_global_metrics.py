import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

def run_global_analysis():
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    
    total_trips = df['COUNT'].sum()
    distances = df['euclidean_distance_km'].values
    counts = df['COUNT'].values
    
    # 50 bins
    bins = np.linspace(0.1, np.max(distances), 51)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    mask = hist > 0
    x = bin_centers[mask]
    y = hist[mask] / total_trips
    
    def lognormal_dist(r, C, mu, sigma):
        r_safe = np.clip(r, 1e-5, None)
        return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

    def shift_power_law(r, C, r0, beta):
        return C * (r + r0)**(-beta)

    def exp_dist(r, C, lam):
        return C * np.exp(-r / lam)

    def gamma_dist(r, C, alpha, lam):
        r_safe = np.clip(r, 1e-5, None)
        return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

    def tlf_dist(r, C, r0, beta, kappa):
        r_safe = np.clip(r, 1e-5, None)
        return C * (r_safe + r0)**(-beta) * np.exp(-r_safe / kappa)

    models = {
        'Exponential': (exp_dist, [1, 5], 2, ([0, 0.1], [np.inf, 100])),
        'Lognormal': (lognormal_dist, [1, 1, 1], 3, ([0, -10, 0.1], [np.inf, 10, 10])),
        'Gamma': (gamma_dist, [1, 2, 2], 3, ([0, 0.1, 0.1], [np.inf, 100, 100])),
        'Shifted Power-Law': (shift_power_law, [1, 1, 2], 3, ([0, 0.1, 0.1], [np.inf, 50, 20])),
        'Truncated Levy Flight': (tlf_dist, [1, 1, 2, 10], 4, ([0, 0.1, 0.1, 0.1], [np.inf, 50, 20, 100]))
    }
    
    print(f"| Model | R2 | BIC | KS-stat |")
    print(f"|---|---|---|---|")
    for name, (func, p0, k, bounds) in models.items():
        try:
            popt, _ = curve_fit(func, x, y, p0=p0, bounds=bounds, maxfev=50000)
            y_fit = func(x, *popt)
            r2 = 1 - np.sum((y - y_fit)**2) / np.sum((y - np.mean(y))**2)
            # Log likelihood for BIC
            y_fit_norm = y_fit / np.sum(y_fit)
            ll = np.sum((y * total_trips) * np.log(np.clip(y_fit_norm, 1e-300, 1)))
            bic = k * np.log(total_trips) - 2 * ll
            # KS
            y_cdf = np.cumsum(y / np.sum(y))
            fit_cdf = np.cumsum(y_fit_norm)
            ks = np.max(np.abs(y_cdf - fit_cdf))
            print(f"| {name} | {r2:.4f} | {bic:,.0f} | {ks:.4f} |")
        except Exception as e:
            print(f"| {name} | Error: {e} | - | - |")

if __name__ == "__main__":
    run_global_analysis()
