import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Distributions
def lognormal_pdf(r, mu, sigma):
    return (1.0 / (r * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))

def gamma_pdf(r, alpha, l):
    return (r**(alpha - 1)) * np.exp(-r / l)

def spl_pdf(r, r0, beta):
    return (r + r0)**(-beta)

def tlf_pdf(r, r0, beta, kappa):
    return (r + r0)**(-beta) * np.exp(-r / kappa)

def exp_pdf(r, l):
    return np.exp(-r / l)

def get_nll(params, r, h, pdf_f):
    p = pdf_f(r, *params)
    if np.any(p <= 0) or np.any(np.isinf(p)): return 1e18
    p /= np.sum(p)
    return -np.sum(h * np.log(np.clip(p, 1e-300, 1)))

def fit_data(r, h, models_config):
    fits = {}
    for name, (pdf_f, p0, bnds) in models_config.items():
        res = minimize(get_nll, p0, args=(r, h, pdf_f), method='L-BFGS-B', bounds=bnds)
        if res.success:
            fits[name] = res.x
    return fits

def main():
    # Load data
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df_main = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df_main = df_main.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone', 'COUNT': 'trips'})
    
    # Scale labels
    scales = ['Subzone', '40 Groups', 'District', 'Global']
    
    # Mapping for scales
    districts_df = pd.read_csv('district_zone.csv')
    groups_df = pd.read_csv('singapore_40_regions.csv')
    
    # Prepare datasets for each scale
    data_scales = []
    
    # 1. Representative Subzone (AMSZ01)
    sub_id = 'AMSZ01'
    data_scales.append(df_main[df_main['zone'] == sub_id])
    
    # 2. Representative Group
    df_group = df_main.merge(groups_df, left_on='zone', right_on='zone_id')
    grp_id = df_group['group_id'].iloc[0]
    data_scales.append(df_group[df_group['group_id'] == grp_id])
    
    # 3. Representative District
    df_distr = df_main.merge(districts_df, left_on='zone', right_on='zone_id')
    dist_id = 1 # Central
    data_scales.append(df_distr[df_distr['district_id'] == dist_id])
    
    # 4. Global
    data_scales.append(df_main)
    
    models_config = {
        'Lognormal': (lognormal_pdf, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_pdf, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'TLF': (tlf_pdf, [1.0, 2.0, 20.0], [(0.1, 20), (0.1, 10), (1, 100)]),
        'SPL': (spl_pdf, [1.0, 2.5], [(0.1, 10), (0.1, 10)]),
        'Exponential': (exp_pdf, [5.0], [(0.1, 100)])
    }
    
    colors = {
        'Lognormal': '#1f77b4', 
        'Gamma': '#2ca02c', 
        'TLF': '#41b6c4',
        'SPL': '#ff7f0e',
        'Exponential': '#d62728'
    }
    
    fig, axes = plt.subplots(1, 4, figsize=(24, 7))
    
    for i, df in enumerate(data_scales):
        ax = axes[i]
        # Histogram
        bins = np.linspace(0.1, min(df['distance'].max(), 40), 40)
        centers = 0.5 * (bins[:-1] + bins[1:])
        h, _ = np.histogram(df['distance'], bins=bins, weights=df['trips'], density=True)
        h_fit_counts, _ = np.histogram(df['distance'], bins=bins, weights=df['trips'])
        mask = h_fit_counts > 0
        r_fit_c, h_fit_c = centers[mask], h_fit_counts[mask]
        N_total = np.sum(h_fit_c)
        
        ax.bar(centers, h, width=np.diff(bins)[0], color='black', alpha=0.15, label='Empirical')
        
        # Fit all 5 models and calculate BIC
        results = []
        for name, (pdf_f, p0, bnds) in models_config.items():
            res = minimize(get_nll, p0, args=(r_fit_c, h_fit_c, pdf_f), method='L-BFGS-B', bounds=bnds)
            if res.success:
                ll = -res.fun
                k = len(p0)
                bic = k * np.log(N_total) - 2 * ll
                results.append({'name': name, 'params': res.x, 'bic': bic, 'pdf_f': pdf_f})
        
        # Sort by BIC and pick top 3
        results = sorted(results, key=lambda x: x['bic'])[:3]
        
        # Plot continuous curves for top 3
        x_plot = np.linspace(0.1, 40, 200)
        max_y = 0.1
        if len(h) > 0 and not np.isnan(np.max(h)):
            max_y = np.max(h)

        for res_item in results:
            name = res_item['name']
            y_plot = res_item['pdf_f'](x_plot, *res_item['params'])
            y_plot = np.nan_to_num(y_plot)
            if np.sum(y_plot) > 0:
                y_norm = y_plot / np.trapz(y_plot, x_plot)
                ax.plot(x_plot, y_norm, color=colors[name], lw=3, label=f'{name}')
                max_curr = np.max(y_norm)
                if not np.isnan(max_curr) and not np.isinf(max_curr):
                    max_y = max(max_y, max_curr)
            
        ax.set_title(f"Scale: {scales[i]}", fontsize=16, weight='bold')
        ax.set_xlabel("Distance (km)")
        if i == 0: ax.set_ylabel("Density")
        ax.legend(fontsize=10, loc='upper right', frameon=True)
        ax.set_ylim(0, max_y * 1.3)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('distribution_morphing_v2.png', dpi=300)
    print("Saved enhanced morphing plot to distribution_morphing_v2.png")

if __name__ == "__main__":
    main()
