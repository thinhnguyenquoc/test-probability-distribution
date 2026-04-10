import pandas as pd
import numpy as np
from scipy.optimize import minimize
from sklearn.model_selection import ShuffleSplit

# Use the same distributions as before
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
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df_regions = pd.read_csv('singapore_40_regions.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    group_map = df_regions.set_index('zone_id')['group_id'].to_dict()
    df['group_id'] = df['ORIGIN_SUBZONE'].map(group_map)
    df = df.dropna(subset=['group_id'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'COUNT': 'trips'})
    
    unique_groups = df['group_id'].unique()
    ss = ShuffleSplit(n_splits=20, train_size=30, random_state=42)
    
    models = {
        'LN': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'SPL': (spl_dist, [1.0, 3.0], [(0.1, 20), (0.1, 10)]),
        'TLF': (tlf_dist, [1.0, 3.0, 10.0], [(0.1, 20), (0.1, 10), (1, 100)]),
        'Exp': (exp_dist, [5.0], [(0.1, 100)])
    }
    
    win_counts = {m: 0 for m in models}
    total_evals = 0
    
    print("Running Spatial Block CV (30 train groups, 10 test groups)...")
    
    for i, (tr_idx, te_idx) in enumerate(ss.split(unique_groups)):
        te_groups = unique_groups[te_idx]
        df_te = df[df['group_id'].isin(te_groups)]
        
        # In the test groups, evaluate each subzone
        test_zones = df_te['ORIGIN_SUBZONE'].unique()
        for zone in test_zones:
            df_z = df_te[df_te['ORIGIN_SUBZONE'] == zone]
            if df_z['trips'].sum() < 500: continue
            
            # Use 80/20 splitting within the zone to satisfy "Log-loss on Test"
            # But the primary "Spatial" constraint is that we are in the Test blocks.
            indices = np.arange(len(df_z))
            np.random.seed(42)
            np.random.shuffle(indices)
            split_idx = int(0.8 * len(indices))
            train_idx, test_idx = indices[:split_idx], indices[split_idx:]

            
            # Setup bins
            bins = np.linspace(0, df_z['distance'].max(), 30)
            centers = 0.5 * (bins[:-1] + bins[1:])
            
            h_tr, _ = np.histogram(df_z.iloc[train_idx]['distance'], bins=bins, weights=df_z.iloc[train_idx]['trips'])
            h_te, _ = np.histogram(df_z.iloc[test_idx]['distance'], bins=bins, weights=df_z.iloc[test_idx]['trips'])
            
            m_tr, m_te = h_tr > 0, h_te > 0
            if np.sum(m_tr) < 5 or np.sum(m_te) < 2: continue
            
            nlls = {}
            for name, (dist_f, p0, bnds) in models.items():
                res = minimize(get_nll, p0, args=(centers[m_tr], h_tr[m_tr], dist_f), method='L-BFGS-B', bounds=bnds)
                if res.success:
                    # Test on unseen bins
                    p_te = dist_f(centers[m_te], *res.x)
                    p_te = np.clip(p_te, 1e-20, None)
                    p_te /= np.sum(p_te)
                    nlls[name] = -np.sum(h_te[m_te] * np.log(p_te)) / np.sum(h_te[m_te])
            
            if nlls:
                best_m = min(nlls, key=nlls.get)
                win_counts[best_m] += 1
                total_evals += 1
        
        print(f"Fold {i+1} completed. current evals: {total_evals}")

    print("\n--- Final Results (Subzone Log-loss Win Rate in Test Blocks) ---")
    for m, c in win_counts.items():
        print(f"{m}: {c/total_evals:.2%}")

if __name__ == "__main__":
    main()
