import pandas as pd
import numpy as np
from scipy.optimize import minimize

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
    x_data = bin_centers[mask]
    y_counts = hist[mask]
    y_prob = y_counts / total_trips
    
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
    
    print(f"| Model | R2 | Log-Likelihood | AIC | BIC | KS-stat |")
    print(f"|---|---|---|---|---|---|")
    for name, (func, p0, k, bounds) in models.items():
        try:
            # Objective function for MLE: Negative Log-Likelihood
            def nll(params):
                y_raw = func(x_data, *params)
                if np.sum(y_raw) <= 0 or np.any(y_raw < 0):
                    return 1e18
                y_pmf = y_raw / np.sum(y_raw)
                y_safe = np.clip(y_pmf, 1e-300, 1)
                return -np.sum(y_counts * np.log(y_safe))

            bnds = list(zip(bounds[0], bounds[1]))
            res = minimize(nll, p0, method='L-BFGS-B', bounds=bnds)
            
            popt = res.x
            y_fit_raw = func(x_data, *popt)
            y_fit_pmf = y_fit_raw / np.sum(y_fit_raw)
            
            r2 = 1 - np.sum((y_prob - y_fit_pmf)**2) / np.sum((y_prob - np.mean(y_prob))**2)
            ll = -res.fun
            aic = 2 * k - 2 * ll
            bic = k * np.log(total_trips) - 2 * ll
            
            # KS
            y_cdf = np.cumsum(y_prob)
            fit_cdf = np.cumsum(y_fit_pmf)
            ks = np.max(np.abs(y_cdf - fit_cdf))
            print(f"| {name} | {r2:.4f} | {ll:,.0f} | {aic:,.0f} | {bic:,.0f} | {ks:.4f} |")
        except Exception as e:
            print(f"| {name} | Error: {e} | - | - |")

if __name__ == "__main__":
    run_global_analysis()
