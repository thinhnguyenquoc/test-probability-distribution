import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.cluster import KMeans

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

def run_analysis(df, k_groups):
    # Perform grouping
    # For simplicity, we use K-Means on the district centers or just random subzone samples coordinates if coords available
    # Actually, we'll use the 'zone' level data and group zones
    zones = df['zone'].unique()
    num_zones = len(zones)
    
    # Simulate geographic grouping if coordinates missing, or check if we have them
    # For now, we'll just partition the 303 subzones into K groups to test scale effect
    group_size = num_zones // k_groups
    indices = np.arange(num_zones)
    np.random.shuffle(indices)
    
    zone_to_group = {}
    for i, idx in enumerate(indices):
        grp = min(i // (group_size + 1), k_groups - 1) if num_zones % k_groups != 0 else i // group_size
        zone_to_group[zones[idx]] = grp
    
    df['temp_group'] = df['zone'].map(zone_to_group)
    df_grouped = df.groupby(['temp_group', 'distance'])['trips'].sum().reset_index()
    
    models = {
        'LN': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'TLF': (tlf_dist, [1.0, 2.0, 20.0], [(0.1, 20), (0.1, 10), (1, 100)]),
        'SPL': (spl_dist, [1.0, 2.0], [(0.1, 20), (0.1, 15)])
    }
    
    winners = []
    for gId in range(k_groups):
        df_g = df_grouped[df_grouped['temp_group'] == gId]
        if df_g['trips'].sum() < 100: continue
        
        bins = np.linspace(0, df_g['distance'].max(), 30)
        centers = 0.5 * (bins[:-1] + bins[1:])
        h, _ = np.histogram(df_g['distance'], bins=bins, weights=df_g['trips'])
        mask = h > 0
        r_f, h_f = centers[mask], h[mask]
        N = np.sum(h_f)
        
        bics = {}
        for name, (dist_f, p0, bnds) in models.items():
            res = minimize(get_nll, p0, args=(r_f, h_f, dist_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                k = len(p0)
                bics[name] = 2 * res.fun + k * np.log(N)
        
        if bics:
            winners.append(min(bics, key=bics.get))
            
    win_counts = pd.Series(winners).value_counts(normalize=True) * 100
    return win_counts

def main():
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone', 'COUNT': 'trips'})
    
    print("--- Sensitivity Analysis for Number of Intermediate Groups ---")
    for k in [30, 40, 50]:
        print(f"\nScenario: K = {k} groups")
        results = run_analysis(df, k)
        print(results)

if __name__ == "__main__":
    main()
