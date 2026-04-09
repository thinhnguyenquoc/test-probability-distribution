import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings

warnings.filterwarnings('ignore')

# 1. Load data
print("Loading data...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
gdf_pois = gpd.read_file('detail_pois.geojson')
df_dz = pd.read_csv('district_zone.csv')

# 2. Pre-process POIs
poi_cols = ['amenity', 'leisure', 'office', 'public_transport', 'shop', 'tourism']
gdf_pois['total_poi'] = gdf_pois[poi_cols].sum(axis=1)
poi_map = dict(zip(gdf_pois['SUBZONE_C'], gdf_pois['total_poi']))

# 3. Map Zones to Districts
dist_map = dict(zip(df_dz['zone_id'], df_dz['district_id']))
dist_names = dict(zip(df_dz['district_id'], df_dz['district_name']))

# 4. Merge OD, Distance, POIs, and Districts
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
df['dest_poi'] = df['DESTINATION_SUBZONE'].map(poi_map)
df['origin_district'] = df['ORIGIN_SUBZONE'].map(dist_map)
df = df.dropna(subset=['dest_poi', 'origin_district'])

# 5. Analysis Functions
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

def shift_power_law(r, C, r0, alpha):
    return C * (r + r0)**(-alpha)

def get_r2(y_true, y_pred):
    return 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2)

def exp_dist(r, C, lam):
    return C * np.exp(-r / lam)

# 6. Analyze per District
districts = df['origin_district'].unique()
results = []

# Use log-spaced bins for better tail resolution
num_bins = 50
bins = np.logspace(np.log10(0.5), np.log10(50), num_bins + 1)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, dist in enumerate(districts):
    sub_df = df[df['origin_district'] == dist]
    if len(sub_df) < 100: continue
    
    # Calculate density manually with log bins
    distances = sub_df['euclidean_distance_km'].values
    counts = sub_df['COUNT'].values
    pois = sub_df['dest_poi'].values
    
    hist_trips, _ = np.histogram(distances, bins=bins, weights=counts)
    hist_pois, _ = np.histogram(distances, bins=bins, weights=pois)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    mask = (hist_trips > 0) & (hist_pois > 0)
    if mask.sum() < 6: continue
    
    x = bin_centers[mask]
    y_eff = hist_trips[mask] / hist_pois[mask]
    y_eff /= y_eff.sum() # Normalize
    
    try:
        popt_log, _ = curve_fit(lognormal_dist, x, y_eff, p0=[1, np.mean(np.log(x)), np.std(np.log(x))], maxfev=40000)
        popt_spl, _ = curve_fit(shift_power_law, x, y_eff, p0=[1, 0.5, 2], bounds=([0, 1e-4, 0.1], [np.inf, 10, 10]), maxfev=40000)
        popt_exp, _ = curve_fit(exp_dist, x, y_eff, p0=[1, 5], maxfev=40000)
        
        r2_log = get_r2(y_eff, lognormal_dist(x, *popt_log))
        r2_spl = get_r2(y_eff, shift_power_law(x, *popt_spl))
        r2_exp = get_r2(y_eff, exp_dist(x, *popt_exp))
        
        # Calculate BIC for standardized comparison
        # Treat N as the total trips in the district to give statistical weight
        N_trips = sub_df['COUNT'].sum()
        
        def calculate_bic(y_true, y_pred, k, n_total):
            y_pred_norm = y_pred / np.sum(y_pred)
            ll = np.sum((y_true * n_total) * np.log(np.clip(y_pred_norm, 1e-300, 1)))
            return k * np.log(n_total) - 2 * ll

        bic_log = calculate_bic(y_eff, lognormal_dist(x, *popt_log), 3, N_trips)
        bic_spl = calculate_bic(y_eff, shift_power_law(x, *popt_spl), 3, N_trips)
        bic_exp = calculate_bic(y_eff, exp_dist(x, *popt_exp), 2, N_trips)

        results.append({
            'district_id': dist,
            'district_name': dist_names.get(dist, dist),
            'r2_log': round(r2_log, 4),
            'r2_spl': round(r2_spl, 4),
            'r2_exp': round(r2_exp, 4),
            'bic_log': bic_log,
            'bic_spl': bic_spl,
            'bic_exp': bic_exp
        })
        
        # Plot
        ax = axes[i]
        ax.scatter(x, y_eff, color='black', alpha=0.5, label='Efficiency Phi(d)')
        ax.plot(x, lognormal_dist(x, *popt_log), 'g-', label='LN')
        ax.plot(x, shift_power_law(x, *popt_spl), 'b--', label='SPL')
        ax.plot(x, exp_dist(x, *popt_exp), 'r:', label='Exp')
        ax.set_title(f"{dist_names.get(dist, dist)}")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=8)
        
    except Exception as e:
        print(f"Error fitting for {dist}: {e}")

plt.tight_layout()
plt.savefig('district_poi_analysis.png', dpi=300)
print("Analysis complete. Plot saved to 'district_poi_analysis.png'")

# Output CSV
res_df = pd.DataFrame(results)
res_df.to_csv('district_poi_results.csv', index=False)
print("Results saved to 'district_poi_results.csv'")
