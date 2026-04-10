import pandas as pd
import numpy as np
from scipy.optimize import minimize
import os
from sklearn.model_selection import ShuffleSplit

# Distribution definitions (as used in previous scripts)
def exp_dist(r, l):
    # k=2: C, l
    if l <= 0: return np.inf * np.ones_like(r)
    return np.exp(-r / l)

def lognormal_dist(r, mu, sigma):
    # k=3: C, mu, sigma
    if sigma <= 0: return np.inf * np.ones_like(r)
    return (1.0 / (r * sigma)) * np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))

def gamma_dist(r, alpha, l):
    # k=3: C, alpha, l
    if l <= 0 or alpha <= 0: return np.inf * np.ones_like(r)
    from scipy.special import gamma
    return (r**(alpha - 1)) * np.exp(-r / l)

def spl_dist(r, r0, beta):
    # k=3: C, r0, beta
    if r0 <= 0 or beta <= 0: return np.inf * np.ones_like(r)
    return (r + r0)**(-beta)

def tlf_dist(r, r0, beta, kappa):
    # k=4: C, r0, beta, kappa
    if r0 <= 0 or beta <= 0 or kappa <= 0: return np.inf * np.ones_like(r)
    return (r + r0)**(-beta) * np.exp(-r / kappa)

def get_nll(params, r, h, dist_func):
    prob = dist_func(r, *params)
    if np.any(prob <= 0) or np.any(np.isinf(prob)) or np.any(np.isnan(prob)):
        return 1e18
    prob_norm = prob / np.sum(prob)
    return -np.sum(h * np.log(prob_norm))

def get_test_nll(params, r_test, h_test, dist_func):
    prob = dist_func(r_test, *params)
    # Clip prob to avoid log(0)
    prob = np.clip(prob, 1e-20, None)
    prob_norm = prob / np.sum(prob)
    return -np.sum(h_test * np.log(prob_norm))

# Setup
def fit_and_evaluate():
    # Load data
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df_regions = pd.read_csv('singapore_40_regions.csv')
    
    # Merge and prepare
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    # Mapping for groups
    # singapore_40_regions.csv has 'zone_id' which maps to ORIGIN_SUBZONE
    group_map = df_regions.set_index('zone_id')['group_id'].to_dict()
    
    # Filter valid zones (as in other scripts)
    zone_trips = df.groupby('ORIGIN_SUBZONE')['COUNT'].sum()
    valid_zones = zone_trips[zone_trips >= 100].index
    df = df[df['ORIGIN_SUBZONE'].isin(valid_zones)]
    df['group_id'] = df['ORIGIN_SUBZONE'].map(group_map)
    df = df.dropna(subset=['group_id'])
    
    groups = df['group_id'].unique()
    n_groups = len(groups)
    
    # To reduce size for iterations, only keep distance and group_id
    df = df[['euclidean_distance_km', 'COUNT', 'group_id']]
    df.columns = ['distance', 'trips', 'group_id']
    
    models = {
        'Exponential': (exp_dist, [5.0], [(0.01, 100.0)]),
        'Lognormal': (lognormal_dist, [1.0, 1.0], [(-10, 10), (0.01, 10)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.01, 20.0), (0.01, 50.0)]),
        'Shifted Power-Law': (spl_dist, [2.0, 3.0], [(0.01, 50.0), (0.01, 15.0)]),
        'Truncated Lévy Flight': (tlf_dist, [2.0, 3.0, 10.0], [(0.01, 50.0), (0.1, 15.0), (1.0, 100.0)])
    }
    
    rs = 50 # Iterations
    ss = ShuffleSplit(n_splits=rs, train_size=30, random_state=42)
    
    results = []
    
    print(f"Starting Spatial Cross-Validation with {rs} iterations...")
    
    for i, (train_idx, test_idx) in enumerate(ss.split(groups)):
        train_groups = groups[train_idx]
        test_groups = groups[test_idx]
        
        df_train_raw = df[df['group_id'].isin(train_groups)]
        df_test_raw = df[df['group_id'].isin(test_groups)]
        
        # Binning for train
        # We pool all trips from train subzones to find the "law"
        bin_width = 1.0
        bins = np.arange(0, df['distance'].max() + bin_width, bin_width)
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        
        # Train histogram
        h_train, _ = np.histogram(df_train_raw['distance'], bins=bins, weights=df_train_raw['trips'])
        mask_train = h_train > 0
        r_tr = bin_centers[mask_train]
        h_tr = h_train[mask_train]
        
        # Test histogram
        h_test, _ = np.histogram(df_test_raw['distance'], bins=bins, weights=df_test_raw['trips'])
        mask_test = h_test > 0
        r_te = bin_centers[mask_test]
        h_te = h_test[mask_test]
        
        fold_res = {'fold': i}
        
        for name, (dist_f, p0, bnds) in models.items():
            res = minimize(get_nll, p0, args=(r_tr, h_tr, dist_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                p_opt = res.x
                # Calculate NLL on test set
                logloss = get_test_nll(p_opt, r_te, h_te, dist_f)
                # Normalize logloss by total trips in test set
                norm_logloss = logloss / np.sum(h_te)
                fold_res[name] = norm_logloss
            else:
                fold_res[name] = np.nan
        
        results.append(fold_res)
        if (i+1) % 10 == 0: print(f"Completed {i+1}/{rs} iterations...")

    df_res = pd.DataFrame(results)
    df_res.to_csv('spatial_cv_results.csv', index=False)
    
    summary = df_res.drop(columns='fold').mean().sort_values()
    print("\n--- Summary of Mean Normalized Log-Loss (Lower is Better) ---")
    print(summary)
    
    # Calculate win rate
    winners = df_res.drop(columns='fold').idxmin(axis=1).value_counts(normalize=True) * 100
    print("\n--- Model Win Rate (%) ---")
    print(winners)

if __name__ == "__main__":
    fit_and_evaluate()
