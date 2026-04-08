import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

print("Chuẩn bị dữ liệu và Môi trường Phân tích Rủi ro Bootstrapping...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
dz = pd.read_csv('district_zone.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district'])

def shift_power_law(r, C, r0, beta):
    return C * (r + r0)**(-beta)

N_BOOTSTRAP = 200
results = []
bootstrap_params = [] # Dữ liệu thô để vẽ boxplot
districts = np.sort(df['district'].unique())

print(f"Bắt đầu thuật toán Bootstrapping {N_BOOTSTRAP} vòng cho {len(districts)} Quận (Áp dụng Shifted Power-Law)...")

for d in districts:
    group = df[df['district'] == d]
    total_trips = group['COUNT'].sum()
    distances = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    # Binning nguyên bản làm gốc
    num_bins = min(50, len(np.unique(distances)))
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist_orig, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask_orig = hist_orig > 0
    x_data = bin_centers[mask_orig]
    
    # Tần suất chuẩn làm xác suất lõi cho Multinomial
    p_orig = hist_orig / total_trips
    
    # Mảng lưu trữ parameter của N lần lặp
    params_c = []
    params_r0 = []
    params_beta = []
    
    for _ in range(N_BOOTSTRAP):
        # Tái tạo quần thể ngẫu nhiên có hoàn lại (Resampling with replacement) thông qua Multinomial
        hist_sampled = np.random.multinomial(total_trips, p_orig)
        y_prob_sampled = hist_sampled[mask_orig] / total_trips
        
        try:
            popt, _ = curve_fit(shift_power_law, x_data, y_prob_sampled, p0=[1, 1, 2], bounds=([0, 1e-3, 1e-3], [np.inf, np.inf, 15]), maxfev=15000)
            params_c.append(popt[0])
            params_r0.append(popt[1])
            params_beta.append(popt[2])
            
            bootstrap_params.append({'District': d, 'Parameter': 'beta', 'Value': popt[2]})
        except:
            pass
            
    if len(params_beta) > 0:
        results.append({
            'District': d,
            'C_mean': round(np.mean(params_c), 4),
            'C_ci_low': round(np.percentile(params_c, 2.5), 4),
            'C_ci_high': round(np.percentile(params_c, 97.5), 4),
            
            'r0_mean': round(np.mean(params_r0), 4),
            'r0_ci_low': round(np.percentile(params_r0, 2.5), 4),
            'r0_ci_high': round(np.percentile(params_r0, 97.5), 4),
            
            'beta_mean': round(np.mean(params_beta), 4),
            'beta_ci_low': round(np.percentile(params_beta, 2.5), 4),
            'beta_ci_high': round(np.percentile(params_beta, 97.5), 4),
        })
    print(f"Hoàn thành xuất {N_BOOTSTRAP} phân thân ngẫu nhiên cho Quận {d}")

res_df = pd.DataFrame(results)
res_df.to_csv('spl_parameter_uncertainty.csv', index=False)
print("\n>>> Đã xuất dữ liệu Parameter Confidence Interval 95% vào 'spl_parameter_uncertainty.csv'")

bs_df = pd.DataFrame(bootstrap_params)
plt.figure(figsize=(10, 6))

colors = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']

# Bóc tách list để vẽ trong matplotlib thuần
data_to_plot = []
districts_sorted = np.sort(bs_df['District'].unique())
for d in districts_sorted:
    data_to_plot.append(bs_df[bs_df['District'] == d]['Value'].values)

box = plt.boxplot(data_to_plot, patch_artist=True, labels=districts_sorted)

for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Vẽ Scatter Jitter
for i, d in enumerate(districts_sorted):
    y = data_to_plot[i]
    x = np.random.normal(i + 1, 0.04, size=len(y))
    plt.scatter(x, y, color='black', alpha=0.3, s=8)

plt.title('Độ phân tán Tham số Đuôi dài (Beta - β) qua 200 vòng Bootstrapping ngẫu nhiên', pad=15, fontsize=14, fontweight='bold')
plt.ylabel('Tham số \u03b2 (Trọng lực Kháng cự Không gian)', fontsize=11)
plt.xlabel('Cụm Vĩ mô (Districts)')
plt.grid(axis='y', ls='--', alpha=0.5)

plt.tight_layout()
plt.savefig('spl_parameter_uncertainty.png', dpi=300)
print(">>> Đã xuất biểu đồ Boxplot độ lệch chuẩn vào 'spl_parameter_uncertainty.png'")
