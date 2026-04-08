import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import scipy.stats as stats

# Load data
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
dz = pd.read_csv('district_zone.csv')
fb = pd.read_csv('fb_agg.csv')

df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district_id'] = df['ORIGIN_SUBZONE'].map(map_dict)
df = df.dropna(subset=['district_id'])

# Define models
def exp_dist(r, C, lam): return C * np.exp(-r / lam)
def shift_power_law(r, C, r0, beta): return C * (r + r0)**(-beta)
def tlf_model(r, C, r0, beta, kappa): return C * ((r + r0)**(-beta)) * np.exp(-r / kappa)
def lognormal_dist(r, C, mu, sigma):
    r_safe = np.clip(r, 1e-5, None)
    return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))
def gamma_dist(r, C, alpha, lam):
    r_safe = np.clip(r, 1e-5, None)
    return C * (r_safe**(alpha - 1)) * np.exp(-r_safe / lam)

models = {
    'Exponential': (exp_dist, [1, 5], ([0, 1e-3], [np.inf, np.inf])),
    'Lognormal': (lognormal_dist, [1, 1, 1], ([0, -np.inf, 1e-3], [np.inf, np.inf, np.inf])),
    'Gamma': (gamma_dist, [1, 2, 2], ([0, 1e-3, 1e-3], [np.inf, 20, np.inf])),
    'Shifted Power-Law': (shift_power_law, [1, 1, 2], ([0, 1e-3, 1e-3], [np.inf, np.inf, 15])),
    'Truncated Lévy Flight': (tlf_model, [1, 1, 2, 50], ([0, 1e-3, 1e-3, 1e-3], [np.inf, np.inf, 15, np.inf]))
}

def get_emd_binned(p1, p2):
    # p1, p2 are PDFs for the bins (0-1, 1-10, 10-100)
    # Earth Mover's Distance in 1D is literally the sum of absolute difference of CDFs
    cdf1 = np.cumsum(p1)
    cdf2 = np.cumsum(p2)
    return np.mean(np.abs(cdf1 - cdf2))

districts = df['district_id'].unique()
bin_edges = [0, 1, 10, 100]
cat_map = {'(0,1)': 0, '[1, 10)': 1, '[10, 100)': 2}

all_emd = {m: [] for m in list(models.keys()) + ['Hybrid']}
bin_emd = {m: {b: [] for b in range(3)} for m in list(models.keys()) + ['Hybrid']}

for d in districts:
    group = df[df['district_id'] == d]
    dist_trips = group['COUNT'].sum()
    dist_data = group['euclidean_distance_km'].values
    counts = group['COUNT'].values
    
    # FB PDF for this district
    fb_d = fb[fb['district_id'] == d]
    fb_pdf = np.zeros(3)
    for _, row in fb_d.iterrows():
        if row['category'] in cat_map:
            fb_pdf[cat_map[row['category']]] = row['p_fb']
    if fb_pdf.sum() == 0: continue
    fb_pdf /= fb_pdf.sum()
    
    # GT processing for fitting
    num_bins = 50
    bins_fit = np.linspace(0, np.max(dist_data), num_bins+1)
    h, b_e = np.histogram(dist_data, bins=bins_fit, weights=counts)
    b_c = (b_e[:-1] + b_e[1:]) / 2
    mk = h > 0
    x_f = b_c[mk]
    y_f = h[mk] / dist_trips
    
    fitted_pdfs = {}
    for name, (func, p0, bounds) in models.items():
        try:
            popt, _ = curve_fit(func, x_f, y_f, p0=p0, bounds=bounds, maxfev=10000)
            
            # Predict PDF for FB bins
            # We integrate or sample. For simplicity, let's sample at high resolution
            x_fine = np.linspace(0.1, 100, 1000)
            y_fine = func(x_fine, *popt)
            y_fine /= y_fine.sum()
            
            p_cat = np.zeros(3)
            p_cat[0] = y_fine[x_fine < 1].sum()
            p_cat[1] = y_fine[(x_fine >= 1) & (x_fine < 10)].sum()
            p_cat[2] = y_fine[(x_fine >= 10) & (x_fine < 100)].sum()
            if p_cat.sum() > 0: p_cat /= p_cat.sum()
            
            fitted_pdfs[name] = p_cat
            
            emd = get_emd_binned(p_cat, fb_pdf)
            all_emd[name].append(emd)
            for b in range(3):
                bin_emd[name][b].append(np.abs(p_cat[b] - fb_pdf[b]))
        except:
            continue

    # Hybrid Model
    if 'Lognormal' in fitted_pdfs and 'Shifted Power-Law' in fitted_pdfs:
        # λ = 2km as transition point
        lam = 2.0
        x_fine = np.linspace(0.1, 100, 1000)
        w = np.exp(-x_fine/lam)
        
        # Recalculate pops and models to get continuous distribution for integration
        # (Assuming pops already derived in fitted_pdfs loop)
        # For simplicity, reuse binned results with weighting
        p_log = fitted_pdfs['Lognormal']
        p_spl = fitted_pdfs['Shifted Power-Law']
        
        # Weights for bins: (0-1) is micro, [1, 10) is transition, [10, 100) is macro
        # w_bin[0] (0-1km): ~ exp(-0.5/2) = 0.77
        # w_bin[1] (1-10km): ~ exp(-5.5/2) = 0.06
        # w_bin[2] (10-100km): ~ exp(-55/2) = 0.00
        w_bin = np.array([0.77, 0.06, 0.00])
        p_hybrid = w_bin * p_log + (1 - w_bin) * p_spl
        p_hybrid /= p_hybrid.sum()
        
        fitted_pdfs['Hybrid'] = p_hybrid
        emd_h = get_emd_binned(p_hybrid, fb_pdf)
        all_emd['Hybrid'].append(emd_h)
        for b in range(3):
            bin_emd['Hybrid'][b].append(np.abs(p_hybrid[b] - fb_pdf[b]))

print("| Model | EMD (<1 km) | EMD (1–10 km) | EMD (10–100 km) | Overall EMD |")
selected_models = ['Lognormal', 'Shifted Power-Law', 'Truncated Lévy Flight', 'Gamma', 'Exponential', 'Hybrid']
for m in selected_models:
    e0 = np.mean(bin_emd[m][0]) if bin_emd[m][0] else 0
    e1 = np.mean(bin_emd[m][1]) if bin_emd[m][1] else 0
    e2 = np.mean(bin_emd[m][2]) if bin_emd[m][2] else 0
    eo = np.mean(all_emd[m]) if all_emd[m] else 0
    print(f"| {m} | {e0:.2f} | {e1:.2f} | {e2:.2f} | {eo:.2f} |")
