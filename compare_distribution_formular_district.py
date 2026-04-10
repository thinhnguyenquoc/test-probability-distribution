import pandas as pd
import numpy as np
from scipy.optimize import minimize
import scipy.stats as stats
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

print("Đồng bộ bộ dữ liệu Chuyến đi, Khoảng cách và Quận (District)...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
dz = pd.read_csv('district_zone.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

# Ánh xạ subzone thành district
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district_id'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district_id'])

def r2_score_custom(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

def exp_dist(r, C, lam): return C * np.exp(-r / lam)
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def tlf_model(r, C, r0, beta, kappa): return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))
def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

models = {
    'Exponential': (exp_dist, [1, 5], 2, ([0, 1e-3], [np.inf, np.inf])),
    'Lognormal': (lognormal_dist, [1, 1, 1], 3, ([0, -np.inf, 1e-3], [np.inf, np.inf, np.inf])),
    'Gamma': (gamma_dist, [1, 2, 2], 3, ([0, 1e-3, 1e-3], [np.inf, 20, np.inf])),
    'Shifted Power-Law': (shift_power_law, [1, 1, 2], 3, ([0, 1e-3, 1e-3], [np.inf, np.inf, 15])),
    'Truncated Lévy Flight': (tlf_model, [1, 1, 2, 50], 4, ([0, 1e-3, 1e-3, 1e-3], [np.inf, np.inf, 15, np.inf]))
}

results = []
districts_list = df['district_id'].unique()
print(f"Bắt đầu quy trình fitting và trích xuất chỉ số (AIC, BIC, KS) cho {len(districts_list)} districts...")

for district, group in df.groupby('district_id'):
    total_trips = group['COUNT'].sum()
    if total_trips < 100 or len(group) < 5:
        continue
    
    distances = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    # Số bin lớn hơn do tập dữ liệu cấp District thường dồn cục khổng lồ
    num_bins = min(50, len(np.unique(distances)))
    if num_bins < 3:
        continue
        
    bins = np.linspace(0, np.max(distances), num_bins+1)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    mask = hist > 0
    if mask.sum() < 4:
        continue
        
    x_data = bin_centers[mask]
    y_counts = hist[mask]
    y_prob = y_counts / total_trips
    
    empirical_cdf = np.cumsum(y_prob)
    district_res = {}
    
    for name, (func, p0, k, bounds) in models.items():
        try:
            def nll(params):
                y_raw = func(x_data, *params)
                if np.sum(y_raw) <= 0 or np.any(y_raw < 0): return 1e18
                y_pmf = y_raw / np.sum(y_raw)
                return -np.sum(y_counts * np.log(np.clip(y_pmf, 1e-300, 1)))

            bnds = list(zip(bounds[0], bounds[1]))
            res = minimize(nll, p0, method='L-BFGS-B', bounds=bnds)
            if not res.success: res = minimize(nll, p0, method='Nelder-Mead', bounds=bnds)
            
            popt = res.x
            y_fit_raw = func(x_data, *popt)
            y_fit_pmf = y_fit_raw / np.sum(y_fit_raw)
            
            r2 = r2_score_custom(y_prob, y_fit_raw)
            model_cdf = np.cumsum(y_fit_pmf)
            ks_stat = np.max(np.abs(empirical_cdf - model_cdf))
            
            log_likelihood = -res.fun
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(total_trips) - 2 * log_likelihood
            
            district_res[name] = {
                'R2': round(r2, 4),
                'KS_Stat': round(ks_stat, 4),
                'Log_Likelihood': round(log_likelihood, 2),
                'AIC': round(aic, 2),
                'BIC': round(bic, 2),
                'k': k
            }
        except:
            pass
            
    if len(district_res) == 0:
        continue
        
    lr_stat = np.nan
    p_value = np.nan
    if 'Shifted Power-Law' in district_res and 'Truncated Lévy Flight' in district_res:
        ll_spl = district_res['Shifted Power-Law']['Log_Likelihood']
        ll_tlf = district_res['Truncated Lévy Flight']['Log_Likelihood']
        lr_stat_val = -2 * (ll_spl - ll_tlf)
        if lr_stat_val > 0:
            p_value = stats.chi2.sf(lr_stat_val, 1)
            lr_stat = round(lr_stat_val, 4)
            p_value = round(p_value, 6)
        else:
            lr_stat = 0
            p_value = 1.0
            
    best_model = min(district_res.keys(), key=lambda m: district_res[m]['BIC'])
    
    for name, metrics in district_res.items():
        results.append({
            'district_id': district,
            'Total_Trips': total_trips,
            'Model': name,
            'k_params': metrics['k'],
            'R2': metrics['R2'],
            'KS_Stat': metrics['KS_Stat'],
            'Log_Likelihood': metrics['Log_Likelihood'],
            'AIC': metrics['AIC'],
            'BIC': metrics['BIC'],
            'LR_Stat_SPL_vs_TLF': lr_stat if name in ['Shifted Power-Law', 'Truncated Lévy Flight'] else np.nan,
            'p_value_LR': p_value if name in ['Shifted Power-Law', 'Truncated Lévy Flight'] else np.nan,
            'Is_Best_BIC': (name == best_model)
        })

res_df = pd.DataFrame(results)
res_df.to_csv('district_distribution_metrics.csv', index=False)
print(">>> Dữ liệu đã lưu vào tệp 'district_distribution_metrics.csv'.")

# Báo cáo tổng thể
print("\n=== KẾT LUẬN MÔ HÌNH PHỦ HỢP NHẤT TẠI CẤP QUẬN (DỰA TRÊN BIC) ===")
best_df = res_df[res_df['Is_Best_BIC'] == True]
best_counts = best_df['Model'].value_counts()

for model, count in best_counts.items():
    print(f"- {model}: {count} districts")

# ----------- XUẤT ẢNH 1: TỔNG QUAN BIC -----------
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
colors = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'][:len(best_counts)]
bars = plt.bar(best_counts.index, best_counts.values, color=colors, edgecolor='black')
plt.title('Số lượng District mà mỗi Mô hình chiếm Ưu thế (BIC)', pad=15)
plt.ylabel('Số Quận')
plt.yticks(range(0, len(districts_list)+1))

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), va='bottom', ha='center', fontweight='bold')

plt.subplot(1, 2, 2)
plt.pie(best_counts.values, labels=best_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
plt.title('Tỉ trọng bao phủ Dữ liệu Cấp Quận', pad=15)

plt.tight_layout()
plt.savefig('district_distribution_metrics.png', dpi=300)
print(f"\n>>> Đã xuất biểu đồ tổng quan vào 'district_distribution_metrics.png'")


# ----------- XUẤT ẢNH 2: SO SÁNH TRỰC TIẾP SPL & LOGNORMAL -----------
spl = res_df[res_df['Model'] == 'Shifted Power-Law'].set_index('district_id')
lgn = res_df[res_df['Model'] == 'Lognormal'].set_index('district_id')

common_districts = spl.index.intersection(lgn.index)
if len(common_districts) > 0:
    spl = spl.loc[common_districts]
    lgn = lgn.loc[common_districts]

    avg_r2 = [spl['R2'].mean(), lgn['R2'].mean()]
    avg_ks = [spl['KS_Stat'].mean(), lgn['KS_Stat'].mean()]

    ks_wins_spl = np.sum(spl['KS_Stat'] < lgn['KS_Stat'])
    ks_wins_lgn = np.sum(lgn['KS_Stat'] < spl['KS_Stat'])

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    labels = ['Shifted Power-Law', 'Lognormal']
    colors_comp = ['#aec7e8', '#ffbb78']

    axes[0].bar(labels, avg_r2, color=colors_comp, edgecolor='black')
    axes[0].set_title('Trung bình R² trên các Quận', fontsize=14, pad=15)
    axes[0].set_ylabel('Điểm R²')
    for i, v in enumerate(avg_r2):
        axes[0].text(i, v + 0.02, f"{v:.4f}", ha='center', fontweight='bold', fontsize=12)
    axes[0].set_ylim(0, 1.05)

    axes[1].bar(labels, avg_ks, color=colors_comp, edgecolor='black')
    axes[1].set_title('Trung bình KS-Test trên các Quận', fontsize=14, pad=15)
    axes[1].set_ylabel('Khoảng cách hình học KS (Thấp tốt hơn)')
    for i, v in enumerate(avg_ks):
        axes[1].text(i, v + 0.005, f"{v:.4f}", ha='center', fontweight='bold', fontsize=12)

    axes[2].pie([ks_wins_spl, ks_wins_lgn], labels=labels, autopct='%1.1f%%', startangle=140, colors=colors_comp, wedgeprops={'edgecolor': 'black'})
    axes[2].set_title('Tỷ lệ thắng 1-vs-1 (Theo KS-Test)', fontsize=14, pad=15)

    plt.tight_layout()
    plt.savefig('district_distribution_metrics_best.png', dpi=300)
    print(f">>> Đã xuất biểu đồ so sánh chi tiết vào 'district_distribution_metrics_best.png'")
