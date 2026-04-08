import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# Load data
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
dz = pd.read_csv('district_zone.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district_id'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district_id'])

# Define models
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

# Find a district with many data points
district_counts = df['district_id'].value_counts()
target_district = district_counts.index[0]
print(f"Plotting for district: {target_district}")

group = df[df['district_id'] == target_district]
total_trips = group['COUNT'].sum()
distances = group['euclidean_distance_km'].values
counts = group['COUNT'].values

# Increase bin count for better tail visualization
num_bins = 60
bins = np.linspace(0, np.max(distances), num_bins+1)
hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
mask = (hist > 0) & (bin_centers > 0.1) # Avoid zero or near-zero distance for log
x_data = bin_centers[mask]
y_prob = hist[mask] / total_trips

# Robust curve fitting
try:
    # Use log-space fitting sometimes helps but here we stick to linear with higher maxfev
    popt_spl, _ = curve_fit(shift_power_law, x_data, y_prob, p0=[y_prob[0], 1, 2], 
                            bounds=([0, 1e-3, 0.1], [np.inf, 50, 10]), maxfev=20000)
    
    popt_log, _ = curve_fit(lognormal_dist, x_data, y_prob, p0=[y_prob[0], np.log(np.mean(x_data)), 1], 
                            bounds=([0, -10, 0.1], [np.inf, 10, 5]), maxfev=20000)

    y_fit_spl = shift_power_law(x_data, *popt_spl)
    y_fit_log = lognormal_dist(x_data, *popt_log)

    # BIC calculation
    def calc_bic(y_fit, k, n_total, counts_obs):
        y_fit_pmf = y_fit / np.sum(y_fit)
        y_fit_safe = np.clip(y_fit_pmf, 1e-300, 1)
        log_likelihood = np.sum(counts_obs * np.log(y_fit_safe))
        return k * np.log(n_total) - 2 * log_likelihood

    bic_spl = calc_bic(y_fit_spl, 3, total_trips, hist[mask])
    bic_log = calc_bic(y_fit_log, 3, total_trips, hist[mask])

    def r2_score(y_true, y_pred):
        return 1 - (np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2))

    r2_spl = r2_score(y_prob, y_fit_spl)
    r2_log = r2_score(y_prob, y_fit_log)

    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Subplot 1: Linear Scale
    ax1.bar(x_data, y_prob, width=(bins[1]-bins[0])*0.8, alpha=0.3, color='gray', label='Empirical Data')
    ax1.plot(x_data, y_fit_log, color='#ff7f0e', lw=3, label=f'Lognormal (R²={r2_log:.4f})')
    ax1.plot(x_data, y_fit_spl, color='#1f77b4', lw=3, label=f'SPL (R²={r2_spl:.4f})')
    ax1.set_title(f'Linear Scale: {target_district}', fontsize=14)
    ax1.set_xlabel('Distance (km)')
    ax1.set_ylabel('Probability Density')
    ax1.legend()

    # Subplot 2: Log-Log Scale
    ax2.scatter(x_data, y_prob, alpha=0.5, color='gray', s=30, label='Empirical Data')
    ax2.plot(x_data, y_fit_log, color='#ff7f0e', lw=3, label=f'Lognormal (BIC: {bic_log/1e3:.1f}k)')
    ax2.plot(x_data, y_fit_spl, color='#1f77b4', lw=3, label=f'SPL (BIC: {bic_spl/1e3:.1f}k)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title('Log-Log Scale: Tail Fit Accuracy', fontsize=14)
    ax2.set_xlabel('Distance (km)')
    ax2.set_ylabel('Probability Density')
    ax2.legend()
    
    # Highlight the divergence
    ax2.annotate('Lognormal drops exponentially\ndeviating from the long-tail data', 
                 xy=(x_data[-5], y_fit_log[-5]), xytext=(x_data[-20], y_fit_log[-5]*1e-2),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                 fontsize=10, bbox=dict(boxstyle="round", fc="white", alpha=0.8))

    plt.suptitle('The "R² vs BIC" Paradox: Why Lognormal fails at Macro Scale', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('bic_logic_illustration.png', dpi=300, bbox_inches='tight')
    print("Success: Image generated.")

except Exception as e:
    print(f"Error: {e}")
