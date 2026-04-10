import pandas as pd
import numpy as np
from scipy.optimize import minimize
import scipy.stats as stats
import warnings

warnings.filterwarnings('ignore')

print("Đồng bộ bộ dữ liệu Chuyến đi và Khoảng cách Euclid...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

def r2_score_custom(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

# Các hàm lý thuyết phân phối
def exp_dist(r, C, lam): return C * np.exp(-r / lam)
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def tlf_model(r, C, r0, beta, kappa): return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))
def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

# Định nghĩa các models cùng số lượng parameters(k) và bounds
models = {
    'Exponential': (exp_dist, [1, 5], 2, ([0, 1e-3], [np.inf, np.inf])),
    'Lognormal': (lognormal_dist, [1, 1, 1], 3, ([0, -np.inf, 1e-3], [np.inf, np.inf, np.inf])),
    'Gamma': (gamma_dist, [1, 2, 2], 3, ([0, 1e-3, 1e-3], [np.inf, 20, np.inf])),
    'Shifted Power-Law': (shift_power_law, [1, 1, 2], 3, ([0, 1e-3, 1e-3], [np.inf, np.inf, 15])),
    'Truncated Lévy Flight': (tlf_model, [1, 1, 2, 50], 4, ([0, 1e-3, 1e-3, 1e-3], [np.inf, np.inf, 15, np.inf]))
}

results = []
valid_zones = 0
total_zones = df['ORIGIN_SUBZONE'].nunique()

print(f"Bắt đầu quy trình fitting và trích xuất chỉ số (AIC, BIC, KS) cho {total_zones} zones...")

for zone, group in df.groupby('ORIGIN_SUBZONE'):
    total_trips = group['COUNT'].sum()
    if total_trips < 100 or len(group) < 5:
        continue
    
    distances = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    num_bins = min(30, len(np.unique(distances)))
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
    zone_res = {}
    
    for name, (func, p0, k, bounds) in models.items():
        try:
            # Objective function for MLE: Negative Log-Likelihood
            def nll(params):
                y_raw = func(x_data, *params)
                # Normalize to get PMF
                if np.sum(y_raw) <= 0 or np.any(y_raw < 0):
                    return 1e18 # High penalty for invalid params
                y_pmf = y_raw / np.sum(y_raw)
                y_safe = np.clip(y_pmf, 1e-300, 1)
                return -np.sum(y_counts * np.log(y_safe))

            # Reshape bounds for minimize (list of tuples)
            bnds = list(zip(bounds[0], bounds[1]))
            
            # Initial run with minimize
            res = minimize(nll, p0, method='L-BFGS-B', bounds=bnds, options={'maxiter': 500, 'ftol': 1e-6})
            
            if not res.success:
                # Retry with Nelder-Mead if L-BFGS-B fails to find a good spot
                res = minimize(nll, p0, method='Nelder-Mead', bounds=bnds)
            
            popt = res.x
            y_fit_pmf_raw = func(x_data, *popt)
            y_fit_pmf = y_fit_pmf_raw / np.sum(y_fit_pmf_raw)
            
            if np.any(np.isnan(popt)) or np.any(np.isinf(popt)):
                continue
                
            r2 = r2_score_custom(y_prob, y_fit_pmf_raw)
            model_cdf = np.cumsum(y_fit_pmf)
            ks_stat = np.max(np.abs(empirical_cdf - model_cdf))
            
            log_likelihood = -res.fun # Negative of NLL is Log-Likelihood
            
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(total_trips) - 2 * log_likelihood
            
            # Anderson-Darling for Choice (Binned approximation)
            # A^2 = N * sum( (CDF_obs - CDF_fit)^2 / (CDF_fit * (1 - CDF_fit)) * dCDF_fit )
            # To avoid division by zero, we clip CDF_fit
            fit_cdf_diff = np.diff(np.insert(model_cdf, 0, 0))
            ad_num = (empirical_cdf - model_cdf)**2
            ad_den = model_cdf * (1 - model_cdf)
            ad_den = np.clip(ad_den, 1e-6, None)
            ad_stat = total_trips * np.sum((ad_num / ad_den) * fit_cdf_diff)

            zone_res[name] = {
                'KS_Stat': round(ks_stat, 4),
                'AD_Stat': round(ad_stat, 4),
                'Log_Likelihood': round(log_likelihood, 2),
                'AIC': round(aic, 2),
                'BIC': round(bic, 2),
                'k': k
            }

        except:
            pass
            
    if len(zone_res) == 0:
        continue
        
    # Likelihood Ratio Test: Shifted Power-Law vs TLF
    lr_stat = np.nan
    p_value = np.nan
    if 'Shifted Power-Law' in zone_res and 'Truncated Lévy Flight' in zone_res:
        ll_spl = zone_res['Shifted Power-Law']['Log_Likelihood']
        ll_tlf = zone_res['Truncated Lévy Flight']['Log_Likelihood']
        lr_stat_val = -2 * (ll_spl - ll_tlf)
        if lr_stat_val > 0:
            p_value = stats.chi2.sf(lr_stat_val, 1)
            lr_stat = round(lr_stat_val, 4)
            p_value = round(p_value, 6)
        else:
            lr_stat = 0
            p_value = 1.0
            
    # Bộ đánh giá chọn ra mô hình tốt nhất theo BIC (Phạt nghiệm khắt khe nhất)
    best_model = min(zone_res.keys(), key=lambda m: zone_res[m]['BIC'])
    
    for name, metrics in zone_res.items():
        results.append({
            'ORIGIN_SUBZONE': zone,
            'Total_Trips': total_trips,
            'Model': name,
            'k_params': metrics['k'],
            'KS_Stat': metrics['KS_Stat'],
            'AD_Stat': metrics['AD_Stat'],
            'Log_Likelihood': metrics['Log_Likelihood'],
            'AIC': metrics['AIC'],
            'BIC': metrics['BIC'],

            'LR_Stat_SPL_vs_TLF': lr_stat if name in ['Shifted Power-Law', 'Truncated Lévy Flight'] else np.nan,
            'p_value_LR': p_value if name in ['Shifted Power-Law', 'Truncated Lévy Flight'] else np.nan,
            'Is_Best_BIC': (name == best_model)
        })
        
    valid_zones += 1
    if valid_zones % 50 == 0:
        print(f"Đã xử lý {valid_zones} zones...")

# Lưu kết quả
res_df = pd.DataFrame(results)
res_df.to_csv('zone_distribution_metrics.csv', index=False)
print(f"\nĐã tính toán thành công cho {valid_zones} zones hợp lệ.")
print(">>> Dữ liệu đã lưu vào tệp 'zone_distribution_metrics.csv'.")

# Báo cáo tổng thể
print("\n=== KẾT LUẬN MÔ HÌNH PHÙ HỢP NHẤT VỚI DỮ LIỆU CÁC ZONE (DỰA TRÊN ĐIỂM BIC) ===")
best_df = res_df[res_df['Is_Best_BIC'] == True]
best_counts = best_df['Model'].value_counts()
total_best = len(best_df)

for model, count in best_counts.items():
    pct = (count / total_best) * 100
    print(f"- {model}: {count} zones ({pct:.1f}%)")

valid_lr = best_df.drop_duplicates(subset=['ORIGIN_SUBZONE']).dropna(subset=['p_value_LR'])
if len(valid_lr) > 0:
    significant_tlf = len(valid_lr[valid_lr['p_value_LR'] < 0.05])
    print(f"\nPhân tích tính phụ thuộc Cutoff phân rã của Không gian (Likelihood Ratio Test):")
    print(f"- Có {significant_tlf} / {len(valid_lr)} zones ({significant_tlf/len(valid_lr)*100:.1f}%) xác nhận độ rơi tự do cutoff của Truncated Lévy Flight có ý nghĩa thống kê (p < 0.05).")
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 6))

# Cột 1: Bar Chart
plt.subplot(1, 2, 1)
colors = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'][:len(best_counts)]
bars = plt.bar(best_counts.index, best_counts.values, color=colors, edgecolor='black')
plt.title('Số lượng Zone mà mỗi Mô hình chiếm Ưu thế (Khắt khe bằng BIC)', pad=15)
plt.ylabel('Số phân khu (Zones)')
plt.xticks(rotation=25)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, int(yval), va='bottom', ha='center', fontweight='bold')

# Cột 2: Pie Chart
plt.subplot(1, 2, 2)
plt.pie(best_counts.values, labels=best_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor': 'black'})
plt.title('Tỉ trọng bao phủ Dữ liệu Phân khu xuất phát', pad=15)

plt.tight_layout()
plt.savefig('zone_distribution_metrics.png', dpi=300)
print(f"\n>>> Đã xuất biểu đồ thống kê phân phối vào 'zone_distribution_metrics.png'")
