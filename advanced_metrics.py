import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.stats as stats
import warnings

warnings.filterwarnings('ignore')

print("Đồng bộ dữ liệu tính khoảng cách Euclid (để tính Metrics Tổng quan)...")
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

distances = df['euclidean_distance_km'].values
counts = df['COUNT'].values

# Tổ chức Bin để đánh giá
num_bins = 50
bins = np.linspace(0, np.max(distances), num_bins+1)
hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

mask = hist > 0
x_data = bin_centers[mask]
y_counts = hist[mask]
total_trips = y_counts.sum()
y_prob = y_counts / total_trips

# Bấm hàm CDF Thực nghiệm (Empirical CDF)
empirical_cdf = np.cumsum(y_prob)

# Các hàm mô hình (Probability Density / Mass Functions)
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
    'Exponential': (exp_dist, [1, 5], 2),
    'Lognormal': (lognormal_dist, [1, 1, 1], 3),
    'Gamma': (gamma_dist, [1, 2, 2], 3),
    'Shifted Power-Law': (shift_power_law, [1, 1, 2], 3),
    'Truncated Levy Flight': (tlf_model, [1, 1, 2, 50], 4)
}

results = []
metrics_md = "# Kết quả Chỉ số Đánh giá Cấu trúc Phân phối Nâng cao\n\n"
metrics_md += "Bộ Metrics chi tiết cho từng loại đường cong dựa trên tổng toàn bộ mạng lưới không gian:\n\n"

for name, (func, p0, k) in models.items():
    try:
        # Bounds constraints definition
        if name == 'Truncated Levy Flight':
            bounds = ([0, 1e-3, 0, 1e-3], [np.inf, np.inf, 15, np.inf])
        else:
            bounds = (0, np.inf)
            
        popt, _ = curve_fit(func, x_data, y_prob, p0=p0, bounds=bounds, maxfev=25000)
        y_fit_raw = func(x_data, *popt)
        
        # Chuẩn hóa về phân phối thực sự (PMF tổng bằng 1 trong khoảng khảo sát)
        # Bắt buộc để tính toán KS Test và Likelihood
        y_fit_pmf = y_fit_raw / np.sum(y_fit_raw)
        
        # 1. Kolmogorov-Smirnov (KS) Statistic
        model_cdf = np.cumsum(y_fit_pmf)
        ks_stat = np.max(np.abs(empirical_cdf - model_cdf))
        
        # 2. Maximum Log-Likelihood (Dựa theo số liệu đếm số chuyến)
        y_fit_safe = np.clip(y_fit_pmf, 1e-300, 1) # Ngừa lỗi log(0)
        log_likelihood = np.sum(y_counts * np.log(y_fit_safe))
        
        # 3. Akaike Information Criterion (AIC)
        aic = 2 * k - 2 * log_likelihood
        
        # 4. Bayesian Information Criterion (BIC)
        bic = k * np.log(total_trips) - 2 * log_likelihood
        
        results.append({
            'Mô hình': name,
            'Số tham số (k)': k,
            'KS Test (D)': round(ks_stat, 4),
            'Log-Likelihood': round(log_likelihood, 2),
            'AIC': round(aic, 2),
            'BIC': round(bic, 2)
        })
        
    except Exception as e:
        print(f"Failed to process {name}: {e}")

res_df = pd.DataFrame(results)
# Sort results based on BIC (lower is better)
res_df = res_df.sort_values(by='BIC')

metrics_md += res_df.to_markdown(index=False)

# Likelihood Ratio Test (So sánh Heavy-tail models: TLF vs Shifted Power-Law)
try:
    logL_spl = res_df.loc[res_df['Mô hình'] == 'Shifted Power-Law', 'Log-Likelihood'].values[0]
    logL_tlf = res_df.loc[res_df['Mô hình'] == 'Truncated Levy Flight', 'Log-Likelihood'].values[0]
    k_spl = int(res_df.loc[res_df['Mô hình'] == 'Shifted Power-Law', 'Số tham số (k)'].values[0])
    k_tlf = int(res_df.loc[res_df['Mô hình'] == 'Truncated Levy Flight', 'Số tham số (k)'].values[0])
    
    # Kểm định sự gần gũi bằng hệ số Likelihood Ratio test
    # LR = -2 * (L0 - L1)
    lr_stat = -2 * (logL_spl - logL_tlf)
    df_diff = k_tlf - k_spl # Độ tự do = 1 do khác biêt thêm biến kappa
    p_value = stats.chi2.sf(lr_stat, df_diff)
    
    metrics_md += "\n\n### Đánh giá Likelihood Ratio cho Heavy-tail models (Lévy Flight vs. Shifted Power Law)\n"
    metrics_md += f"- **Likelihood Ratio (LR)**: {lr_stat:.2f}\n"
    metrics_md += f"- **p-value ($\\chi^2$)**: {p_value:.4e}\n"
    if p_value < 0.05:
        metrics_md += "$\\Rightarrow$ Truncated Lévy Flight mang lại độ vặn thông tin đáng kể cho dữ liệu so với Power-law thông thường (khẳng định việc chia cắt exponential cutoff là cần thiết ở một số phân vùng, dẫu nhỏ).\n"
    else:
        metrics_md += "$\\Rightarrow$ Chênh lệch không quan trọng, Shifted Power-Law vốn có số tham số nhẹ hơn là phương án thiết kiệm và mạnh mẽ ngang ngửa Truncated Lévy Flight.\n"
except Exception as e:
    pass

res_df.to_csv('advanced_metrics_global.csv', index=False)

with open('metrics_chuyen_sau.md', 'w', encoding='utf-8') as f:
    f.write(metrics_md)

print("Đã hoàn tất tính toán métrics phân phối chuyên sâu (KS test, AIC, BIC, Likelihood Ratio).")
print("Kết xuất báo cáo tại 'metrics_chuyen_sau.md'")
