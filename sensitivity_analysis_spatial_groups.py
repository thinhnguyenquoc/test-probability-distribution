import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.optimize import minimize

# Distributions
def exp_dist(r, l): return np.exp(-r / l) if l > 0 else np.inf * np.ones_like(r)
def lognormal_dist(r, mu, sigma): return (1.0/(r*sigma)) * np.exp(-(np.log(r)-mu)**2/(2*sigma**2)) if sigma > 0 else np.inf * np.ones_like(r)
def gamma_dist(r, alpha, l): return (r**(alpha-1)) * np.exp(-r/l) if l > 0 and alpha > 0 else np.inf * np.ones_like(r)
def tlf_dist(r, r0, beta, kappa): return (r+r0)**(-beta) * np.exp(-r/kappa) if r0 > 0 and beta > 0 and kappa > 0 else np.inf * np.ones_like(r)

def get_nll(params, r, h, dist_f):
    p = dist_f(r, *params)
    if np.any(p <= 0) or np.any(np.isinf(p)): return 1e18
    p /= np.sum(p)
    return -np.sum(h * np.log(p))

def create_spatial_groups(k_per_district, gdf, districts_df):
    merged = gdf.merge(districts_df, left_on='SUBZONE_C', right_on='zone_id', how='left').dropna(subset=['district_name'])
    district_list = merged['district_name'].unique()
    zone_to_group = {}
    group_counter = 1
    
    for district in sorted(district_list):
        d_zones = merged[merged['district_name'] == district].copy().reset_index(drop=True)
        n_subzones = len(d_zones)
        n_clusters = min(k_per_district, n_subzones)
        
        geoms = d_zones.geometry.values
        connectivity = np.zeros((n_subzones, n_subzones))
        for i in range(n_subzones):
            neighbors = d_zones.geometry.touches(geoms[i]) | d_zones.geometry.intersects(geoms[i])
            connectivity[i, neighbors] = 1
            connectivity[i, i] = 0
            
        centroids = np.array([[g.centroid.x, g.centroid.y] for g in d_zones.geometry])
        model = AgglomerativeClustering(n_clusters=n_clusters, connectivity=connectivity, linkage='complete')
        labels = model.fit_predict(centroids)
        
        for idx, lbl in enumerate(labels):
            zone_to_group[d_zones.loc[idx, 'SUBZONE_C']] = lbl + group_counter
        group_counter += n_clusters
        
    return zone_to_group

def main():
    # Load data
    gdf = gpd.read_file('/Users/nguyenquocthinh/Documents/test-probability-distribution/sub_zone/data_sgp_subzone.shp')
    districts_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/district_zone.csv')
    df_trips = pd.read_csv('data_trip_sum.csv')
    df_dist = pd.read_csv('zone_euclid_distances.csv')
    df_main = df_trips.merge(df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'])
    df_main = df_main.rename(columns={'euclidean_distance_km': 'distance', 'ORIGIN_SUBZONE': 'zone', 'COUNT': 'trips'})
    
    models = {
        'LN': (lognormal_dist, [1.0, 1.0], [(-5, 5), (0.1, 5)]),
        'Gamma': (gamma_dist, [1.5, 3.0], [(0.1, 10), (0.1, 30)]),
        'TLF': (tlf_dist, [1.0, 2.0, 20.0], [(0.1, 20), (0.1, 10), (1, 100)])
    }
    
    print("--- Spatial Sensitivity Analysis (Contiguous Grouping) ---")
    for k_per in [6, 8, 10]:
        total_k = k_per * 5
        print(f"\nScenario: {total_k} groups ({k_per} per district)")
        
        zone_map = create_spatial_groups(k_per, gdf, districts_df)
        df_main['group'] = df_main['zone'].map(zone_map)
        df_grouped = df_main.groupby(['group', 'distance'])['trips'].sum().reset_index()
        
        winners = []
        actual_groups = df_grouped['group'].unique()
        for gId in actual_groups:
            if pd.isna(gId): continue
            df_g = df_grouped[df_grouped['group'] == gId]
            bins = np.linspace(0, df_g['distance'].max(), 30)
            centers = 0.5 * (bins[:-1] + bins[1:])
            h, _ = np.histogram(df_g['distance'], bins=bins, weights=df_g['trips'])
            mask = h > 0
            r_f, h_f = centers[mask], h[mask]
            N = np.sum(h_f)
            
            bics = {}
            for name, (dist_f, p0, bnds) in models.items():
                res = minimize(get_nll, p0, args=(r_f, h_f, dist_f), method='L-BFGS-B', bounds=bnds)
                if res.success:
                    bics[name] = 2 * res.fun + len(p0) * np.log(N)
            if bics:
                winners.append(min(bics, key=bics.get))
        
        print(pd.Series(winners).value_counts(normalize=True) * 100)

if __name__ == "__main__":
    main()
