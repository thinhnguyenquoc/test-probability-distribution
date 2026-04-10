import pandas as pd
import numpy as np

def compute_llh(row):
    # BIC = k*log(n) - 2*LLH  => LLH = (k*log(n) - BIC) / 2
    if 'Log_Likelihood' in row and not pd.isna(row['Log_Likelihood']):
        return row['Log_Likelihood']
    if 'AIC' in row and not pd.isna(row['AIC']):
        return (2 * row['k'] - row['AIC']) / 2
    return np.nan

def add_k(df):
    k_map = {
        'Exponential': 2,
        'Lognormal': 3,
        'Gamma': 3,
        'Shifted Power-Law': 3,
        'Truncated Lévy Flight': 4,
        'SPL': 3,
        'TLF': 4,
        'LN': 3,
        'Exp': 2
    }
    df['k'] = df['Model'].map(k_map)
    return df

# 1. Subzone Level
df_zone = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/zone_distribution_metrics.csv')
df_zone = add_k(df_zone)
summary_zone = df_zone.groupby('Model').agg({
    'Log_Likelihood': 'mean',
    'AIC': 'mean',
    'BIC': 'mean',
    'R2': 'mean',
    'KS_Stat': 'mean'
}).reset_index()

# 2. 40 Groups Level (Rerunning might be needed to get LLH, but we use the formula if missing)
df_40 = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/group_40_distribution_metrics.csv')
df_40 = add_k(df_40)
if 'Log_Likelihood' not in df_40.columns:
    df_40['Log_Likelihood'] = df_40.apply(compute_llh, axis=1)
summary_40 = df_40.groupby('Model').agg({
    'Log_Likelihood': 'mean',
    'AIC': 'mean',
    'BIC': 'mean',
    'R2': 'mean',
    'KS_Stat': 'mean'
}).reset_index()

# 3. District Level
df_dist = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/district_distribution_metrics.csv')
df_dist = add_k(df_dist)
summary_dist = df_dist.groupby('Model').agg({
    'Log_Likelihood': 'mean',
    'AIC': 'mean',
    'BIC': 'mean',
    'R2': 'mean',
    'KS_Stat': 'mean'
}).reset_index()

# 4. Global Scale
df_trips = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/data_trip_sum.csv')
n_global = df_trips['COUNT'].sum()
global_data = {
    'Model': ['Exponential', 'Lognormal', 'Shifted Power-Law', 'Truncated Lévy Flight', 'Gamma'],
    'BIC': [39099105, 39230037, 39342512, 39100828, 45060308],
    'R2': [0.7856, 0.9286, 0.7820, 0.7856, 0.8532],
    'KS_Stat': [0.0698, 0.1291, 0.0697, 0.0698, 0.2460],
    'k': [2, 3, 3, 4, 3]
}
df_global = pd.DataFrame(global_data)
log_n = np.log(n_global)
df_global['Log_Likelihood'] = (df_global['k'] * log_n - df_global['BIC']) / 2
df_global['AIC'] = 2 * df_global['k'] - 2 * df_global['Log_Likelihood']

def format_summary(df, title):
    print(f"\n{'='*20} {title} {'='*20}")
    pd.options.display.float_format = '{:,.4f}'.format
    # Format large numbers for readability in paper
    disp_df = df.copy()
    for col in ['Log_Likelihood', 'AIC', 'BIC']:
        disp_df[col] = disp_df[col].apply(lambda x: f"{x/1e6:.2f}M" if abs(x) > 1e6 else (f"{x/1e3:.1f}k" if abs(x) > 1e3 else f"{x:.2f}"))
    print(disp_df[['Model', 'Log_Likelihood', 'AIC', 'BIC', 'R2', 'KS_Stat']])

format_summary(summary_zone, "Subzone Summary (n=303)")
format_summary(summary_40, "40 Groups Summary (n=40)")
format_summary(summary_dist, "District Summary (n=5)")
format_summary(df_global, "Global Summary (n=1)")
