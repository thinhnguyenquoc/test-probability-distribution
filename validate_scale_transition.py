import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load Data
zone_df = pd.read_csv('zone_distribution_metrics.csv')
district_df = pd.read_csv('district_distribution_metrics.csv')

def get_metrics(df, level_name):
    ln_df = df[df['Model'] == 'Lognormal']
    spl_df = df[df['Model'] == 'Shifted Power-Law']
    
    ln_r2 = ln_df['R2'].mean()
    spl_r2 = spl_df['R2'].mean()
    
    ln_ks = ln_df['KS_Stat'].mean()
    spl_ks = spl_df['KS_Stat'].mean()
    
    total_locations = len(df['ORIGIN_SUBZONE'].unique()) if 'ORIGIN_SUBZONE' in df.columns else len(df['district_id'].unique())
    ln_wins = len(ln_df[ln_df['Is_Best_BIC'] == True])
    spl_wins = len(spl_df[spl_df['Is_Best_BIC'] == True])
    
    ln_win_rate = (ln_wins / total_locations) * 100
    spl_win_rate = (spl_wins / total_locations) * 100
    
    print(f"--- {level_name.upper()} LEVEL ---")
    print(f"Lognormal -> Mean R2: {ln_r2:.4f}, Mean KS: {ln_ks:.4f}, BIC Win Rate: {ln_win_rate:.1f}% ({ln_wins}/{total_locations})")
    print(f"SPL -> Mean R2: {spl_r2:.4f}, Mean KS: {spl_ks:.4f}, BIC Win Rate: {spl_win_rate:.1f}% ({spl_wins}/{total_locations})")
    print()
    
    return [ln_r2, spl_r2], [ln_ks, spl_ks], [ln_win_rate, spl_win_rate]

print("KHẢO SÁT CHỮNG MINH LUẬN ĐIỂM CHUYỂN PHA (SCALE TRANSITION)\n")
micro_r2, micro_ks, micro_win = get_metrics(zone_df, "Micro (Zone)")
macro_r2, macro_ks, macro_win = get_metrics(district_df, "Macro (District)")

# Plotting the aggregated validation
fig, axs = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Validation of Scale Transition Hypothesis:\nLognormal (Micro) vs Shifted Power-Law (Macro)', fontsize=16, fontweight='bold', y=0.98)

models = ['Lognormal', 'Shifted Power-Law']
colors = ['#1f77b4', '#d62728']

def plot_bar(ax, data, title, ylabel, is_percentage=False):
    bars = ax.bar(models, data, color=colors, width=0.5)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(data) * 1.2 if max(data) > 0 else 1)
    
    for bar in bars:
        height = bar.get_height()
        label = f"{height:.1f}%" if is_percentage else f"{height:.4f}"
        ax.text(bar.get_x() + bar.get_width()/2., height + (max(data)*0.02),
                label, ha='center', va='bottom', fontweight='bold')

# Row 1: Micro Level
plot_bar(axs[0, 0], micro_r2, 'Micro (Zone) - Phù hợp R² (Cao là Tốt)', 'Mean R²')
plot_bar(axs[0, 1], micro_ks, 'Micro (Zone) - Sai lệch KS-Stat (Thấp là Tốt)', 'Mean KS-Stat')
plot_bar(axs[0, 2], micro_win, 'Micro (Zone) - Tỉ lệ Chiến thắng BIC', 'Win Rate (%)', is_percentage=True)

# Row 2: Macro Level
plot_bar(axs[1, 0], macro_r2, 'Macro (District) - Phù hợp R² (Cao là Tốt)', 'Mean R²')
plot_bar(axs[1, 1], macro_ks, 'Macro (District) - Sai lệch KS-Stat (Thấp là Tốt)', 'Mean KS-Stat')
plot_bar(axs[1, 2], macro_win, 'Macro (District) - Tỉ lệ Chiến thắng BIC', 'Win Rate (%)', is_percentage=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('scale_transition_validation.png', dpi=300)
print("Saved comparison chart to 'scale_transition_validation.png'")

