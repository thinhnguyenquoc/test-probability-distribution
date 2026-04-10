import pandas as pd
import numpy as np
from scipy.optimize import minimize
import scipy.stats as stats
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

print("Loading data and 40 groups mapping...")
df_trips = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/data_trip_sum.csv')
df_dist = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/zone_euclid_distances.csv')
groups_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv')

# Merge trips and distances
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

# Map subzone to group_id
map_dict = dict(zip(groups_df['zone_id'], groups_df['group_id']))
df['group_id'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['group_id'])

def r2_score_custom(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

def exp_dist(r, C, lam): return C * np.exp(-r / lam)
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def tlf_model(r, C, r0, beta, kappa): return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))
def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

models = {
    'Exponential': (exp_dist, [1, 5], 2, ([0, 1e-3], [np.inf, np.inf])),
    'Lognormal': (lognormal_dist, [1, 1, 1], 3, ([0, -np.inf, 1e-3], [np.inf, np.inf, np.inf])),
    'Gamma': (gamma_dist, [1, 2, 2], 3, ([0, 1e-3, 1e-3], [np.inf, 20, np.inf])),
    'Shifted Power-Law': (shift_power_law, [1, 1, 2], 3, ([0, 1e-3, 1e-3], [np.inf, np.inf, 15])),
    'Truncated Lévy Flight': (tlf_model, [1, 1, 2, 50], 4, ([0, 1e-3, 1e-3, 1e-3], [np.inf, np.inf, 15, np.inf]))
}

results = []
groups_list = sorted(df['group_id'].unique())
print(f"Starting fitting for {len(groups_list)} groups...")

for group_id, group_data in df.groupby('group_id'):
    total_trips = group_data['COUNT'].sum()
    if total_trips < 50 or len(group_data) < 5:
        continue
    
    distances = group_data['euclidean_distance_km'].values
    counts = group_data['COUNT'].values
    
    num_bins = min(30, len(np.unique(distances)))
    if num_bins < 3:
        continue
        
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask = (hist > 0) & (bin_centers > 0)
    if mask.sum() < 4:
        continue
        
    x_data = bin_centers[mask]
    y_counts = hist[mask]
    y_prob = y_counts / total_trips
    
    empirical_cdf = np.cumsum(y_prob)
    group_res = {}
    
    for name, (func, p0, k, bounds) in models.items():
        try:
            def nll(params):
                y_raw = func(x_data, *params)
                if np.sum(y_raw) <= 0 or np.any(y_raw < 0): return 1e18
                y_pmf = y_raw / np.sum(y_raw)
                return -np.sum(y_counts * np.log(np.clip(y_pmf, 1e-300, 1)))

            bnds = list(zip(bounds[0], bounds[1]))
            res = minimize(nll, p0, method='L-BFGS-B', bounds=bnds)
            if not res.success: res = minimize(nll, p0, method='Nelder-Mead', bounds=bnds)
            
            popt = res.x
            y_fit_raw = func(x_data, *popt)
            y_fit_pmf = y_fit_raw / np.sum(y_fit_raw)
            
            r2 = r2_score_custom(y_prob, y_fit_raw)
            model_cdf = np.cumsum(y_fit_pmf)
            ks_stat = np.max(np.abs(empirical_cdf - model_cdf))
            
            log_likelihood = -res.fun
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(total_trips) - 2 * log_likelihood
            
            # AD Stat
            fit_cdf_diff = np.diff(np.insert(model_cdf, 0, 0))
            ad_num = (empirical_cdf - model_cdf)**2
            ad_den = np.clip(model_cdf * (1 - model_cdf), 1e-6, None)
            ad_stat = total_trips * np.sum((ad_num / ad_den) * fit_cdf_diff)

            group_res[name] = {
                'KS_Stat': round(ks_stat, 4),
                'AD_Stat': round(ad_stat, 4),
                'Log_Likelihood': round(log_likelihood, 2),
                'AIC': round(aic, 2),
                'BIC': round(bic, 2),
                'k': k
            }

        except:
            pass
            
    if len(group_res) == 0:
        continue
        
    best_model = min(group_res.keys(), key=lambda m: group_res[m]['BIC'])
    
    for name, metrics in group_res.items():
        results.append({
            'group_id': group_id,
            'Total_Trips': total_trips,
            'Model': name,
            'KS_Stat': metrics['KS_Stat'],
            'AD_Stat': metrics['AD_Stat'],
            'Log_Likelihood': metrics['Log_Likelihood'],
            'AIC': metrics['AIC'],
            'BIC': metrics['BIC'],

            'Is_Best_BIC': (name == best_model)
        })

res_df = pd.DataFrame(results)
res_df.to_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/group_40_distribution_metrics.csv', index=False)

# Analysis Report
print("\n=== BEST MODELS AT 40-GROUPS SCALE (BIC) ===")
best_df = res_df[res_df['Is_Best_BIC'] == True]
best_counts = best_df['Model'].value_counts()
print(best_counts)

# Summary for District comparison (Assuming previous results were: Exponential: 2, SPL: 2, Gamma: 1)
print("\nComparison with 5 District scale:")
print("District level: Mostly Split between Exponential and SPL.")

# Visualization
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
best_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Best Model Counts (40 Groups)')
plt.ylabel('Number of Groups')

plt.subplot(1, 2, 2)
best_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, cmap='Pastel1')
plt.title('Best Model Distribution')
plt.tight_layout()
plt.savefig('/Users/nguyenquocthinh/Documents/test-probability-distribution/group_40_distribution_comparison.png', dpi=300)
print(f"Plot saved to group_40_distribution_comparison.png")
