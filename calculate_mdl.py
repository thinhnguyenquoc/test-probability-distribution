import pandas as pd
import numpy as np
from scipy.optimize import minimize
import os

# Distribution definitions
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

def calculate_mdl(nll, k, n_bins):
    """
    MDL approximation: NLL + (k/2) * log(n_bins)
    Note: Using n_bins as N for MDL since we fit on histogram bins.
    """
    if n_bins <= 0: return np.inf
    return nll + (k/2) * np.log(n_bins)

def analyze_scale(df, label, n_params_dict):
    zones = df['zone'].unique()
    results = []
    
    models = {
        'Exp': (exp_dist, [5.0], [(0.1, 100)]),
        'LN': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'SPL': (spl_dist, [1.0, 3.0], [(0.1, 20), (0.1, 15)]),
        'TLF': (tlf_dist, [1.0, 3.0, 10.0], [(0.1, 20), (0.1, 10), (1, 100)])
    }
    
    for zone in zones:
        df_z = df[df['zone'] == zone]
        if df_z['COUNT'].sum() < 100: continue
        
        # Binning
        bins = np.linspace(0, df_z['distance'].max(), 30)
        centers = 0.5 * (bins[:-1] + bins[1:])
        h, _ = np.histogram(df_z['distance'], bins=bins, weights=df_z['COUNT'])
        mask = h > 0
        r_fit, h_fit = centers[mask], h[mask]
        n_bins = np.sum(mask)
        
        if n_bins < 5: continue
        
        mdls = {}
        for name, (dist_f, p0, bnds) in models.items():
            res = minimize(get_nll, p0, args=(r_fit, h_fit, dist_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                k = len(p0) + 1 # +1 for normalization constant C
                mdls[name] = calculate_mdl(res.fun, k, n_bins)
        
        if mdls:
            best = min(mdls, key=mdls.get)
            mdls['zone'] = zone
            mdls['best'] = best
            results.append(mdls)
            
    res_df = pd.DataFrame(results)
    print(f"\n--- MDL Results for {label} ---")
    print(res_df['best'].value_counts(normalize=True) * 100)
    return res_df

def main():
    # Load data
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone'})
    
    # Analyze Subzones (Micro)
    analyze_scale(df, "Subzone (Micro)", {})
    
    # Analyze Districts (Macro)
    df_district_zone = pd.read_csv('district_zone.csv')
    dist_map = df_district_zone.set_index('zone_id')['district_id'].to_dict()
    df['district'] = df['zone'].map(dist_map)
    df_districts = df.dropna(subset=['district']).copy()
    df_districts['zone'] = df_districts['district']
    analyze_scale(df_districts, "District (Macro)", {})

if __name__ == "__main__":
    main()
