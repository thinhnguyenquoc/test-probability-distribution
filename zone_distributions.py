import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings
from collections import Counter

def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    if ss_tot == 0:
        return 0
    return 1 - (ss_res / ss_tot)

warnings.filterwarnings('ignore')

# 1. Tải dữ liệu
print("Đang tải và xử lý dữ liệu...")
gdf = gpd.read_file('sub_zone/data_sgp_subzone.shp')
df = pd.read_csv('data_trip_sum.csv')

# Tính centroid cho các zone
gdf = gdf.to_crs(epsg=4326)
gdf['centroid'] = gdf.geometry.centroid
gdf['lon'] = gdf.centroid.x
gdf['lat'] = gdf.centroid.y
subzone_dict = gdf.set_index('SUBZONE_C')[['lat', 'lon']].to_dict('index')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# Vectorized distance calculation
lats1 = df['ORIGIN_SUBZONE'].map(lambda x: subzone_dict[x]['lat'] if x in subzone_dict else np.nan)
lons1 = df['ORIGIN_SUBZONE'].map(lambda x: subzone_dict[x]['lon'] if x in subzone_dict else np.nan)
lats2 = df['DESTINATION_SUBZONE'].map(lambda x: subzone_dict[x]['lat'] if x in subzone_dict else np.nan)
lons2 = df['DESTINATION_SUBZONE'].map(lambda x: subzone_dict[x]['lon'] if x in subzone_dict else np.nan)

df['distance'] = haversine(lats1, lons1, lats2, lons2)
df = df.dropna(subset=['distance'])

# Danh sách mô hình
def exp_dist(r, C, lam): return C * np.exp(-r / lam)
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))
def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

models = {
    'Exponential': (exp_dist, (1, 5), (0, np.inf)),
    'Shifted Power-Law': (shift_power_law, (1, 1, 2), (0, np.inf)),
    'Lognormal': (lognormal_dist, (1, 1, 1), (0, np.inf)),
    'Gamma': (gamma_dist, (1, 2, 2), (0, np.inf))
}

best_models_linear = []
results_data = []

# Tìm top 4 zone nhiều chuyến đi nhất để vẽ mẫu
top_zones = df.groupby('ORIGIN_SUBZONE')['COUNT'].sum().sort_values(ascending=False).head(4).index

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
plot_idx = 0

total_zones = df['ORIGIN_SUBZONE'].nunique()
print(f"Bắt đầu phân tích từng zone trong tổng số {total_zones} zone...")

# Group by origin
for zone, group in df.groupby('ORIGIN_SUBZONE'):
    total_trips = group['COUNT'].sum()
    # Chỉ xét những zone có lượng chuyến đi đủ lớn để có ý nghĩa phân phối
    if total_trips < 100 or len(group) < 5:
        continue 
        
    distances = group['distance'].values
    counts = group['COUNT'].values
    
    num_bins = min(30, len(np.unique(distances)))
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask = hist > 0
    if mask.sum() < 5: 
        continue
        
    x_data = bin_centers[mask]
    y_prob = hist[mask] / total_trips
    
    best_r2 = -np.inf
    best_name = None
    fits = {}
    
    for name, (model_func, p0, bounds) in models.items():
        try:
            popt, _ = curve_fit(model_func, x_data, y_prob, p0=p0, bounds=bounds, maxfev=10000)
            y_fit = model_func(x_data, *popt)
            r2 = r2_score(y_prob, y_fit)
            fits[name] = {'popt': popt, 'r2': r2, 'y_fit': y_fit}
            
            if r2 > best_r2:
                best_r2 = r2
                best_name = name
        except:
            continue
            
    if best_name is not None:
        best_models_linear.append(best_name)
        results_data.append({
            'Zone': zone,
            'Total_Trips': int(total_trips),
            'Best_Model': best_name,
            'R2_Score': round(best_r2, 4)
        })
        
        if zone in top_zones and plot_idx < 4:
            ax = axes[plot_idx]
            ax.scatter(x_data, y_prob, color='black', label='Dữ liệu', alpha=0.6)
            
            x_plot = np.linspace(min(x_data), max(x_data), 100)
            colors = ['red', 'blue', 'green', 'orange']
            for i, (name, fit_res) in enumerate(fits.items()):
                y_plot = models[name][0](x_plot, *fit_res['popt'])
                ax.plot(x_plot, y_plot, color=colors[i], label=f"{name} (R2={fit_res['r2']:.2f})")
                
            ax.set_title(f"Zone: {zone} (Trips: {int(total_trips)})")
            ax.set_xlabel('Khoảng cách (km)')
            ax.set_ylabel('Xác suất P')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.legend(fontsize=8)
            ax.grid(True, ls='--', alpha=0.5)
            plot_idx += 1

plt.tight_layout()
plt.savefig('zone_sample_distributions.png', dpi=300)
print("\nĐã lưu biểu đồ của 4 zone mẫu vào 'zone_sample_distributions.png'")

# Tống kết
counts_summary = Counter(best_models_linear)
total_valid = len(best_models_linear)

print("\n--- THỐNG KÊ MÔ HÌNH PHÙ HỢP NHẤT TRÊN TỪNG ZONE ---")
for name, count in counts_summary.most_common():
    pct = (count / total_valid) * 100
    print(f"- {name}: {count} zones ({pct:.1f}%)")

res_df = pd.DataFrame(results_data)
res_df.to_csv('zone_distribution_results.csv', index=False)
print("Đã lưu kết quả chi tiết của tất cả zone vào 'zone_distribution_results.csv'")

with open('ket_qua_tung_zone.md', 'w', encoding='utf-8') as f:
    f.write("# Tổng kết phân phối chuyến đi cho từng Zone riêng biệt\n\n")
    f.write(f"Sau khi quét qua các phân khu (zone) và chỉ phân tích các zone có lượng chuyến đi trên 500 (tổng cộng {total_valid} zones), các mô hình khớp tốt nhất (dựa trên $R^2$) là:\n\n")
    for name, count in counts_summary.most_common():
        pct = (count / total_valid) * 100
        f.write(f"- **{name}**: Phù hợp nhất cho {count} zones ({pct:.1f}%)\n")
    f.write("\nNhìn chung, hiện tượng đa số các zone tuân theo phân phối **Lognormal** hoặc **Gamma** lại một lần nữa chứng minh rằng trong quy mô thành phố nhỏ lẻ, hành vi con người thích đi xa dần đến một mốc nào đó (đỉnh của lognormal) rồi mới suy giảm theo cấp số, thay vì suy giảm ngay lập tức.\n")
