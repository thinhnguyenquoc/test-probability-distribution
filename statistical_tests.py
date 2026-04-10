import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2, norm

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

def vuong_test(r, h, p1, p2):
    """
    Perform Vuong's test for non-nested models.
    p1, p2 are the probability vectors for model 1 and model 2 at centers r.
    h is the observation count (trips).
    """
    lr = np.log(p1 / p2)
    llr = h * lr
    # Pointwise contribution to LLH ratio across bins
    mean_llr = np.sum(llr) / np.sum(h)
    std_llr = np.sqrt(np.sum(h * (lr - mean_llr)**2) / np.sum(h)) # Weighted std
    
    if std_llr == 0: return 0.0
    v_stat = np.sum(llr) / (std_llr * np.sqrt(np.sum(h)))
    return v_stat

def lrt_test(nll1, nll2, df):
    """
    Perform Likelihood Ratio Test for nested models.
    nll1: Null model NLL, nll2: Alternative model NLL
    df: Difference in degrees of freedom
    """
    lr_stat = 2 * (nll1 - nll2)
    p_val = chi2.sf(lr_stat, df)
    return lr_stat, p_val

def main():
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone'})
    
    # Nested Relationships
    # Exp (k=2) -> Gamma (k=3)
    # SPL (k=3) -> TLF (k=4)
    
    # Non-nested: LN (k=3) vs Gamma (k=3)
    # LN (k=3) vs SPL (k=3)
    
    # We analyze District Scale (Macro) as a case study for significance
    df_district_zone = pd.read_csv('district_zone.csv')
    dist_map = df_district_zone.set_index('zone_id')['district_id'].to_dict()
    df['district'] = df['zone'].map(dist_map)
    df_macro = df.dropna(subset=['district']).groupby(['district', 'distance'])['COUNT'].sum().reset_index()
    
    models = {
        'Exp': (exp_dist, [5.0], [(0.1, 100)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'SPL': (spl_dist, [1.0, 3.0], [(0.1, 20), (0.1, 15)]),
        'TLF': (tlf_dist, [1.0, 3.0, 10.0], [(0.1, 20), (0.1, 10), (1, 100)]),
        'LN': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)])
    }
    
    district_ids = df_macro['district'].unique()
    
    print("--- Statistical Tests for Model Comparison at District Scale ---")
    
    for dist in district_ids:
        df_d = df_macro[df_macro['district'] == dist]
        bins = np.linspace(0, df_d['distance'].max(), 30)
        centers = 0.5 * (bins[:-1] + bins[1:])
        h, _ = np.histogram(df_d['distance'], bins=bins, weights=df_d['COUNT'])
        mask = h > 0
        r_f, h_f = centers[mask], h[mask]
        
        fits = {}
        for name, (dist_f, p0, bnds) in models.items():
            res = minimize(get_nll, p0, args=(r_f, h_f, dist_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                p = dist_f(r_f, *res.x)
                p /= np.sum(p)
                fits[name] = {'nll': res.fun, 'p': p}
        
        print(f"\nDistrict {dist}:")
        
        # 1. LRT: Exp vs Gamma
        if 'Exp' in fits and 'Gamma' in fits:
            stat, pval = lrt_test(fits['Exp']['nll'], fits['Gamma']['nll'], 1)
            print(f"  Nested LRT (Exp vs Gamma): Stat={stat:.2f}, p={pval:.4f} {'Significant' if pval<0.05 else 'Not Sig'}")

        # 2. LRT: SPL vs TLF
        if 'SPL' in fits and 'TLF' in fits:
            stat, pval = lrt_test(fits['SPL']['nll'], fits['TLF']['nll'], 1)
            print(f"  Nested LRT (SPL vs TLF): Stat={stat:.2f}, p={pval:.4f} {'Significant' if pval<0.05 else 'Not Sig'}")

        # 3. Vuong: LN vs Gamma
        if 'LN' in fits and 'Gamma' in fits:
            v_stat = vuong_test(r_f, h_f, fits['LN']['p'], fits['Gamma']['p'])
            print(f"  Vuong Test (LN vs Gamma, + is LN): V={v_stat:.4f} (Sig if |V|>1.96)")

        # 4. Vuong: LN vs TLF
        if 'LN' in fits and 'TLF' in fits:
            v_stat = vuong_test(r_f, h_f, fits['LN']['p'], fits['TLF']['p'])
            print(f"  Vuong Test (LN vs TLF, + is LN): V={v_stat:.4f} (Sig if |V|>1.96)")

if __name__ == "__main__":
    main()
