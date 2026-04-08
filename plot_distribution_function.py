import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

print("Đồng bộ dữ liệu và chuẩn bị lưới tọa độ...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
dz = pd.read_csv('district_zone.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district'])

def shift_power_law(r, C, r0, beta):
    return C * (r + r0)**(-beta)

districts = np.sort(df['district'].unique())

plt.figure(figsize=(16, 10))

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']

for i, d in enumerate(districts):
    ax = plt.subplot(2, 3, i+1)
    group = df[df['district'] == d]
    
    total_trips = group['COUNT'].sum()
    distances = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    num_bins = min(50, len(np.unique(distances)))
    if num_bins < 3:
        continue
        
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask = hist > 0
    x_data = bin_centers[mask]
    y_prob = hist[mask] / total_trips
    
    try:
        popt, _ = curve_fit(shift_power_law, x_data, y_prob, p0=[1, 1, 2], bounds=([0, 1e-3, 1e-3], [np.inf, np.inf, 15]), maxfev=15000)
    except:
        popt = [1, 1, 2]
        
    # Vẽ các điểm (Bins) Empirical
    ax.scatter(x_data, y_prob, color=colors[i], label=f'Dữ liệu thực tế', alpha=0.7, edgecolor='k')
    
    # Vẽ hàm phân phối Model
    x_line = np.linspace(min(x_data), max(x_data), 500)
    y_line = shift_power_law(x_line, *popt)
    ax.plot(x_line, y_line, color='red', linewidth=2.5, label=f'SPL Fit: $\\beta={popt[2]:.2f}$')
    
    # Format
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_title(f"Quận (District): {d}", pad=10, fontsize=12, fontweight='bold')
    ax.set_xlabel("Khoảng cách - r (km)", fontsize=10)
    ax.set_ylabel("Xác suất P(r)", fontsize=10)
    ax.legend(loc='upper right')
    ax.grid(True, which="both", ls="--", alpha=0.5)

plt.suptitle("Đường cong Phân phối Thực nghiệm & Mô hình Shifted Power-Law (Macro-scale Log-Log)", fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('distribution_function.png', dpi=300)
print("\n>>> Đã sinh thành công tập bản đồ phân phối 'distribution_function.png'")
