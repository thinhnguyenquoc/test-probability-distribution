import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings

def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

warnings.filterwarnings('ignore')

# 1. Tải dữ liệu
gdf = gpd.read_file('sub_zone/data_sgp_subzone.shp')
df = pd.read_csv('data_trip_sum.csv')

# Tính centroid
gdf = gdf.to_crs(epsg=4326)
gdf['centroid'] = gdf.geometry.centroid
gdf['lon'] = gdf.centroid.x
gdf['lat'] = gdf.centroid.y
subzone_dict = gdf.set_index('SUBZONE_C')[['lat', 'lon']].to_dict('index')

# Hàm tính khoảng cách
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

distances = []
counts = []

for _, row in df.iterrows():
    orig = row['ORIGIN_SUBZONE']
    dest = row['DESTINATION_SUBZONE']
    count = row['COUNT']
    
    if orig in subzone_dict and dest in subzone_dict:
        lat1, lon1 = subzone_dict[orig]['lat'], subzone_dict[orig]['lon']
        lat2, lon2 = subzone_dict[dest]['lat'], subzone_dict[dest]['lon']
        dist = haversine(lat1, lon1, lat2, lon2)
        distances.append(dist)
        counts.append(count)

distances = np.array(distances)
counts = np.array(counts)
total_trips = np.sum(counts)

num_bins = 50
bins = np.linspace(0, np.max(distances), num_bins+1)
hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

mask = hist > 0
x_data = bin_centers[mask]
y_prob = hist[mask] / total_trips

# Các hàm mô hình thử nghiệm
def exp_dist(r, C, lam):
    return C * np.exp(-r / lam)

def shift_power_law(r, C, r0, beta):
    return C * (r + r0)**(-beta)

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

results = {}
plt.figure(figsize=(10, 7))
plt.scatter(x_data, y_prob, color='black', label='Dữ liệu thực tế', alpha=0.6, s=30)

x_fit = np.linspace(min(x_data), max(x_data), 200)
colors = ['red', 'blue', 'green', 'orange']

for (name, (model_func, p0, bounds)), color in zip(models.items(), colors):
    try:
        # Cố gắng tính Log không gian nếu có thể để đo lường độ chính xác phân mảnh đuôi tốt hơn
        popt, _ = curve_fit(model_func, x_data, y_prob, p0=p0, bounds=bounds, maxfev=10000)
        y_fit = model_func(x_data, *popt)
        
        # Calculate R^2 in log space to see how well the tail is approximated
        y_fit_safe = np.clip(y_fit, 1e-12, None)
        valid = y_prob > 0
        r2_log = r2_score(np.log(y_prob[valid]), np.log(y_fit_safe[valid]))
        r2_linear = r2_score(y_prob, y_fit)
        
        results[name] = {'r2_log': r2_log, 'r2_linear': r2_linear, 'popt': popt}
        
        y_fit_plot = model_func(x_fit, *popt)
        plt.plot(x_fit, y_fit_plot, color=color, label=f'{name} ($R^2_L$={r2_log:.2f})')
        print(f"Khớp {name} thành công. R2 log: {r2_log:.3f}, R2 Tuyến tính: {r2_linear:.3f}")
    except Exception as e:
        print(f"Không thể khớp {name}: {e}")

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Khoảng cách $\\Delta r$ (km)')
plt.ylabel('Xác suất $P(\\Delta r)$')
plt.title('So sánh các Mô hình Phân phối')
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)

output_plot = 'model_comparison.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"\nBiểu đồ đã được lưu tại {output_plot}")

with open('ket_qua_so_sanh.md', 'w', encoding='utf-8') as f:
    f.write("# So sánh các mô hình phân phối cho lượng di chuyển\n\n")
    f.write("Dưới đây là một số mô hình có thể mô tả tập dữ liệu chuyến đi, sắp xếp theo mức độ phù hợp trên thang đo logarit (chú trọng phần đuôi phân bố):\n\n")
    
    for name, res in sorted(results.items(), key=lambda x: x[1]['r2_log'], reverse=True):
        f.write(f"### {name} \n")
        f.write(f"- Độ chính xác $R^2$ (tính trên log space): **{res['r2_log']:.4f}**\n")
        f.write(f"- Độ chính xác $R^2$ (tuyến tính thông thường): **{res['r2_linear']:.4f}**\n")
        
        # Định dạng in tham số dễ nhìn
        params_str = ", ".join([f"{p:.4f}" for p in res['popt']])
        f.write(f"- Các tham số tối ưu: `[{params_str}]`\n\n")
