import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load data
print("Loading data...")
try:
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# Global distance distribution
distances = df['euclidean_distance_km'].values
counts = df['COUNT'].values

# Create bins
num_bins = 100
bins = np.logspace(np.log10(max(0.1, np.min(distances))), np.log10(np.max(distances)), num_bins+1)
hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
bin_widths = bin_edges[1:] - bin_edges[:-1]

# Normalize to probability density
density = hist / (np.sum(hist) * bin_widths)

# Filter out zeros
mask = (density > 0) & (bin_centers > 0)
x = bin_centers[mask]
y = density[mask]

# Define models
def power_law(r, C, alpha):
    return C * r**(-alpha)

def lognormal(r, C, mu, sigma):
    return (C / (r * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r) - mu)**2 / (2 * sigma**2))

def shifted_power_law(r, C, r0, beta):
    return C * (r + r0)**(-beta)

# Fit models
print("Fitting models...")
try:
    # Use better initial guesses and increased maxfev
    popt_pl, _ = curve_fit(power_law, x, y, p0=[1, 2], maxfev=20000)
    
    # Lognormal fitting needs careful initialization
    mean_log = np.mean(np.log(x))
    std_log = np.std(np.log(x))
    popt_lognorm, _ = curve_fit(lognormal, x, y, p0=[1, mean_log, std_log], maxfev=20000)
    
    # Shifted Power-law
    popt_spl, _ = curve_fit(shifted_power_law, x, y, p0=[1, 0.5, 2], bounds=([0, 1e-4, 0], [np.inf, 10, 10]), maxfev=20000)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, color='black', alpha=0.5, label='Empirical Data (Singapore)')
    plt.plot(x, power_law(x, *popt_pl), 'r--', label=f'Power-law (Scale-free): alpha={popt_pl[1]:.2f}')
    plt.plot(x, lognormal(x, *popt_lognorm), 'g-', label='Lognormal')
    plt.plot(x, shifted_power_law(x, *popt_spl), 'b-', label='Shifted Power-law')

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Distance d (km)')
    plt.ylabel('Probability Density P(d)')
    plt.title('Log-Log plot of Mobility Distance Distribution')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.savefig('scale_free_check.png', dpi=300)
    print("Plot saved to 'scale_free_check.png'")

    # Calculate MSE for quantitative check (in log space)
    mse_pl = np.mean((np.log(y) - np.log(power_law(x, *popt_pl)))**2)
    mse_lognorm = np.mean((np.log(y) - np.log(lognormal(x, *popt_lognorm)))**2)
    mse_spl = np.mean((np.log(y) - np.log(shifted_power_law(x, *popt_spl)))**2)

    print(f"MSE Power-law (Log-Log): {mse_pl:.4f}")
    print(f"MSE Lognormal (Log-Log): {mse_lognorm:.4f}")
    print(f"MSE Shifted Power-law (Log-Log): {mse_spl:.4f}")

    if mse_pl < mse_lognorm and mse_pl < mse_spl:
        print("Conclusion: Du lieu co xu huong Scale-free (Power-law tot nhat).")
    else:
        print("Conclusion: Du lieu KHONG thuan tuy Scale-free. Lognormal hoac Shifted Power-law khop tot hon.")
        
except Exception as e:
    print(f"Error during fitting: {e}")
