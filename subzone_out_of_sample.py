import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.model_selection import KFold

# Distribution definitions
def exp_dist(r, l):
    if l <= 0: return np.inf * np.ones_like(r)
    return np.exp(-r / l)

def lognormal_dist(r, mu, sigma):
    if sigma <= 0: return np.inf * np.ones_like(r)
    return (1.0 / (r * sigma)) * np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))

def gamma_dist(r, alpha, l):
    if l <= 0 or alpha <= 0: return np.inf * np.ones_like(r)
    from scipy.special import gamma
    return (r**(alpha - 1)) * np.exp(-r / l)

def spl_dist(r, r0, beta):
    if r0 <= 0 or beta <= 0: return np.inf * np.ones_like(r)
    return (r + r0)**(-beta)

def tlf_dist(r, r0, beta, kappa):
    if r0 <= 0 or beta <= 0 or kappa <= 0: return np.inf * np.ones_like(r)
    return (r + r0)**(-beta) * np.exp(-r / kappa)

def get_nll(params, r, h, dist_func):
    prob = dist_func(r, *params)
    if np.any(prob <= 0) or np.any(np.isinf(prob)) or np.any(np.isnan(prob)):
        return 1e18
    prob_norm = prob / np.sum(prob)
    return -np.sum(h * np.log(prob_norm))

def main():
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'COUNT': 'trips'})
    
    zones = df.groupby('ORIGIN_SUBZONE')['trips'].sum()
    valid_zones = zones[zones >= 1000].index # Use high-count zones for stability
    
    models = {
        'Exponential': (exp_dist, [5.0], [(0.01, 100.0)]),
        'Lognormal': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.01, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10.0), (0.1, 30.0)]),
        'SPL': (spl_dist, [1.0, 3.0], [(0.01, 20.0), (0.1, 10.0)]),
        'TLF': (tlf_dist, [1.0, 3.0, 10.0], [(0.01, 20.0), (0.1, 10.0), (1.0, 100.0)])
    }
    
    results = []
    
    print(f"Running Out-of-Sample evaluation for {len(valid_zones[:50])} subzones...")
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    for zone in valid_zones[:50]: # Limit to 50 for speed
        df_z = df[df['ORIGIN_SUBZONE'] == zone]
        
        # We split OD pairs
        indices = np.arange(len(df_z))
        
        zone_cv = {'zone': zone}
        for name in models: zone_cv[name] = []
        
        for train_idx, test_idx in kf.split(indices):
            train_data = df_z.iloc[train_idx]
            test_data = df_z.iloc[test_idx]
            
            # Simple binning for train
            bins = np.linspace(0, df_z['distance'].max(), 20)
            centers = 0.5 * (bins[:-1] + bins[1:])
            
            h_tr, _ = np.histogram(train_data['distance'], bins=bins, weights=train_data['trips'])
            m_tr = h_tr > 0
            r_tr, count_tr = centers[m_tr], h_tr[m_tr]
            
            h_te, _ = np.histogram(test_data['distance'], bins=bins, weights=test_data['trips'])
            m_te = h_te > 0
            r_te, count_te = centers[m_te], h_te[m_te]
            
            if len(r_tr) < 4 or len(r_te) < 2: continue
            
            for name, (dist_f, p0, bnds) in models.items():
                res = minimize(get_nll, p0, args=(r_tr, count_tr, dist_f), method='L-BFGS-B', bounds=bnds)
                if res.success:
                    # Evaluate NLL on test set
                    prob_te = dist_f(r_te, *res.x)
                    prob_te = np.clip(prob_te, 1e-20, None)
                    prob_te_norm = prob_te / np.sum(prob_te)
                    nll_te = -np.sum(count_te * np.log(prob_te_norm))
                    zone_cv[name].append(nll_te / np.sum(count_te))
        
        # Average across folds
        final_row = {'zone': zone}
        for name in models:
            final_row[name] = np.mean(zone_cv[name]) if zone_cv[name] else np.nan
        results.append(final_row)

    df_res = pd.DataFrame(results).dropna()
    print("\n--- Mean Normalized Log-Loss across Subzones ---")
    print(df_res.drop(columns='zone').mean().sort_values())
    
    winners = df_res.drop(columns='zone').idxmin(axis=1).value_counts(normalize=True) * 100
    print("\n--- Win Rate (%) ---")
    print(winners)

if __name__ == "__main__":
    main()
