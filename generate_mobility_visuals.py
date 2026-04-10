import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def generate_visuals():
    print("Loading data...")
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    
    total_trips = df['COUNT'].sum()
    distances = df['euclidean_distance_km'].values
    counts = df['COUNT'].values
    
    # 1. Histogram (Linear Scale)
    print("Generating Histogram...")
    plt.figure(figsize=(10, 6))
    bins = np.linspace(0, np.max(distances), 51)
    hist, bin_edges = np.histogram(distances, bins=bins, weights=counts)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    plt.bar(bin_centers, hist/total_trips, width=(bin_edges[1]-bin_edges[0])*0.8, color='skyblue', alpha=0.7, label='Data')
    plt.xlabel('Distance (km)')
    plt.ylabel('Probability Density')
    plt.title('Trip Distance Distribution (Histogram)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('distance_histogram.png', dpi=300)
    plt.close()

    # Define models for plotting fits
    def lognormal_dist(r, C, mu, sigma):
        r_safe = np.clip(r, 1e-5, None)
        return (C / (r_safe * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(r_safe) - mu)**2 / (2 * sigma**2))

    def shift_power_law(r, C, r0, beta):
        return C * (r + r0)**(-beta)

    def exp_dist(r, C, lam):
        return C * np.exp(-r / lam)

    # Prepare data for log-log and fitting
    mask = hist > 0
    x_data = bin_centers[mask]
    y_data = hist[mask] / total_trips
    
    # 2. Log-Log Plot
    print("Generating Log-Log Plot...")
    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, color='black', s=20, label='Empirical Data')
    
    # Fit and plot Exponential
    popt_exp, _ = curve_fit(exp_dist, x_data, y_data, p0=[1, 5], maxfev=50000)
    plt.plot(x_data, exp_dist(x_data, *popt_exp), 'r--', label=f'Exponential Fit (λ={popt_exp[1]:.2f})')
    
    # Fit and plot SPL
    # Use better initial guess and constraints for global scale
    try:
        popt_spl, _ = curve_fit(shift_power_law, x_data, y_data, p0=[0.1, 1, 2], bounds=([0, 0.01, 1], [10, 10, 5]), maxfev=100000)
        plt.plot(x_data, shift_power_law(x_data, *popt_spl), 'b-', label=f'Shifted Power-Law (β={popt_spl[2]:.2f})')
    except Exception as e:
        print(f"SPL fit failed: {e}")
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Distance (km) - log scale')
    plt.ylabel('P(r) - log scale')
    plt.title('Trip Distance Distribution (Log-Log Scale)')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig('distance_loglog.png', dpi=300)
    plt.close()

    # 3. CCDF (Complementary Cumulative Distribution Function)
    print("Generating CCDF Plot...")
    # Sort distances to calculate CCDF
    sorted_indices = np.argsort(distances)
    sorted_dist = distances[sorted_indices]
    sorted_counts = counts[sorted_indices]
    
    total_trips_sum = np.sum(sorted_counts)
    cdf = np.cumsum(sorted_counts) / total_trips_sum
    ccdf = 1 - cdf
    
    plt.figure(figsize=(10, 6))
    # Downsample for plotting if too many points
    step = max(1, len(sorted_dist) // 1000)
    plt.plot(sorted_dist[::step], ccdf[::step], 'k.', markersize=3, label='Log-Log CCDF')
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Distance r (km)')
    plt.ylabel('P(R > r)')
    plt.title('Complementary Cumulative Distribution Function (CCDF)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig('distance_ccdf.png', dpi=300)
    plt.close()
    
    print("All plots saved: distance_histogram.png, distance_loglog.png, distance_ccdf.png")

if __name__ == "__main__":
    generate_visuals()
