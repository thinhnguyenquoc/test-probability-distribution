import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# Load data
print("Loading data...")
metrics = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/zone_distribution_metrics.csv')
regions = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv')

# Map subzone → 40 groups
zone_to_group = dict(zip(regions['zone_id'], regions['group_id']))
metrics['group_block'] = metrics['ORIGIN_SUBZONE'].map(zone_to_group)
metrics = metrics.dropna(subset=['group_block'])

blocks = metrics['group_block'].unique()
models = ['Lognormal', 'Shifted Power-Law', 'Gamma', 'Exponential', 'Truncated Lévy Flight']

print(f"Blocks (40 Groups): {len(blocks)}, Subzones: {metrics['ORIGIN_SUBZONE'].nunique()}, Models: {len(models)}")

def compute_stats(df):
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
            'BIC_Best_Pct': bic_pct,
            'Mean_R2': mean_r2,
            'Mean_KS': mean_ks
        }
    return results

observed = compute_stats(metrics)

# Block Bootstrap
N_BOOT = 1000
print(f"\nRunning block bootstrap ({N_BOOT} iterations, {len(blocks)} blocks)...")

boot_results = {m: {'BIC_Best_Pct': [], 'Mean_R2': [], 'Mean_KS': []} for m in models}

for i in range(N_BOOT):
    # Resample 40 blocks with replacement
    sampled_blocks = np.random.choice(blocks, size=len(blocks), replace=True)
    
    # Collect all subzones from sampled blocks
    # Note: Using a dictionary for faster lookup or pre-grouping
    grouped = metrics.groupby('group_block')
    boot_df = pd.concat([grouped.get_group(b) for b in sampled_blocks], ignore_index=True)
    
    stats_boot = compute_stats(boot_df)
    for m in models:
        boot_results[m]['BIC_Best_Pct'].append(stats_boot[m]['BIC_Best_Pct'])
        boot_results[m]['Mean_R2'].append(stats_boot[m]['Mean_R2'])
        boot_results[m]['Mean_KS'].append(stats_boot[m]['Mean_KS'])

    if (i + 1) % 200 == 0:
        print(f"  ... {i+1}/{N_BOOT} done")

# Compute 95% CI
ci_results = []
for m in models:
    bic_arr = np.array(boot_results[m]['BIC_Best_Pct'])
    r2_arr  = np.array(boot_results[m]['Mean_R2'])
    
    bic_ci = np.percentile(bic_arr, [2.5, 97.5])
    r2_ci  = np.percentile(r2_arr, [2.5, 97.5])
    
    o = observed[m]
    ci_results.append({
        'Model': m,
        'BIC_Observed': o['BIC_Best_Pct'],
        'BIC_CI_Low': round(bic_ci[0], 2),
        'BIC_CI_High': round(bic_ci[1], 2),
        'R2_Observed': o['Mean_R2'],
        'R2_CI_Low': round(r2_ci[0], 4),
        'R2_CI_High': round(r2_ci[1], 4)
    })

# Save results
ci_df = pd.DataFrame(ci_results)
ci_df.to_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/bootstrap_table1_ci_40groups.csv', index=False)

# Print markdown for easy copy-paste
print("\n| Model | BIC Best (%) | 95% CI BIC | Mean R2 | 95% CI R2 |")
print("|-------|-------------|------------|---------|-----------|")
for r in ci_results:
    print(f"| {r['Model']:25s} | {r['BIC_Observed']:5.2f} | [{r['BIC_CI_Low']:.2f}, {r['BIC_CI_High']:.2f}] | {r['R2_Observed']:.4f} | [{r['R2_CI_Low']:.4f}, {r['R2_CI_High']:.4f}] |")
