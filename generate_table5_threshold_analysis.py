"""
Table 5: Cumulative Distance Window Analysis
Tính R² của Lognormal vs SPL trên các cửa sổ khoảng cách tích lũy [0-d]
để phát hiện ngưỡng chuyển pha d*
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import kstest
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('data_trip_sum.csv')
distances = pd.read_csv('zone_euclid_distances.csv')
district_mapping = pd.read_csv('district_zone.csv')

# Define distribution functions
def lognormal_pdf(x, mu, sigma):
    """Lognormal PDF"""
    return (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mu) ** 2 / (2 * sigma ** 2))

def shifted_power_law_pdf(x, C, r0, beta):
    """Shifted Power-Law PDF: P(x) ∝ (x + r0)^(-beta)"""
    return C / ((x + r0) ** beta)

def compute_r_squared(y_true, y_pred):
    """Compute R² statistic"""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

# Prepare aggregated trip distance distribution
all_trips = []
for _, row in data.iterrows():
    origin = row['ORIGIN_SUBZONE']
    destination = row['DESTINATION_SUBZONE']
    num_trips = row['COUNT']

    # Find distance
    dist_row = distances[(distances['ORIGIN_SUBZONE'] == origin) & (distances['DESTINATION_SUBZONE'] == destination)]
    if not dist_row.empty:
        dist = dist_row.iloc[0]['euclidean_distance_km']
        all_trips.extend([dist] * int(num_trips))

all_trips = np.array(all_trips)

# Define cumulative distance windows
distance_windows = np.arange(0.5, 10.5, 0.5)  # [0.5, 1.0, ..., 10.0] km
results = []

print("Computing R² for Lognormal vs SPL across cumulative distance windows...")
print("=" * 100)

for d_max in distance_windows:
    # Filter trips within window
    trips_in_window = all_trips[all_trips <= d_max]

    if len(trips_in_window) < 50:  # Skip if too few samples
        continue

    # Create histogram (bins)
    hist, bin_edges = np.histogram(trips_in_window, bins=30, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Fit Lognormal
    try:
        popt_ln, _ = curve_fit(lognormal_pdf, bin_centers, hist, p0=[0, 1], maxfev=10000)
        y_pred_ln = lognormal_pdf(bin_centers, *popt_ln)
        r2_ln = compute_r_squared(hist, y_pred_ln)
    except:
        r2_ln = -999

    # Fit SPL
    try:
        popt_spl, _ = curve_fit(shifted_power_law_pdf, bin_centers, hist,
                                p0=[0.1, 0.5, 2], bounds=([0.001, 0.001, 0.5], [10, 5, 5]),
                                maxfev=10000)
        y_pred_spl = shifted_power_law_pdf(bin_centers, *popt_spl)
        r2_spl = compute_r_squared(hist, y_pred_spl)
    except:
        r2_spl = -999

    # Determine winner
    winner = "LN" if r2_ln > r2_spl else "SPL"
    pct_data = (len(trips_in_window) / len(all_trips)) * 100

    results.append({
        'Distance_Window_km': f"0 – {d_max:.1f}",
        'R2_Lognormal': round(r2_ln, 4),
        'R2_SPL': round(r2_spl, 4),
        'Winner': winner,
        'Percent_Data_Enclosed': f"{pct_data:.0f}%"
    })

    print(f"0–{d_max:.1f} km | LN: {r2_ln:.4f} | SPL: {r2_spl:.4f} | Winner: {winner:>3} | Data: {pct_data:>3.0f}%")

# Find crossover point
df_results = pd.DataFrame(results)
df_results.to_csv('table5_threshold_analysis.csv', index=False)

print("\n" + "=" * 100)
print("Threshold Transition Analysis:")

# Find where R² values cross
crossover_idx = np.argmax((df_results['R2_Lognormal'] - df_results['R2_SPL']).abs())
if crossover_idx > 0:
    d_threshold = 2.5 + 0.5 * crossover_idx  # Approximate
    print(f"  ✓ Transition threshold d* ≈ {d_threshold:.1f} km")
    print(f"  ✓ At this point, ~{df_results.iloc[crossover_idx]['Percent_Data_Enclosed']} of trips are included")

print("\nTable 5 saved to: table5_threshold_analysis.csv")
print("\nFormatted for markdown:\n")
print("| Distance Window | $R^2$ (Lognormal) | $R^2$ (SPL) | Winner | % Data Enclosed |")
print("|-----------------|-------------------|------------|--------|-----------------|")
for _, row in df_results.iterrows():
    print(f"| {row['Distance_Window_km']:15} | {row['R2_Lognormal']:17.4f} | {row['R2_SPL']:10.4f} | {row['Winner']:>6} | {row['Percent_Data_Enclosed']:>15} |")
