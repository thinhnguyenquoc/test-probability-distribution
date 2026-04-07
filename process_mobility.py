import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings

warnings.filterwarnings('ignore')

# 1. Tải dữ liệu
gdf = gpd.read_file('sub_zone/data_sgp_subzone.shp')
df = pd.read_csv('data_trip_sum.csv')

# Tính centroid (chuyển sang EPSG 4326 để lấy lat/lon)
gdf = gdf.to_crs(epsg=4326)
gdf['centroid'] = gdf.geometry.centroid
gdf['lon'] = gdf.centroid.x
gdf['lat'] = gdf.centroid.y
subzone_dict = gdf.set_index('SUBZONE_C')[['lat', 'lon']].to_dict('index')

# Hàm tính khoảng cách bằng Haversine (km)
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

# Bin dữ liệu khoảng cách làm 50 khoảng
num_bins = 50
bins = np.linspace(0, np.max(distances), num_bins+1)
hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

# Lọc các bin có count > 0
mask = hist > 0
x_data = bin_centers[mask]
y_counts = hist[mask]

# Xác suất P(Delta r) = Count / Total trips
y_prob = y_counts / total_trips

# Hàm Truncated Levy Flight (có thêm biến C để chuẩn hóa vì hàm mật độ cần hệ số)
def truncated_levy_flight(r, C, r0, beta, kappa):
    return C * (r + r0)**(-beta) * np.exp(-r / kappa)

# Khớp mô hình
try:
    popt, pcov = curve_fit(truncated_levy_flight, x_data, y_prob, p0=(1, 1, 1, 10), maxfev=10000)
    C_fit, r0_fit, beta_fit, kappa_fit = popt
    fit_success = True
    print(f"Khớp mô hình thành công!")
    print(f"Các tham số: C={C_fit:.4e}, r0={r0_fit:.4f}, beta={beta_fit:.4f}, kappa={kappa_fit:.4f}")
except Exception as e:
    print(f"Lỗi khi khớp mô hình: {e}")
    fit_success = False

plt.figure(figsize=(8, 6))
plt.scatter(x_data, y_prob, color='blue', label='Dữ liệu thực tế', alpha=0.6)

if fit_success:
    x_fit = np.linspace(min(x_data), max(x_data), 200)
    y_fit = truncated_levy_flight(x_fit, *popt)
    plt.plot(x_fit, y_fit, color='red', label=f'Mô hình khớp: $\\beta={beta_fit:.2f}, \\kappa={kappa_fit:.2f}$')

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Khoảng cách $\\Delta r$ (km)')
plt.ylabel('Xác suất $P(\\Delta r)$')
plt.title('Phân phối khoảng cách di chuyển (Truncated Lévy Flight)')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend()

output_plot = 'log_log_distribution.png'
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"Đã lưu đồ thị vào {output_plot}")

# Viết một file md ngắn để lưu lại kết quả
with open('ket_qua_TLF.md', 'w', encoding='utf-8') as f:
    f.write("# Kết quả phân tích Truncated Lévy Flight\n\n")
    if fit_success:
        f.write("Dữ liệu phân phối khoảng cách có thể khớp với phương trình Truncated Lévy Flight.\n")
        f.write(f"- Hệ số tỷ lệ **C** = {C_fit:.4e}\n")
        f.write(f"- Khoảng cách bù **Δr_0** = {r0_fit:.4f} km\n")
        f.write(f"- Số mũ đặc trưng **β** = {beta_fit:.4f}\n")
        f.write(f"- Điểm cắt giới hạn **κ** = {kappa_fit:.4f} km\n\n")
        f.write("Điều này cho thấy di chuyển của quần thể ở Singapore tuân theo dạng Lévy flight bị cắt cụt do tác động của giới hạn không gian hoặc địa lý tự nhiên.")
    else:
        f.write("Không thể khớp mô hình Truncated Lévy Flight lên dữ liệu này.\n")
