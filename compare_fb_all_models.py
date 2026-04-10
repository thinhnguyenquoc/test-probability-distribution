"""
Table 4: Facebook Validation — All 5 Models vs Facebook Ground-Truth
So sánh Wasserstein (EMD) của 5 mô hình vs Facebook Mobility Data, per district.

Input:  data_trip_sum.csv, zone_euclid_distances.csv, district_zone.csv, fb_agg.csv
Output: fb_vs_all_models.csv
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import wasserstein_distance
import warnings
warnings.filterwarnings('ignore')

# ─── Load data ───
print("Loading data...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist  = pd.read_csv('zone_euclid_distances.csv')
dz       = pd.read_csv('district_zone.csv')
fb       = pd.read_csv('fb_agg.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
map_dict   = dict(zip(dz['zone_id'], dz['district_id']))
name_dict  = dict(zip(dz['district_id'], dz['district_name']))
df['district_id'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district_id'])

# ─── Facebook bins ───
def bin_distance(d):
    if d < 1:      return '(0,1)'
    elif d < 10:   return '[1, 10)'
    elif d < 100:  return '[10, 100)'
    else:          return '100+'

cat_order = ['(0,1)', '[1, 10)', '[10, 100)', '100+']

# ─── 5 distribution functions ───
def exp_dist(r, C, lam):
    return C * np.exp(-r / lam)

def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(r_safe) - mu)**2 / (2 * sigma**2))

def tlf_model(r, C, r0, beta, kappa):
    return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)

def shift_power_law(r, C, r0, beta):
    return C * (r + r0)**(-beta)

models = {
    'Exponential':    (exp_dist,        [1, 5],        ([0, 1e-3], [np.inf, np.inf])),
    'Gamma':          (gamma_dist,      [1, 2, 2],     ([0, 1e-3, 1e-3], [np.inf, 20, np.inf])),
    'Lognormal':      (lognormal_dist,  [1, 1, 1],     ([0, -np.inf, 1e-3], [np.inf, np.inf, np.inf])),
    'TLF':            (tlf_model,       [1, 1, 2, 50], ([0, 1e-3, 1e-3, 1e-3], [np.inf, np.inf, 15, np.inf])),
    'SPL':            (shift_power_law, [1, 1, 2],     ([0, 1e-3, 1e-3], [np.inf, np.inf, 15])),
}

# ─── Per-district analysis ───
results = []
districts_list = sorted(df['district_id'].unique())

print(f"\nPhân tích {len(districts_list)} districts × {len(models)} models...")
print("=" * 100)

for d_id in districts_list:
    group = df[df['district_id'] == d_id]
    total_trips = group['COUNT'].sum()
    if total_trips == 0:
        continue

    distances = group['euclidean_distance_km'].values
    counts    = group['COUNT'].values
    d_name    = name_dict.get(d_id, d_id)

    # Histogram for fitting
    num_bins = min(50, len(np.unique(distances)))
    if num_bins < 3:
        continue
    bins_arr = np.linspace(0, np.max(distances), num_bins + 1)
    hist, bin_edges = np.histogram(distances, bins=bins_arr, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    mask = hist > 0
    x_data = bin_centers[mask]
    y_prob = hist[mask] / total_trips

    # Ground truth binned to FB categories
    group = group.copy()
    group['P_gt'] = group['COUNT'] / total_trips
    group['category'] = group['euclidean_distance_km'].apply(bin_distance)
    gt_cat = group.groupby('category')['P_gt'].sum().reindex(cat_order).fillna(0)
    p_gt = gt_cat.values
    p_gt = p_gt / p_gt.sum() if p_gt.sum() > 0 else p_gt

    # Facebook data for this district
    fb_d = fb[fb['district_id'] == d_id].set_index('category')['p_fb'].reindex(cat_order).fillna(0)
    p_fb = fb_d.values
    p_fb = p_fb / p_fb.sum() if p_fb.sum() > 0 else p_fb

    # GT vs Facebook EMD (baseline)
    emd_gt = wasserstein_distance(range(len(cat_order)), range(len(cat_order)), p_gt, p_fb)

    for model_name, (func, p0, bounds) in models.items():
        try:
            def nll(params):
                y_raw = func(x_data, *params)
                if np.sum(y_raw) <= 0 or np.any(y_raw < 0): return 1e18
                y_pmf = y_raw / np.sum(y_raw)
                return -np.sum(y_counts * np.log(np.clip(y_pmf, 1e-300, 1)))

            # Use Nelder-Mead for very small data sets (like districts)
            res = minimize(nll, p0, method='Nelder-Mead')
            popt = res.x
            
            # Predict on all OD pairs, then bin to FB categories
            raw_pred = func(group['euclidean_distance_km'].values, *popt)
            if np.any(np.isnan(raw_pred)) or np.sum(raw_pred) <= 0:
                continue
            group[f'P_{model_name}'] = raw_pred / np.sum(raw_pred)

            pred_cat = group.groupby('category')[f'P_{model_name}'].sum().reindex(cat_order).fillna(0)
            p_model = pred_cat.values
            p_model = p_model / p_model.sum() if p_model.sum() > 0 else p_model

            # EMD: model vs Facebook
            emd_model_fb = wasserstein_distance(range(len(cat_order)), range(len(cat_order)), p_model, p_fb)
            # EMD: model vs Ground Truth
            emd_model_gt = wasserstein_distance(range(len(cat_order)), range(len(cat_order)), p_model, p_gt)

            results.append({
                'District': d_name,
                'Model': model_name,
                'EMD_vs_FB': round(emd_model_fb, 4),
                'EMD_vs_GT': round(emd_model_gt, 4),
                'EMD_GT_vs_FB': round(emd_gt, 4),
            })
        except Exception as e:
            pass

# ─── Output ───
res_df = pd.DataFrame(results)
res_df.to_csv('fb_vs_all_models.csv', index=False)
print(f"\n>>> Saved: fb_vs_all_models.csv ({len(res_df)} rows)")

# ─── Summary: Mean EMD per model ───
print("\n=== MEAN EMD vs Facebook (across 5 districts) ===")
summary = res_df.groupby('Model')[['EMD_vs_FB', 'EMD_vs_GT']].mean().round(4)
summary = summary.sort_values('EMD_vs_FB')
print(summary.to_string())

# ─── Markdown table: per-model mean ───
print("\n--- Markdown Table (Mean across districts) ---")
print("| Model | EMD vs Facebook | EMD vs Ground Truth |")
print("|-------|-----------------|---------------------|")
for model_name in ['Exponential', 'Gamma', 'Lognormal', 'TLF', 'SPL']:
    sub = res_df[res_df['Model'] == model_name]
    if len(sub) > 0:
        emd_fb = sub['EMD_vs_FB'].mean()
        emd_gt = sub['EMD_vs_GT'].mean()
        print(f"| {model_name:13s} | {emd_fb:.4f}          | {emd_gt:.4f}              |")

# ─── Markdown table: per-district, per-model ───
print("\n--- Markdown Table (Full breakdown) ---")
print("| District | Model | EMD vs FB | EMD vs GT |")
print("|----------|-------|-----------|-----------|")
for _, row in res_df.iterrows():
    print(f"| {row['District']:10s} | {row['Model']:13s} | {row['EMD_vs_FB']:.4f}    | {row['EMD_vs_GT']:.4f}    |")
