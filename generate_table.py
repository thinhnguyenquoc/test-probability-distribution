import pandas as pd

df = pd.read_csv('district_distribution_metrics.csv')
models = ['Shifted Power-Law', 'Lognormal', 'Truncated Lévy Flight', 'Gamma', 'Exponential']
total_zones = 5

print("| Distribution | BIC Best (%) | Mean R2 | Mean KS-stat | Std. dev. (R2) |")
for m in models:
    sub = df[df['Model'] == m]
    bic_win = len(sub[sub['Is_Best_BIC'] == True])
    bic_pct = (bic_win / total_zones) * 100
    r2_mean = sub['R2'].mean()
    ks_mean = sub['KS_Stat'].mean()
    r2_std = sub['R2'].std()
    
    print(f"| {m} | {bic_pct:.1f} | {r2_mean:.4f} | {ks_mean:.4f} | {r2_std:.4f} |")
