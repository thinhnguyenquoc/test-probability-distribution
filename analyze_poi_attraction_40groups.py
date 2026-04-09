import pandas as pd
import geopandas as gpd
import numpy as np
from scipy.optimize import curve_fit
import warnings

warnings.filterwarnings('ignore')

# 1. Load data
print("Loading data...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
gdf_pois = gpd.read_file('detail_pois.geojson')
df_groups = pd.read_csv('singapore_40_regions.csv') # mapping subzone -> group_id

# 2. Pre-process POIs
poi_cols = ['amenity', 'leisure', 'office', 'public_transport', 'shop', 'tourism']
gdf_pois['total_poi'] = gdf_pois[poi_cols].sum(axis=1)
poi_map = dict(zip(gdf_pois['SUBZONE_C'], gdf_pois['total_poi']))

# 3. Map Zones to Groups
group_map = dict(zip(df_groups['zone_id'], df_groups['group_id']))

# 4. Merge
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
df['dest_poi'] = df['DESTINATION_SUBZONE'].map(poi_map)
df['origin_group'] = df['ORIGIN_SUBZONE'].map(group_map)
df = df.dropna(subset=['dest_poi', 'origin_group'])

# 5. Functions
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

def shift_power_law(r, C, r0, alpha):
    return C * (r + r0)**(-alpha)

def exp_dist(r, C, lam):
    return C * np.exp(-r / lam)

def get_r2(y_true, y_pred):
    return 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2)

def calculate_bic(y_true, y_pred, k, n_total):
    y_pred_norm = y_pred / np.sum(y_pred)
    ll = np.sum((y_true * n_total) * np.log(np.clip(y_pred_norm, 1e-300, 1)))
    return k * np.log(n_total) - 2 * ll

# 6. Analyze per Group
groups = df['origin_group'].unique()
results = []
num_bins = 50
bins = np.logspace(np.log10(0.5), np.log10(50), num_bins + 1)

for dist in groups:
    sub_df = df[df['origin_group'] == dist]
    if len(sub_df) < 50: continue
    
    distances = sub_df['euclidean_distance_km'].values
    counts = sub_df['COUNT'].values
    pois = sub_df['dest_poi'].values
    
    hist_trips, _ = np.histogram(distances, bins=bins, weights=counts)
    hist_pois, _ = np.histogram(distances, bins=bins, weights=pois)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    mask = (hist_trips > 0) & (hist_pois > 0)
    if mask.sum() < 6: continue
    
    x = bin_centers[mask]
    P_d = hist_trips[mask] / hist_trips.sum()
    A_d = hist_pois[mask]
    y_eff = P_d / A_d
    y_eff /= y_eff.sum()
    
    try:
        popt_log, _ = curve_fit(lognormal_dist, x, y_eff, p0=[1, np.mean(np.log(x)), np.std(np.log(x))], maxfev=40000)
        popt_spl, _ = curve_fit(shift_power_law, x, y_eff, p0=[1, 0.5, 2], bounds=([0, 1e-4, 0.1], [np.inf, 10, 10]), maxfev=40000)
        popt_exp, _ = curve_fit(exp_dist, x, y_eff, p0=[1, 5], maxfev=40000)
        
        r2_log = get_r2(y_eff, lognormal_dist(x, *popt_log))
        r2_spl = get_r2(y_eff, shift_power_law(x, *popt_spl))
        r2_exp = get_r2(y_eff, exp_dist(x, *popt_exp))
        
        N_trips = sub_df['COUNT'].sum()
        bic_log = calculate_bic(y_eff, lognormal_dist(x, *popt_log), 3, N_trips)
        bic_spl = calculate_bic(y_eff, shift_power_law(x, *popt_spl), 3, N_trips)
        bic_exp = calculate_bic(y_eff, exp_dist(x, *popt_exp), 2, N_trips)

        results.append({
            'group_id': dist,
            'r2_log': r2_log, 'r2_spl': r2_spl, 'r2_exp': r2_exp,
            'bic_log': bic_log, 'bic_spl': bic_spl, 'bic_exp': bic_exp
        })
    except: continue

res_df = pd.DataFrame(results)
print(f"40 Groups Mean Results:")
print(f"LN: R2={res_df.r2_log.mean():.4f}, BIC={res_df.bic_log.mean():.1f}")
print(f"SPL: R2={res_df.r2_spl.mean():.4f}, BIC={res_df.bic_spl.mean():.1f}")
print(f"Exp: R2={res_df.r2_exp.mean():.4f}, BIC={res_df.bic_exp.mean():.1f}")

res_df.to_csv('group_40_poi_results.csv', index=False)
