import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 1. Load data
print("Loading data...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
gdf_pois = gpd.read_file('detail_pois.geojson')

# 2. Calculate Total POI Attraction per Subzone
poi_cols = ['amenity', 'leisure', 'office', 'public_transport', 'shop', 'tourism']
gdf_pois['total_poi'] = gdf_pois[poi_cols].sum(axis=1)
poi_map = dict(zip(gdf_pois['SUBZONE_C'], gdf_pois['total_poi']))

# 3. Merge data
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
df['dest_poi'] = df['DESTINATION_SUBZONE'].map(poi_map)
df = df.dropna(subset=['dest_poi'])

# 4. Binning by distance
num_bins = 50
bins = np.linspace(0.1, 50, num_bins + 1)
df['dist_bin'] = pd.cut(df['euclidean_distance_km'], bins=bins)

# Group by bin
bin_stats = df.groupby('dist_bin', observed=False).agg({
    'COUNT': 'sum',
    'dest_poi': 'sum',
    'euclidean_distance_km': 'mean'
}).reset_index()

# Filter out empty bins
bin_stats = bin_stats[bin_stats['COUNT'] > 0]
bin_centers = bin_stats['euclidean_distance_km']
trips = bin_stats['COUNT']
total_attraction = bin_stats['dest_poi']

# Calculate Probabilities and Efficiencies
prob_d = trips / trips.sum()
efficiency_d = trips / total_attraction # T(d) / A(d)
efficiency_d /= efficiency_d.sum() # Normalize for fitting

# 5. Curve Fitting Functions
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

def shift_power_law(r, C, r0, alpha):
    return C * (r + r0)**(-alpha)

# Fit both P(d) and Efficiency Phi(d)
x = bin_centers.values
y_prob = prob_d.values
y_eff = efficiency_d.values

# Lognormal fit on Phi(d)
popt_log_eff, _ = curve_fit(lognormal_dist, x, y_eff, p0=[1, 1, 1], maxfev=10000)
# SPL fit on Phi(d)
popt_spl_eff, _ = curve_fit(shift_power_law, x, y_eff, p0=[1, 1, 1.5], maxfev=10000)

# Calculate metrics for Phi(d)
def get_metrics(y_true, y_pred, k, n):
    res = y_true - y_pred
    rss = np.sum(res**2)
    rmse = np.sqrt(rss / n)
    r2 = 1 - rss / np.sum((y_true - np.mean(y_true))**2)
    
    # Standard KS-stat
    cdf_true = np.cumsum(y_true)
    cdf_pred = np.cumsum(y_pred)
    ks_stat = np.max(np.abs(cdf_true - cdf_pred))
    
    return round(r2, 4), round(ks_stat, 4), round(rmse, 6)

n = len(x)
r2_log_eff, ks_log_eff, rmse_log_eff = get_metrics(y_eff, lognormal_dist(x, *popt_log_eff), 3, n)
r2_spl_eff, ks_spl_eff, rmse_spl_eff = get_metrics(y_eff, shift_power_law(x, *popt_spl_eff), 3, n)

print(f"Lognormal: R2={r2_log_eff}, KS={ks_log_eff}, RMSE={rmse_log_eff}")
print(f"SPL: R2={r2_spl_eff}, KS={ks_spl_eff}, RMSE={rmse_spl_eff}")

# 6. Plotting
plt.figure(figsize=(15, 6))

# Plot 1: Probability vs Efficiency
plt.subplot(1, 2, 1)
plt.scatter(bin_centers, prob_d, label='P(d) - Observed Prob.', alpha=0.6)
plt.scatter(bin_centers, efficiency_d, label='Phi(d) - Efficiency P(d)/A(d)', marker='x', color='red')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Distance (km)')
plt.ylabel('Density / Intensity')
plt.title('Comparison: Observed Prob. vs Mobility Efficiency')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)

# Plot 2: Fitting on Efficiency
plt.subplot(1, 2, 2)
plt.scatter(x, y_eff, color='black', alpha=0.3, label='Efficiency Data')
plt.plot(x, lognormal_dist(x, *popt_log_eff), 'g-', label=f'Lognormal (R2={r2_log_eff:.3f})')
plt.plot(x, shift_power_law(x, *popt_spl_eff), 'b--', label=f'Shifted PL (R2={r2_spl_eff:.3f})')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Distance (km)')
plt.ylabel('Mobility Efficiency Phi(d)')
plt.title('Log-Log Fit of Mobility Efficiency (POI weighted)')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)

plt.tight_layout()
plt.savefig('poi_attraction_analysis.png', dpi=300)
print("Analysis complete. Results saved to 'poi_attraction_analysis.png'")

# Output CSV for paper
res_df = pd.DataFrame({
    'distance_km': bin_centers,
    'observed_prob': prob_d,
    'attraction_A': total_attraction,
    'efficiency_phi': efficiency_d
})
res_df.to_csv('poi_analysis_results.csv', index=False)
