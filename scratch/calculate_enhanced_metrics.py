import pandas as pd
import numpy as np

# Đọc dữ liệu
df = pd.read_csv('zone_distribution_metrics.csv')

def calculate_weights(group):
    # Tính Delta BIC
    min_bic = group['BIC'].min()
    group['delta_bic'] = group['BIC'] - min_bic
    # Tính weights
    weights = np.exp(-0.5 * group['delta_bic'])
    group['bic_weight'] = weights / weights.sum()
    # Tính Rank (hạng 1 là tốt nhất)
    group['BIC_Rank'] = group['BIC'].rank(ascending=True)
    return group

# Áp dụng cho từng subzone
df_weighted = df.groupby('ORIGIN_SUBZONE').apply(calculate_weights)

# Tính toán kết quả tổng hợp
summary = df_weighted.groupby('Model').agg({
    'bic_weight': 'mean',
    'BIC_Rank': 'mean',
    'R2': 'mean',
    'KS_Stat': 'mean'
}).sort_values('bic_weight', ascending=False)

summary['BIC_Best_Pct'] = df[df['Is_Best_BIC'] == True]['Model'].value_counts(normalize=True) * 100

print("\n--- Model Comparison Summary (Enhanced Metrics) ---")
print(summary.to_string())

# Lưu lại kết quả để bạn cập nhật vào Table 1
summary.to_csv('enhanced_table1_metrics.csv')
