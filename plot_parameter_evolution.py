import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Distribution PDF functions (normalized in the likelihood)
def lognormal_pdf(r, mu, sigma):
    return (1.0 / (r * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))

def gamma_pdf(r, alpha, l):
    return (r**(alpha - 1)) * np.exp(-r / l)

def tlf_pdf(r, r0, beta, kappa):
    return (r + r0)**(-beta) * np.exp(-r / kappa)

def get_nll(params, r, h, pdf_f):
    p = pdf_f(r, *params)
    if np.any(p <= 0) or np.any(np.isinf(p)): return 1e18
    p /= np.sum(p)
    return -np.sum(h * np.log(np.clip(p, 1e-300, 1)))

def fit_scale(df, id_col, models_config):
    results = {m: [] for m in models_config}
    units = df[id_col].unique()
    
    for uid in units:
        unit_data = df[df[id_col] == uid]
        if unit_data['trips'].sum() < 100: continue
        
        # Consistent binning for fitting
        bins = np.linspace(0.1, unit_data['distance'].max(), 30)
        centers = 0.5 * (bins[:-1] + bins[1:])
        h, _ = np.histogram(unit_data['distance'], bins=bins, weights=unit_data['trips'])
        mask = h > 0
        r_f, h_f = centers[mask], h[mask]
        
        for m_name, (pdf_f, p0, bnds) in models_config.items():
            res = minimize(get_nll, p0, args=(r_f, h_f, pdf_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                results[m_name].append(res.x)
    
    return results

def main():
    # Load core data
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df = df.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone', 'COUNT': 'trips'})
    
    # Load scale mappings
    districts_df = pd.read_csv('district_zone.csv')
    groups_df = pd.read_csv('singapore_40_regions.csv') # Already created previously
    
    df_district = df.merge(districts_df, left_on='zone', right_on='zone_id')
    df_group = df.merge(groups_df, left_on='zone', right_on='zone_id')
    
    models_config = {
        'Lognormal': (lognormal_pdf, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_pdf, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'TLF': (tlf_pdf, [1.0, 2.0, 20.0], [(0.1, 10), (0.1, 10), (1, 100)])
    }
    
    scales = ['Subzone', '40 Groups', 'District', 'Global']
    scale_data = [] # List of dicts per scale
    
    # 1. Subzone
    print("Fitting Subzone scale...")
    scale_data.append(fit_scale(df, 'zone', models_config))
    
    # 2. 40 Groups
    print("Fitting 40 Groups scale...")
    scale_data.append(fit_scale(df_group, 'group_id', models_config))
    
    # 3. District
    print("Fitting District scale...")
    scale_data.append(fit_scale(df_district, 'district_id', models_config))
    
    # 4. Global
    print("Fitting Global scale...")
    df['global_id'] = 1
    scale_data.append(fit_scale(df, 'global_id', models_config))
    
    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Panel 0: Lognormal Mu and Sigma
    mu_means = [np.mean([p[0] for p in s['Lognormal']]) for s in scale_data]
    mu_std = [np.std([p[0] for p in s['Lognormal']]) / np.sqrt(max(len(s['Lognormal']), 1)) for s in scale_data]
    sigma_means = [np.mean([p[1] for p in s['Lognormal']]) for s in scale_data]
    sigma_std = [np.std([p[1] for p in s['Lognormal']]) / np.sqrt(max(len(s['Lognormal']), 1)) for s in scale_data]
    
    axes[0].errorbar(scales, mu_means, yerr=1.96*np.array(mu_std), fmt='-o', label='$\mu$ (mean-log)', color='blue')
    axes[0].errorbar(scales, sigma_means, yerr=1.96*np.array(sigma_std), fmt='-o', label='$\sigma$ (sigma-log)', color='cyan')
    axes[0].set_title('Lognormal Parameter Evolution')
    axes[0].set_ylabel('Parameter Value')
    axes[0].legend()
    
    # Panel 1: Gamma Alpha (Shape)
    alpha_means = [np.mean([p[0] for p in s['Gamma']]) for s in scale_data]
    alpha_std = [np.std([p[0] for p in s['Gamma']]) / np.sqrt(max(len(s['Gamma']), 1)) for s in scale_data]
    axes[1].errorbar(scales, alpha_means, yerr=1.96*np.array(alpha_std), fmt='-o', color='green')
    axes[1].set_title('Gamma Shape ($\\alpha$) Evolution')
    axes[1].set_ylabel('$\\alpha$')
    
    # Panel 2: TLF beta (Exponent)
    beta_means = [np.mean([p[1] for p in s['TLF']]) for s in scale_data]
    beta_std = [np.std([p[1] for p in s['TLF']]) / np.sqrt(max(len(s['TLF']), 1)) for s in scale_data]
    axes[2].errorbar(scales, beta_means, yerr=1.96*np.array(beta_std), fmt='-o', color='red')
    axes[2].set_title('TLF Exponent ($\\beta$) Evolution')
    axes[2].set_ylabel('$\\beta$')
    
    # Panel 3: TLF kappa (Truncation)
    kappa_means = [np.mean([p[2] for p in s['TLF']]) for s in scale_data]
    kappa_std = [np.std([p[2] for p in s['TLF']]) / np.sqrt(max(len(s['TLF']), 1)) for s in scale_data]
    axes[3].errorbar(scales, kappa_means, yerr=1.96*np.array(kappa_std), fmt='-o', color='orange')
    axes[3].set_title('TLF Truncation ($\\kappa$) Evolution')
    axes[3].set_ylabel('$\\kappa$ (km)')
    
    for ax in axes:
        ax.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('parameter_evolution_plot.png', dpi=300)
    print("Saved plot to parameter_evolution_plot.png")

if __name__ == "__main__":
    main()
