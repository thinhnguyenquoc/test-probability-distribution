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
def shift_power_law(r, C, r0, beta): 
    return C * (r + r0)**(-beta)

def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-10, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

def exponential_dist(r, C, lmb):
    return C * np.exp(-r / lmb)

def gamma_dist(r, C, alpha, lmb):
    r_safe = np.clip(r, 1e-10, None)
    return C * (r_safe**(alpha-1)) * np.exp(-r_safe / lmb)

def tlf_dist(r, C, r0, beta, kappa):
    r_safe = np.clip(r, 1e-10, None)
    return C * (r_safe + r0)**(-beta) * np.exp(-r_safe / kappa)

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
mask = (hist > 0) & (bin_centers > 0.1) 
x_data = bin_centers[mask]
y_prob = hist[mask] / total_trips

# BIC calculation
def calc_bic(y_fit, k, n_total, counts_obs):
    y_fit_pmf = y_fit / np.sum(y_fit)
    y_fit_safe = np.clip(y_fit_pmf, 1e-300, 1)
    log_likelihood = np.sum(counts_obs * np.log(y_fit_safe))
    return k * np.log(n_total) - 2 * log_likelihood

def r2_score(y_true, y_pred):
    return 1 - (np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2))

# Fitting loop
models = {
    'SPL': {'func': shift_power_law, 'p0': [y_prob[0], 1, 2], 'bounds': ([0, 1e-3, 0.1], [np.inf, 50, 10]), 'k': 3, 'color': '#1f77b4'},
    'Lognormal': {'func': lognormal_dist, 'p0': [y_prob[0], np.log(np.mean(x_data)), 1], 'bounds': ([0, -10, 0.1], [np.inf, 10, 5]), 'k': 3, 'color': '#ff7f0e'},
    'Exponential': {'func': exponential_dist, 'p0': [y_prob[0], 5], 'bounds': ([0, 0.1], [np.inf, 100]), 'k': 2, 'color': '#2ca02c'},
    'Gamma': {'func': gamma_dist, 'p0': [y_prob[0], 2, 5], 'bounds': ([0, 0.1, 0.1], [np.inf, 20, 100]), 'k': 3, 'color': '#d62728'},
    'TLF': {'func': tlf_dist, 'p0': [y_prob[0], 1, 2, 10], 'bounds': ([0, 1e-3, 0.1, 1], [np.inf, 50, 10, 500]), 'k': 4, 'color': '#9467bd'}
}

results = {}

for name, m in models.items():
    try:
        popt, _ = curve_fit(m['func'], x_data, y_prob, p0=m['p0'], bounds=m['bounds'], maxfev=20000)
        y_fit = m['func'](x_data, *popt)
        r2 = r2_score(y_prob, y_fit)
        bic = calc_bic(y_fit, m['k'], total_trips, hist[mask])
        results[name] = {'y_fit': y_fit, 'r2': r2, 'bic': bic, 'color': m['color']}
    except Exception as e:
        print(f"Error fitting {name}: {e}")

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Subplot 1: Linear Scale
ax1.bar(x_data, y_prob, width=(bins[1]-bins[0])*0.8, alpha=0.2, color='gray', label='Empirical Data')
for name, res in results.items():
    ax1.plot(x_data, res['y_fit'], color=res['color'], lw=2.5, label=f"{name}")


ax1.set_title(f'Linear Scale (Head Fit): {target_district}', fontsize=15, weight='bold')
ax1.set_xlabel('Distance (km)', fontsize=12)
ax1.set_ylabel('Probability Density', fontsize=12)
ax1.legend(fontsize=10)
ax1.grid(alpha=0.3)

# Subplot 2: Log-Log Scale
ax2.scatter(x_data, y_prob, alpha=0.4, color='black', s=40, label='Empirical Data', edgecolors='none')
for name, res in results.items():
    ax2.plot(x_data, res['y_fit'], color=res['color'], lw=3, label=f"{name} (BIC: {res['bic']/1e3:.1f}k)")

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_title('Log-Log Scale (Tail Fit Diversity)', fontsize=15, weight='bold')
ax2.set_xlabel('Distance (km)', fontsize=12)
ax2.set_ylabel('Probability Density', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(True, which="both", ls="-", alpha=0.2)

# Specific Annotation for the Transition and Tail
ax2.annotate('Heavier Tail Models (SPL, TLF)\nmatch longer distances', 
             xy=(x_data[-2], results['SPL']['y_fit'][-2]), xytext=(x_data[-15], 1e-1),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
             fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.9))

ax2.annotate('Lognormal/Gamma drop fast', 
             xy=(x_data[-8], results['Lognormal']['y_fit'][-8]), xytext=(x_data[-30], 1e-6),
             arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=5),
             fontsize=11, color='darkred', bbox=dict(boxstyle="round", fc="white", alpha=0.9))

plt.suptitle('Multi-model Distribution Analysis at Macro Scale (District Level)', fontsize=18, y=1.02, weight='bold')
plt.tight_layout()
plt.savefig('bic_logic_illustration.png', dpi=300, bbox_inches='tight')
plt.close()
print("Success: Multi-model image generated.")
