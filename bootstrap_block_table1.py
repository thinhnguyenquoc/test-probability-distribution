"""
Block Bootstrap: Kiểm định Table 1 với 5 district-blocks
Resample 5 districts with replacement × 1000 lần
→ CI 95% cho BIC Best %, Mean R², Mean KS

Input:  zone_distribution_metrics.csv, district_zone.csv
Output: bootstrap_table1_ci.csv, bootstrap_table1_distributions.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ─── Load data ───
print("Loading data...")
metrics = pd.read_csv('zone_distribution_metrics.csv')
dz = pd.read_csv('district_zone.csv')

# Map subzone → district
zone_to_dist = dict(zip(dz['zone_id'], dz['district_id']))
dist_names   = dict(zip(dz['district_id'], dz['district_name']))

metrics['district'] = metrics['ORIGIN_SUBZONE'].map(zone_to_dist)
metrics = metrics.dropna(subset=['district'])

districts = metrics['district'].unique()
models = ['Lognormal', 'Shifted Power-Law', 'Gamma', 'Exponential', 'Truncated Lévy Flight']

print(f"Districts: {len(districts)}, Subzones: {metrics['ORIGIN_SUBZONE'].nunique()}, Models: {len(models)}")
print(f"Subzones per district:")
for d in sorted(districts):
    n = metrics[metrics['district'] == d]['ORIGIN_SUBZONE'].nunique()
    print(f"  {dist_names.get(d, d)}: {n} subzones")

# ─── Original (observed) statistics ───
def compute_stats(df):
    """Compute BIC Best %, Mean R², Mean KS per model."""
    best = df[df['Is_Best_BIC'] == True]
    total_best = len(best)
    
    results = {}
    for m in models:
        sub = df[df['Model'] == m]
        bic_count = best[best['Model'] == m].shape[0]
        bic_pct = bic_count / total_best * 100 if total_best > 0 else 0
        mean_r2 = sub['R2'].mean()
        mean_ks = sub['KS_Stat'].mean()
        results[m] = {
            'BIC_Best_Pct': round(bic_pct, 2),
            'Mean_R2': round(mean_r2, 4),
            'Mean_KS': round(mean_ks, 4)
        }
    return results

observed = compute_stats(metrics)
print("\n=== OBSERVED (Original) ===")
for m in models:
    o = observed[m]
    print(f"  {m:30s}  BIC={o['BIC_Best_Pct']:6.2f}%  R²={o['Mean_R2']:.4f}  KS={o['Mean_KS']:.4f}")

# ─── Block Bootstrap ───
N_BOOT = 1000
print(f"\nRunning block bootstrap ({N_BOOT} iterations, {len(districts)} district-blocks)...")

boot_results = {m: {'BIC_Best_Pct': [], 'Mean_R2': [], 'Mean_KS': []} for m in models}

for i in range(N_BOOT):
    # Resample 5 districts with replacement
    sampled_districts = np.random.choice(districts, size=len(districts), replace=True)
    
    # Collect all subzones from sampled districts
    boot_df = pd.concat([metrics[metrics['district'] == d] for d in sampled_districts], ignore_index=True)
    
    # Compute stats
    stats = compute_stats(boot_df)
    for m in models:
        boot_results[m]['BIC_Best_Pct'].append(stats[m]['BIC_Best_Pct'])
        boot_results[m]['Mean_R2'].append(stats[m]['Mean_R2'])
        boot_results[m]['Mean_KS'].append(stats[m]['Mean_KS'])

    if (i + 1) % 200 == 0:
        print(f"  ... {i+1}/{N_BOOT} done")

# ─── Compute 95% CI ───
print("\n=== BLOCK BOOTSTRAP RESULTS (95% CI) ===")
print("=" * 110)
print(f"{'Model':30s} | {'BIC Best %':20s} | {'Mean R²':22s} | {'Mean KS':22s}")
print("-" * 110)

ci_results = []
for m in models:
    bic_arr = np.array(boot_results[m]['BIC_Best_Pct'])
    r2_arr  = np.array(boot_results[m]['Mean_R2'])
    ks_arr  = np.array(boot_results[m]['Mean_KS'])
    
    bic_ci = np.percentile(bic_arr, [2.5, 97.5])
    r2_ci  = np.percentile(r2_arr, [2.5, 97.5])
    ks_ci  = np.percentile(ks_arr, [2.5, 97.5])
    
    o = observed[m]
    print(f"{m:30s} | {o['BIC_Best_Pct']:5.2f} [{bic_ci[0]:5.2f}, {bic_ci[1]:5.2f}] | "
          f"{o['Mean_R2']:.4f} [{r2_ci[0]:.4f}, {r2_ci[1]:.4f}] | "
          f"{o['Mean_KS']:.4f} [{ks_ci[0]:.4f}, {ks_ci[1]:.4f}]")
    
    ci_results.append({
        'Model': m,
        'BIC_Observed': o['BIC_Best_Pct'],
        'BIC_CI_Low': round(bic_ci[0], 2),
        'BIC_CI_High': round(bic_ci[1], 2),
        'R2_Observed': o['Mean_R2'],
        'R2_CI_Low': round(r2_ci[0], 4),
        'R2_CI_High': round(r2_ci[1], 4),
        'KS_Observed': o['Mean_KS'],
        'KS_CI_Low': round(ks_ci[0], 4),
        'KS_CI_High': round(ks_ci[1], 4),
    })

# ─── Key test: Do LN and SPL R² CIs overlap? ───
ln_r2  = np.array(boot_results['Lognormal']['Mean_R2'])
spl_r2 = np.array(boot_results['Shifted Power-Law']['Mean_R2'])
ln_ci  = np.percentile(ln_r2, [2.5, 97.5])
spl_ci = np.percentile(spl_r2, [2.5, 97.5])

overlap = ln_ci[0] <= spl_ci[1] and spl_ci[0] <= ln_ci[1]
diff_pct = np.mean(ln_r2 > spl_r2) * 100

print(f"\n=== KEY TEST: Lognormal R² vs SPL R² ===")
print(f"  LN  R² 95% CI: [{ln_ci[0]:.4f}, {ln_ci[1]:.4f}]")
print(f"  SPL R² 95% CI: [{spl_ci[0]:.4f}, {spl_ci[1]:.4f}]")
print(f"  CIs overlap: {overlap}")
print(f"  P(LN R² > SPL R²) = {diff_pct:.1f}% (across {N_BOOT} bootstrap samples)")

# ─── Save CSV ───
ci_df = pd.DataFrame(ci_results)
ci_df.to_csv('bootstrap_table1_ci.csv', index=False)
print(f"\n>>> Saved: bootstrap_table1_ci.csv")

# ─── Plot distributions ───
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

colors = {'Lognormal': '#e74c3c', 'Shifted Power-Law': '#3498db', 'Gamma': '#2ecc71', 
          'Exponential': '#f39c12', 'Truncated Lévy Flight': '#9b59b6'}

for ax, metric, title in zip(axes, ['BIC_Best_Pct', 'Mean_R2', 'Mean_KS'], 
                              ['BIC Best (%)', 'Mean R²', 'Mean KS-stat']):
    for m in models:
        arr = boot_results[m][metric]
        ax.hist(arr, bins=30, alpha=0.5, color=colors[m], label=m, density=True)
    ax.set_xlabel(title, fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.set_title(f'Bootstrap Distribution: {title}', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('bootstrap_table1_distributions.png', dpi=300)
print(f">>> Saved: bootstrap_table1_distributions.png")

# ─── Print markdown table ───
print("\n--- Markdown Table ---")
print("| Model | BIC Best (%) | 95% CI | Mean R² | 95% CI | Mean KS | 95% CI |")
print("|-------|-------------|--------|---------|--------|---------|--------|")
for r in ci_results:
    print(f"| {r['Model']:27s} | {r['BIC_Observed']:5.2f} | [{r['BIC_CI_Low']:.2f}, {r['BIC_CI_High']:.2f}] | "
          f"{r['R2_Observed']:.4f} | [{r['R2_CI_Low']:.4f}, {r['R2_CI_High']:.4f}] | "
          f"{r['KS_Observed']:.4f} | [{r['KS_CI_Low']:.4f}, {r['KS_CI_High']:.4f}] |")
