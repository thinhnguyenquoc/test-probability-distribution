import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings

warnings.filterwarnings('ignore')

print("Đồng bộ dữ liệu tính khoảng cách Euclid và ma trận OD...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')

# Áp dụng bảng khoảng cách Euclid chuẩn
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

# Hàm Truncated Lévy Flight với C, r0, beta, kappa
def tlf_model(r, C, r0, beta, kappa):
    # Khử lỗi chia 0 hoặc log âm để bảo vệ phép giải
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)

def r2_score(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

results = []
valid_zones = 0

print(f"Bắt đầu khảo nghiệm mô hình Truncated Lévy Flight (TLF) cho từng zone riêng biệt...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
plot_idx = 0
top_zones = df.groupby('ORIGIN_SUBZONE')['COUNT'].sum().sort_values(ascending=False).head(4).index

for zone, group in df.groupby('ORIGIN_SUBZONE'):
    total_trips = group['COUNT'].sum()
    if total_trips < 500 or len(group) < 10:
        continue
        
    distances = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    # Banning log scale / chia bin
    num_bins = min(30, len(np.unique(distances)))
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask = hist > 0
    if mask.sum() < 5:
        continue
        
    x_data = bin_centers[mask]
    y_prob = hist[mask] / total_trips
    
    try:
        # Cung cấp giới hạn bounds để bảo vệ thuật toán
        # [C, r0, beta, kappa]. Kappa không bao giờ chạm dưới 0.
        lower_bounds = [0, 1e-3, 0, 1e-3]
        upper_bounds = [np.inf, np.inf, 15, np.inf]
        
        popt, _ = curve_fit(tlf_model, x_data, y_prob, 
                            p0=[1, 1, 2, 100], 
                            bounds=(lower_bounds, upper_bounds),
                            maxfev=15000)
        
        y_fit = tlf_model(x_data, *popt)
        r2 = r2_score(y_prob, y_fit)
        
        if np.isnan(r2) or np.isinf(r2):
            continue
            
        C, r0, beta, kappa = popt
        results.append({
            'ORIGIN_SUBZONE': zone,
            'Total_Trips': int(total_trips),
            'R2_Score': round(r2, 4),
            'C': C,
            'Offset_r0': r0,
            'Exponent_beta': beta,
            'Cutoff_kappa': kappa
        })
        valid_zones += 1
        
        # In biểu đồ cho 4 zone tiêu biểu hàng đầu
        if zone in top_zones and plot_idx < 4:
            ax = axes[plot_idx]
            ax.scatter(x_data, y_prob, color='black', label='Dữ liệu phân mảnh', alpha=0.6)
            x_plot = np.linspace(min(x_data), max(x_data), 100)
            y_plot = tlf_model(x_plot, *popt)
            ax.plot(x_plot, y_plot, color='red', lw=2, label=f'TLF Fit\n$R^2$={r2:.2f}\n$\\kappa$={kappa:.0f} km\n$\\beta$={beta:.2f}')
            ax.set_title(f"Phân khu: {zone} (Lượt chuyến: {int(total_trips)})")
            ax.set_xlabel('Khoảng cách phân khu Euclid (km)')
            ax.set_ylabel('Xác suất xuất hiện')
            ax.set_yscale('log')
            ax.set_xscale('log')
            ax.legend(fontsize=9)
            ax.grid(True, ls='--', alpha=0.5)
            plot_idx += 1
            
    except Exception as e:
        pass

plt.tight_layout()
output_image = 'tlf_zone_evaluation.png'
plt.savefig(output_image, dpi=300)

res_df = pd.DataFrame(results)

# Phân loại và đánh giá
# Truncated Levy Flight thường có kappa giới hạn khoảng rải rác một vài trăm kilomet. 
# Nếu vượt quá quá lớn (chẳng hạn 1,000, 10,000, hay tiền thân triệu km), phần cut off \exp(-r/\kappa) 
# bị vô hiệu hóa nên nó rút về phân phối không cắt lũy thừa trượt (Shifted Power-Law).
cutoff_count = len(res_df[res_df['Cutoff_kappa'] < 200])
non_cutoff_count = len(res_df[res_df['Cutoff_kappa'] >= 200])
avg_r2 = res_df['R2_Score'].mean()

print(f"\n--- TÓM TẮT ĐÁNH GIÁ TRUNCATED LÉVY FLIGHT ---")
print(f"Tổng số Zone đủ cấu hình khảo nghiệm: {valid_zones}")
print(f"Độ chính xác tương quan bình quân (Mean R²): {avg_r2:.4f}")
print(f"✓ Số lượng Zone hội tụ đủ đặc tính phân rã mũ kép của TLF (kappa < 200km): {cutoff_count}")
print(f"X Số lượng Zone rơi vào dải không bộc lộ điểm cắt (kappa >= 200km): {non_cutoff_count}")
print(f"Điểm cắt kappa trung vị (Median): {res_df['Cutoff_kappa'].median():.2f} km")

res_df.to_csv('tlf_analysis_per_zone.csv', index=False)
print("\nĐã xuất chi tiết số đo và thông số từng khu vực vào file 'tlf_analysis_per_zone.csv'.")
print(f"Biểu đồ khảo nghiệm chi tiết đã xuất ra file đồ họa '{output_image}'.")
