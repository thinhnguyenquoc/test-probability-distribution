"""
analyze_model_dominance_districts.py
--------------------------
Phân tích từng District (5 Districts Scale): mô hình nào khớp tốt nhất theo 4 tiêu chí
(AIC, BIC, KS-stat, Log-Likelihood), sau đó đếm số District mỗi mô hình chiếm ưu thế.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# 1. ĐỌC DỮ LIỆU
# ==============================================================================
df = pd.read_csv('district_distribution_metrics.csv')

total_districts = df['district_id'].nunique()
print(f"Tổng số districts hợp lệ: {total_districts}")
print(f"Tổng số models: {df['Model'].nunique()} — {df['Model'].unique().tolist()}")

# ==============================================================================
# 2. XÁC ĐỊNH MÔ HÌNH TỐT NHẤT PER DISTRICT THEO 5 TIÊU CHÍ
# ==============================================================================

def best_model_by_metric(group, col, higher_is_better=False):
    """Trả về tên mô hình tốt nhất theo cột `col` trong nhóm district."""
    if higher_is_better:
        return group.loc[group[col].idxmax(), 'Model']
    else:
        return group.loc[group[col].idxmin(), 'Model']

per_district = []
for did, grp in df.groupby('district_id'):
    row = {
        'district_id': did,
        'Total_Trips': grp['Total_Trips'].iloc[0],
        'Best_AIC': best_model_by_metric(grp, 'AIC'),            # thấp hơn tốt hơn
        'Best_BIC': best_model_by_metric(grp, 'BIC'),            # thấp hơn tốt hơn
        'Best_KS':  best_model_by_metric(grp, 'KS_Stat'),        # thấp hơn tốt hơn
        'Best_AD':  best_model_by_metric(grp, 'AD_Stat'),        # thấp hơn tốt hơn
        'Best_LLH': best_model_by_metric(grp, 'Log_Likelihood', higher_is_better=True),  # cao hơn tốt hơn
    }


    per_district.append(row)

per_district_df = pd.DataFrame(per_district)
per_district_df.to_csv('district_best_model_per_metric.csv', index=False)
print(f"\n>>> Đã lưu bảng best-model per district → 'district_best_model_per_metric.csv'")

# ==============================================================================
# 3. ĐẾM SỐ DISTRICT MỖI MÔ HÌNH CHIẾM ƯU THẾ
# ==============================================================================
metrics = {
    'AIC':           'Best_AIC',
    'BIC':           'Best_BIC',
    'KS-stat':       'Best_KS',
    'AD-stat':       'Best_AD',
    'Log-Likelihood':'Best_LLH',
}



model_order = ['Lognormal', 'Gamma', 'Truncated Lévy Flight', 'Shifted Power-Law', 'Exponential']
palette = {
    'Lognormal':            '#1f77b4', # Blue
    'Gamma':                '#2ca02c', # Green
    'Truncated Lévy Flight':'#41b6c4', # Teal
    'Shifted Power-Law':    '#ff7f0e', # Orange
    'Exponential':          '#d62728', # Red
}

dominance = {}
print("\n" + "="*65)
print(f"{'Model':<25}  {'AIC':>6}  {'BIC':>6}  {'KS':>6}  {'AD':>6}  {'LLH':>6}")
print("="*65)

for model in model_order:
    row = {}
    for label, col in metrics.items():
        cnt = (per_district_df[col] == model).sum()
        pct = cnt / total_districts * 100 if total_districts > 0 else 0
        row[label] = (cnt, pct)
    dominance[model] = row
    aic_s = f"{row['AIC'][0]}({row['AIC'][1]:.1f}%)"
    bic_s = f"{row['BIC'][0]}({row['BIC'][1]:.1f}%)"
    ks_s  = f"{row['KS-stat'][0]}({row['KS-stat'][1]:.0f}%)"
    ad_s  = f"{row['AD-stat'][0]}({row['AD-stat'][1]:.0f}%)"
    llh_s = f"{row['Log-Likelihood'][0]}({row['Log-Likelihood'][1]:.0f}%)"
    print(f"{model:<25}  {aic_s:>9}  {bic_s:>11}  {ks_s:>9}  {ad_s:>9}  {llh_s:>9}")

print("="*55)


# DataFrame tổng hợp
summary_rows = []
for model in model_order:
    r = dominance[model]
    summary_rows.append({
        'Model':                  model,
        'AIC (n / %)':           f"{r['AIC'][0]} / {r['AIC'][1]:.1f}%",
        'BIC (n / %)':           f"{r['BIC'][0]} / {r['BIC'][1]:.1f}%",
        'KS-stat (n / %)':       f"{r['KS-stat'][0]} / {r['KS-stat'][1]:.1f}%",
        'AD-stat (n / %)':       f"{r['AD-stat'][0]} / {r['AD-stat'][1]:.1f}%",
        'Log-Likelihood (n / %)':f"{r['Log-Likelihood'][0]} / {r['Log-Likelihood'][1]:.1f}%",
    })


summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv('district_dominance_by_metric.csv', index=False)

# ==============================================================================
# 4. PHÂN TÍCH ĐỒNG THUẬN (Consensus)
# ==============================================================================

def consensus(row):
    votes = [row['Best_AIC'], row['Best_BIC'], row['Best_KS'],
             row['Best_AD'], row['Best_LLH']]

    from collections import Counter
    top_model, top_votes = Counter(votes).most_common(1)[0]
    return top_model, top_votes


per_district_df[['Consensus_Model', 'Consensus_Votes']] = per_district_df.apply(
    lambda r: pd.Series(consensus(r)), axis=1
)

print("\nPhân phối Consensus Model (District Scale):")
print(per_district_df['Consensus_Model'].value_counts().to_string())

# ==============================================================================
# 5. VẼ BIỂU ĐỒ (5-panel)
# ==============================================================================
fig = plt.figure(figsize=(20, 15))
fig.suptitle(
    'Model Dominance Across 5 Districts by Statistical Metric\n(Macro-Scale Analysis)',
    fontsize=16, fontweight='bold', y=0.98
)

gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])]

metric_cols = list(metrics.values())
titles_display = ['AIC', 'BIC', 'KS-stat', 'AD-stat', 'Log-Likelihood']



for ax, col, title in zip(axes, metric_cols, titles_display):
    counts = per_district_df[col].value_counts()
    counts = counts.reindex([m for m in model_order if m in counts.index]).fillna(0)
    bars = ax.bar(
        range(len(counts)),
        counts.values,
        color=[palette.get(m, '#999999') for m in counts.index],
        edgecolor='white', linewidth=0.8
    )
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(counts)))
    short_names = {'Lognormal': 'LN', 'Exponential': 'Exp', 'Gamma': 'Γ', 'Shifted Power-Law': 'SPL', 'Truncated Lévy Flight': 'TLF'}
    ax.set_xticklabels([short_names.get(m, m) for m in counts.index])
    ax.set_ylim(0, total_districts + 1)
    for bar, val in zip(bars, counts.values):
        pct = val / total_districts * 100 if total_districts > 0 else 0
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.1, f'{int(val)}\n({pct:.0f}%)', ha='center', fontweight='bold', fontsize=10)

plt.savefig('district_dominance_by_metric.png', dpi=200, bbox_inches='tight')
print(f"\n>>> Biểu đồ → 'district_dominance_by_metric.png'")
