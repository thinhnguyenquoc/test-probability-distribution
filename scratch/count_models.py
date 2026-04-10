import pandas as pd
df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/subzone_best_model_per_metric.csv')
for col in ['Best_AIC', 'Best_BIC', 'Best_KS', 'Best_LLH', 'Best_R2']:
    print(f"\nMetric: {col}")
    counts = df[col].value_counts()
    for model, count in counts.items():
        pct = count / len(df) * 100
        print(f"{model}: {count} ({pct:.1f}%)")
