import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def plot_regions():
    # Load subzones
    gdf = gpd.read_file('/Users/nguyenquocthinh/Documents/test-probability-distribution/sub_zone/data_sgp_subzone.shp')
    # Load the 40 regions mapping
    regions_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv')
    
    # Merge
    merged = gdf.merge(regions_df, left_on='SUBZONE_C', right_on='zone_id')
    
    # Dissolve subzones into groups
    # This creates a single polygon for each of the 40 groups
    groups_gdf = merged.dissolve(by='group_name', aggfunc='first').reset_index()
    
    # Plotting
    fig, ax = plt.subplots(figsize=(20, 12))
    
    # Use a categorical colormap with 40 colors
    # 'jet' or 'nipy_spectral' or cycling 'tab20'
    groups_gdf.plot(
        column='group_name',
        cmap='tab20', # Cycle through colors
        edgecolor='white',
        linewidth=0.5,
        ax=ax,
        legend=False # Legend for 40 items is too big
    )
    
    # Add labels for groups
    for idx, row in groups_gdf.iterrows():
        # Label at centroid
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, row['group_id'], 
                fontsize=8, ha='center', color='black', weight='bold',
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=1))
    
    # Add district boundaries for clarity
    districts_gdf = merged.dissolve(by='district_name')
    districts_gdf.boundary.plot(ax=ax, color='black', linewidth=1.5, alpha=0.7)
    
    ax.set_title('Singapore 40 Geographic Regions (8 groups per district)', fontsize=20, pad=20)
    ax.axis('off')
    
    output_path = '/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved region map to {output_path}")

if __name__ == "__main__":
    plot_regions()
