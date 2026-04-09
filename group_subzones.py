import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
import shapely

def group_subzones():
    # Load subzones
    gdf = gpd.read_file('/Users/nguyenquocthinh/Documents/test-probability-distribution/sub_zone/data_sgp_subzone.shp')
    # Load district mapping
    districts_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/district_zone.csv')
    
    # Merge
    merged = gdf.merge(districts_df, left_on='SUBZONE_C', right_on='zone_id', how='left')
    
    # Check for missing districts (islands or special areas)
    if merged['district_name'].isnull().any():
        print(f"Warning: {merged['district_name'].isnull().sum()} subzones have no district mapping.")
        missing_mask = merged['district_name'].isnull()
        print("Missing subzones:", merged.loc[missing_mask, 'SUBZONE_C'].tolist())
        # Drop for now as per usual practice, or we could assign to nearest.
        # But usually, all relevant subzones should be in district_zone.csv
        merged = merged.dropna(subset=['district_name'])

    results = []
    
    # Districts are usually: Central, East, North, North-East, West
    district_list = merged['district_name'].unique()
    
    global_group_counter = 1
    
    for district in sorted(district_list):
        district_subzones = merged[merged['district_name'] == district].copy().reset_index(drop=True)
        n_subzones = len(district_subzones)
        n_clusters = 8 # Each group is 1/8 of a district
        
        if n_subzones < n_clusters:
            print(f"District {district} has only {n_subzones} subzones. Assigning each to its own group.")
            n_clusters = n_subzones
            
        # Build connectivity matrix
        # For spatial adjacency, we use 'touches'
        # To handle minor gaps (precision issues), we can use a very small buffer
        geoms = district_subzones.geometry.values
        connectivity = np.zeros((n_subzones, n_subzones))
        for i in range(n_subzones):
            # Some subzones might be islands; AgglomerativeClustering with connectivity
            # will raise an error if there are isolated components if linkage is ward.
            # However, we can use linkage='complete' or handle disconnected components.
            # Actually, to ensure contiguity, we MUST have a connectivity matrix.
            
            # Simple touches
            neighbors = district_subzones.geometry.touches(geoms[i]) | district_subzones.geometry.intersects(geoms[i])
            connectivity[i, neighbors] = 1
            connectivity[i, i] = 0 # No self-loop needed for sklearn
            
        # Use AgglomerativeClustering
        # Linkage 'ward' requires connectivity to be a sparse matrix usually, 
        # but a dense one works for small numbers.
        # However, 'ward' can be sensitive to disconnected components.
        # If there are disconnected components (islands), scikit-learn will cluster them separately
        # if connectivity is provided.
        
        # Calculate centroids for the distance part of clustering
        centroids = np.array([[g.centroid.x, g.centroid.y] for g in district_subzones.geometry])
        
        model = AgglomerativeClustering(
            n_clusters=n_clusters,
            connectivity=connectivity,
            linkage='complete' # 'complete' is often more robust for spatial contiguity when components are disconnected
        )
        
        # We use the centroids as the 'features' for clustering
        labels = model.fit_predict(centroids)
        
        # Assign global group IDs
        district_subzones['group_id'] = labels + global_group_counter
        district_subzones['group_name'] = district_subzones.apply(
            lambda x: f"{x['district_name']}_G{x['group_id']}", axis=1
        )
        
        results.append(district_subzones)
        global_group_counter += n_clusters

    final_df = pd.concat(results)
    
    # Save to CSV
    output_cols = ['zone_id', 'SUBZONE_N', 'district_id', 'district_name', 'group_id', 'group_name']
    output_path = '/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv'
    final_df[output_cols].to_csv(output_path, index=False)
    print(f"Saved 40 regions mapping to {output_path}")

if __name__ == "__main__":
    group_subzones()
