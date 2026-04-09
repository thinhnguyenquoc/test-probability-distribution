"""
Table 5: Cumulative Distance Window Analysis
Tính R² của Lognormal vs SPL trên các cửa sổ khoảng cách tích lũy [0-d]
để phát hiện ngưỡng chuyển pha d*

Input:  data_trip_sum.csv, zone_euclid_distances.csv
Output: table5_threshold_analysis.csv, threshold_transition.png
"""

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─── Load & merge data ───
print("Loading data...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist  = pd.read_csv('zone_euclid_distances.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
df = df[df['euclidean_distance_km'] > 0]

print(f"Tổng cặp OD: {len(df)}, Tổng trips: {df['COUNT'].sum():,.0f}")

# ─── Distribution functions ───
def lognormal_pdf(x, C, mu, sigma):
    x = np.clip(x, 1e-5, None)
    return (C / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2))

def shifted_power_law(x, C, r0, beta):
    return C * (x + r0)**(-beta)

def compute_r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0

# ─── Expand trips to weighted distance array ───
# Dùng histogram có trọng số thay vì expand array (tiết kiệm RAM)
print("Building weighted distance distribution...")

distances = df['euclidean_distance_km'].values
counts    = df['COUNT'].values
total_trips = counts.sum()

# ─── Cumulative window analysis ───
distance_windows = np.arange(0.5, 30.5, 0.5)  # [0.5, 1.0, ..., 30.0]
results = []

print(f"\nTính R² cho {len(distance_windows)} cửa sổ tích lũy [0 – d_max]...")
print("=" * 90)
print(f"{'Window':>12} | {'Bins':>5} | {'Trips':>12} | {'R²(LN)':>10} | {'R²(SPL)':>10} | {'Winner':>6} | {'% Data':>7}")
print("-" * 90)

for d_max in distance_windows:
    # Lọc OD pairs trong cửa sổ [0, d_max]
    mask_window = distances <= d_max
    dist_in     = distances[mask_window]
    cnt_in      = counts[mask_window]
    trips_in    = cnt_in.sum()

    if trips_in < 100 or len(dist_in) < 10:
        continue

    # Histogram có trọng số (weighted)
    num_bins = min(30, max(5, int(d_max / 0.1)))
    bin_edges = np.linspace(0.01, d_max, num_bins + 1)
    hist, _ = np.histogram(dist_in, bins=bin_edges, weights=cnt_in)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Chỉ giữ bins có dữ liệu
    mask = hist > 0
    if mask.sum() < 4:
        continue

    x = bin_centers[mask]
    y = hist[mask].astype(float)
    y = y / y.sum()  # Normalize thành PMF

    # ─── Fit Lognormal ───
    r2_ln = np.nan
    try:
        p0_mu    = np.average(np.log(x), weights=y)
        p0_sigma = max(0.1, np.sqrt(np.average((np.log(x) - p0_mu)**2, weights=y)))
        popt, _ = curve_fit(lognormal_pdf, x, y, p0=[1, p0_mu, p0_sigma],
                            bounds=([0, -5, 0.01], [np.inf, 10, 10]), maxfev=20000)
        y_pred = lognormal_pdf(x, *popt)
        if not np.any(np.isnan(y_pred)):
            r2_ln = compute_r2(y, y_pred)
    except:
        pass

    # ─── Fit SPL ───
    r2_spl = np.nan
    try:
        popt, _ = curve_fit(shifted_power_law, x, y, p0=[0.1, 0.5, 2],
                            bounds=([0.001, 0.001, 0.1], [10, 10, 10]), maxfev=20000)
        y_pred = shifted_power_law(x, *popt)
        if not np.any(np.isnan(y_pred)):
            r2_spl = compute_r2(y, y_pred)
    except:
        pass

    # Winner
    if np.isnan(r2_ln) and np.isnan(r2_spl):
        winner = "N/A"
    elif np.isnan(r2_ln):
        winner = "SPL"
    elif np.isnan(r2_spl):
        winner = "LN"
    else:
        winner = "LN" if r2_ln > r2_spl else "SPL"

    pct_data = trips_in / total_trips * 100

    results.append({
        'Distance_Window_km': f"0 – {d_max:.1f}",
        'd_max': d_max,
        'R2_Lognormal': round(r2_ln, 4) if not np.isnan(r2_ln) else np.nan,
        'R2_SPL': round(r2_spl, 4) if not np.isnan(r2_spl) else np.nan,
        'Winner': winner,
        'Trips_in_Window': int(trips_in),
        'Percent_Data': round(pct_data, 1)
    })

    print(f"  0–{d_max:4.1f} km | {mask.sum():5d} | {trips_in:12,.0f} | {r2_ln:10.4f} | {r2_spl:10.4f} | {winner:>6} | {pct_data:6.1f}%")

# ─── Save CSV ───
df_res = pd.DataFrame(results)
df_res.to_csv('table5_threshold_analysis.csv', index=False)
print(f"\n>>> Saved: table5_threshold_analysis.csv ({len(df_res)} rows)")

# ─── Find crossover ───
print("\n" + "=" * 90)
print("THRESHOLD ANALYSIS:")

valid = df_res.dropna(subset=['R2_Lognormal', 'R2_SPL'])
if len(valid) >= 2:
    r2_diff = valid['R2_Lognormal'].values - valid['R2_SPL'].values
    d_vals  = valid['d_max'].values

    # Tìm điểm sign change (LN > SPL → SPL > LN)
    crossover_found = False
    for i in range(len(r2_diff) - 1):
        if r2_diff[i] > 0 and r2_diff[i+1] <= 0:
            # Linear interpolation
            d_star = d_vals[i] + (0 - r2_diff[i]) / (r2_diff[i+1] - r2_diff[i]) * (d_vals[i+1] - d_vals[i])
            pct_star = np.interp(d_star, d_vals, valid['Percent_Data'].values)
            print(f"  ✓ Ngưỡng chuyển pha d* ≈ {d_star:.2f} km")
            print(f"  ✓ Tại d*, ~{pct_star:.0f}% chuyến đi được bao phủ")
            crossover_found = True
            break

    if not crossover_found:
        # Không có sign change → tìm điểm gần nhau nhất
        min_idx = np.argmin(np.abs(r2_diff))
        print(f"  ⚠ Không tìm thấy giao cắt rõ ràng.")
        print(f"  ⚠ R² gần nhau nhất tại d = {d_vals[min_idx]:.1f} km (diff = {r2_diff[min_idx]:.4f})")

# ─── Plot ───
fig, ax = plt.subplots(figsize=(10, 6))

valid = df_res.dropna(subset=['R2_Lognormal', 'R2_SPL'])
d_plot = valid['d_max'].values
r2_ln_plot  = valid['R2_Lognormal'].values
r2_spl_plot = valid['R2_SPL'].values

ax.plot(d_plot, r2_ln_plot, 'o-', color='#e74c3c', linewidth=2, markersize=8, label='Lognormal')
ax.plot(d_plot, r2_spl_plot, 's--', color='#3498db', linewidth=2, markersize=8, label='Shifted Power-Law')

# Shade regions
ax.fill_between(d_plot, r2_ln_plot, r2_spl_plot,
                where=(r2_ln_plot > r2_spl_plot), alpha=0.15, color='#e74c3c', label='LN dominates')
ax.fill_between(d_plot, r2_ln_plot, r2_spl_plot,
                where=(r2_spl_plot > r2_ln_plot), alpha=0.15, color='#3498db', label='SPL dominates')

ax.set_xlabel('Cumulative Distance Window d_max (km)', fontsize=12)
ax.set_ylabel('$R^2$', fontsize=14)
ax.set_title('Transition Threshold: Lognormal vs SPL across Distance Windows', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 30.5)

plt.tight_layout()
plt.savefig('threshold_transition.png', dpi=300)
print(f"\n>>> Saved: threshold_transition.png")

# ─── Print markdown table ───
print("\n--- Markdown Table ---")
print("| Distance Window | $R^2$ (Lognormal) | $R^2$ (SPL) | Winner | % Data |")
print("|-----------------|-------------------|-------------|--------|--------|")
for _, row in df_res.iterrows():
    ln_v  = f"{row['R2_Lognormal']:.4f}" if not pd.isna(row['R2_Lognormal']) else "N/A"
    spl_v = f"{row['R2_SPL']:.4f}" if not pd.isna(row['R2_SPL']) else "N/A"
    print(f"| {row['Distance_Window_km']:15s} | {ln_v:17s} | {spl_v:11s} | {row['Winner']:6s} | {row['Percent_Data']:5.1f}% |")
