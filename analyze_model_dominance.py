"""
analyze_model_dominance.py
--------------------------
Phân tích từng subzone: mô hình nào khớp tốt nhất theo 4 tiêu chí
(AIC, BIC, KS-stat, Log-Likelihood), sau đó đếm số subzone mỗi mô hình chiếm ưu thế.
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
df = pd.read_csv('zone_distribution_metrics.csv')

# Đảm bảo có đầy đủ cột Log_Likelihood từ AIC nếu thiếu
if 'Log_Likelihood' not in df.columns:
    df['Log_Likelihood'] = (2 * df['k_params'] - df['AIC']) / 2

total_subzones = df['ORIGIN_SUBZONE'].nunique()
print(f"Tổng số subzones: {total_subzones}")
print(f"Tổng số models: {df['Model'].nunique()} — {df['Model'].unique().tolist()}")

# ==============================================================================
# 2. XÁC ĐỊNH MÔ HÌNH TỐT NHẤT PER SUBZONE THEO 4 TIÊU CHÍ
# ==============================================================================

def best_model_by_metric(group, col, higher_is_better=False):
    """Trả về tên mô hình tốt nhất theo cột `col` trong nhóm subzone."""
    if higher_is_better:
        return group.loc[group[col].idxmax(), 'Model']
    else:
        return group.loc[group[col].idxmin(), 'Model']

per_subzone = []
for zone, grp in df.groupby('ORIGIN_SUBZONE'):
    row = {
        'ORIGIN_SUBZONE': zone,
        'Total_Trips': grp['Total_Trips'].iloc[0],
        'Best_AIC': best_model_by_metric(grp, 'AIC'),            # thấp hơn tốt hơn
        'Best_BIC': best_model_by_metric(grp, 'BIC'),            # thấp hơn tốt hơn
        'Best_KS':  best_model_by_metric(grp, 'KS_Stat'),        # thấp hơn tốt hơn
        'Best_LLH': best_model_by_metric(grp, 'Log_Likelihood', higher_is_better=True),  # cao hơn tốt hơn
        'Best_R2':  best_model_by_metric(grp, 'R2', higher_is_better=True),              # cao hơn tốt hơn
    }
    per_subzone.append(row)

per_subzone_df = pd.DataFrame(per_subzone)
per_subzone_df.to_csv('subzone_best_model_per_metric.csv', index=False)
print(f"\n>>> Đã lưu bảng best-model per subzone → 'subzone_best_model_per_metric.csv'")

# ==============================================================================
# 3. ĐẾM SỐ SUBZONE MỖI MÔ HÌNH CHIẾM ƯU THẾ
# ==============================================================================
metrics = {
    'AIC':           'Best_AIC',
    'BIC':           'Best_BIC',
    'KS-stat':       'Best_KS',
    'Log-Likelihood':'Best_LLH',
    'R²':            'Best_R2',
}

model_order = ['Lognormal', 'Exponential', 'Gamma', 'Shifted Power-Law', 'Truncated Lévy Flight']
palette = {
    'Lognormal':            '#4E79A7',
    'Exponential':          '#F28E2B',
    'Gamma':                '#59A14F',
    'Shifted Power-Law':    '#E15759',
    'Truncated Lévy Flight':'#B07AA1',
}

dominance = {}
print("\n" + "="*65)
print(f"{'Model':<25}  {'AIC':>6}  {'BIC':>6}  {'KS':>6}  {'LLH':>6}  {'R²':>6}")
print("="*65)
for model in model_order:
    row = {}
    for label, col in metrics.items():
        cnt = (per_subzone_df[col] == model).sum()
        pct = cnt / total_subzones * 100
        row[label] = (cnt, pct)
    dominance[model] = row
    aic_s = f"{row['AIC'][0]}({row['AIC'][1]:.0f}%)"
    bic_s = f"{row['BIC'][0]}({row['BIC'][1]:.0f}%)"
    ks_s  = f"{row['KS-stat'][0]}({row['KS-stat'][1]:.0f}%)"
    llh_s = f"{row['Log-Likelihood'][0]}({row['Log-Likelihood'][1]:.0f}%)"
    r2_s  = f"{row['R²'][0]}({row['R²'][1]:.0f}%)"
    print(f"{model:<25}  {aic_s:>9}  {bic_s:>9}  {ks_s:>9}  {llh_s:>9}  {r2_s:>9}")
print("="*65)

# Tạo DataFrame tổng hợp dạng clean cho paper
summary_rows = []
for model in model_order:
    r = dominance[model]
    summary_rows.append({
        'Model':                  model,
        'AIC (n / %)':           f"{r['AIC'][0]} / {r['AIC'][1]:.1f}%",
        'BIC (n / %)':           f"{r['BIC'][0]} / {r['BIC'][1]:.1f}%",
        'KS-stat (n / %)':       f"{r['KS-stat'][0]} / {r['KS-stat'][1]:.1f}%",
        'Log-Likelihood (n / %)':f"{r['Log-Likelihood'][0]} / {r['Log-Likelihood'][1]:.1f}%",
        'R² (n / %)':            f"{r['R²'][0]} / {r['R²'][1]:.1f}%",
    })
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv('model_dominance_by_metric.csv', index=False)
print(f"\n>>> Đã lưu bảng tổng hợp → 'model_dominance_by_metric.csv'")

# ==============================================================================
# 4. VẼ BIỂU ĐỒ TỔNG HỢP (5-panel)
# ==============================================================================
fig = plt.figure(figsize=(20, 15))
fig.suptitle(
    'Model Dominance Across 303 Subzones by Statistical Metric\n(Singapore Urban Mobility — Scale-Dependent Analysis)',
    fontsize=16, fontweight='bold', y=0.98
)

gs = GridSpec(2, 3, figure=fig, hspace=0.44, wspace=0.32)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]),
        fig.add_subplot(gs[0, 2]), fig.add_subplot(gs[1, 0]),
        fig.add_subplot(gs[1, 1])]

metric_labels = list(metrics.keys())
metric_cols   = list(metrics.values())
titles_display = ['AIC (lower is better)', 'BIC (lower is better)',
                  'KS-stat (lower is better)', 'Log-Likelihood (higher is better)',
                  'R² (higher is better)']

for ax, col, title in zip(axes, metric_cols, titles_display):
    counts = per_subzone_df[col].value_counts()
    # garantees consistent ordering
    counts = counts.reindex([m for m in model_order if m in counts.index]).dropna()
    bars = ax.bar(
        range(len(counts)),
        counts.values,
        color=[palette.get(m, '#999999') for m in counts.index],
        edgecolor='white', linewidth=0.8
    )
    ax.set_title(title, fontsize=12, fontweight='bold', pad=8)
    ax.set_xticks(range(len(counts)))
    short_names = {
        'Lognormal': 'LN', 'Exponential': 'Exp', 'Gamma': 'Γ',
        'Shifted Power-Law': 'SPL', 'Truncated Lévy Flight': 'TLF'
    }
    ax.set_xticklabels([short_names.get(m, m) for m in counts.index], fontsize=11)
    ax.set_ylabel('Number of Subzones', fontsize=10)
    ax.set_ylim(0, total_subzones + 20)
    ax.axhline(total_subzones, color='gray', linewidth=0.6, linestyle='--', alpha=0.5)
    ax.grid(axis='y', alpha=0.3)
    for bar, (model, val) in zip(bars, counts.items()):
        pct = val / total_subzones * 100
        ax.text(bar.get_x() + bar.get_width()/2, val + 3,
                f'{int(val)}\n({pct:.0f}%)', ha='center', va='bottom',
                fontsize=9, fontweight='bold')

# Panel 6: Heatmap-style consensus table
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
table_data = [['Model', 'AIC', 'BIC', 'KS', 'LLH', 'R²']]
for model in model_order:
    r = dominance[model]
    table_data.append([
        model.replace('Truncated Lévy Flight', 'TLF').replace('Shifted Power-Law', 'SPL'),
        f"{r['AIC'][0]}\n({r['AIC'][1]:.0f}%)",
        f"{r['BIC'][0]}\n({r['BIC'][1]:.0f}%)",
        f"{r['KS-stat'][0]}\n({r['KS-stat'][1]:.0f}%)",
        f"{r['Log-Likelihood'][0]}\n({r['Log-Likelihood'][1]:.0f}%)",
        f"{r['R²'][0]}\n({r['R²'][1]:.0f}%)",
    ])
tbl = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(9)
tbl.scale(1.2, 2.0)
# Màu header
for j in range(6):
    tbl[(0, j)].set_facecolor('#2C3E50')
    tbl[(0, j)].set_text_props(color='white', fontweight='bold')
# Màu từng model
row_colors = [palette.get(m, '#cccccc') + '55' for m in model_order]
for i, color in enumerate(row_colors):
    for j in range(6):
        tbl[(i+1, j)].set_facecolor(color)

ax6.set_title('Dominance Summary Table\n(n subzones / % of 303)', fontweight='bold', fontsize=11)

# Legend chung
legend_patches = [mpatches.Patch(color=palette[m], label=m) for m in model_order]
fig.legend(handles=legend_patches, loc='lower center', ncol=5,
           fontsize=10, framealpha=0.9, bbox_to_anchor=(0.5, 0.01))

plt.savefig('model_dominance_subzone.png', dpi=200, bbox_inches='tight')
print(f"\n>>> Biểu đồ tổng hợp → 'model_dominance_subzone.png'")

# ==============================================================================
# 5. PHÂN TÍCH CONSENSUS: SUBZONE NÀO ĐƯỢC ĐỒNG THUẬN BỞI NHIỀU TIÊU CHÍ?
# ==============================================================================
print("\n" + "="*65)
print("PHÂN TÍCH ĐỒNG THUẬN: Model thắng theo bao nhiêu tiêu chí / subzone")
print("="*65)

def consensus(row):
    votes = [row['Best_AIC'], row['Best_BIC'], row['Best_KS'],
             row['Best_LLH'], row['Best_R2']]
    from collections import Counter
    top_model, top_votes = Counter(votes).most_common(1)[0]
    return top_model, top_votes

per_subzone_df[['Consensus_Model', 'Consensus_Votes']] = per_subzone_df.apply(
    lambda r: pd.Series(consensus(r)), axis=1
)

print("\nPhân phối Consensus Model (mô hình được nhiều tiêu chí đồng thuận nhất):")
print(per_subzone_df['Consensus_Model'].value_counts().to_string())

print("\nPhân phối số phiếu đồng thuận (5 tiêu chí, mỗi vote = 1 tiêu chí):")
print(per_subzone_df['Consensus_Votes'].value_counts().sort_index(ascending=False).to_string())

# Lưu bảng per-subzone đầy đủ
per_subzone_df.to_csv('subzone_best_model_per_metric.csv', index=False)

plt.show()
print("\nHoàn tất.")
