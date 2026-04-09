import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def plot_3_scales():
    # Load subzones
    gdf = gpd.read_file('/Users/nguyenquocthinh/Documents/test-probability-distribution/sub_zone/data_sgp_subzone.shp')
    # Load mapping
    mapping_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv')
    
    # Merge to get only the subzones used in the study (usually 303 or 323 depending on filter)
    # The mapping_df contains 323 rows usually, but let's check. 
    # Actually, the paper says 303 subzones analyzed.
    merged = gdf.merge(mapping_df, left_on='SUBZONE_C', right_on='zone_id')
    
    # Dissolve for 40 groups
    groups_gdf = merged.dissolve(by='group_name', aggfunc='first').reset_index()
    
    # Dissolve for districts
    districts_gdf = merged.dissolve(by='district_name', aggfunc='first').reset_index()
    
    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(30, 8))
    
    # 1. Subzone Level
    # Plot all subzones in light gray, then study subzones in white with black edge
    gdf.plot(ax=axes[0], color='#f0f0f0', edgecolor='#cccccc', linewidth=0.1)
    merged.plot(ax=axes[0], color='white', edgecolor='black', linewidth=0.3)
    axes[0].set_title('A. Micro-scale: Subzones (n=303)', fontsize=26, pad=20, weight='bold')
    axes[0].axis('off')
    
    # 2. 40 Groups Level (Intermediate)
    groups_gdf.plot(
        column='group_name',
        cmap='tab20',
        edgecolor='black',
        linewidth=0.5,
        ax=axes[1]
    )
    # Add district boundaries on top for context
    districts_gdf.boundary.plot(ax=axes[1], color='black', linewidth=2, alpha=0.7)
    axes[1].set_title('B. Intermediate-scale: 40 Groups', fontsize=26, pad=20, weight='bold')
    axes[1].axis('off')
    
    # 3. District Level (Macro)
    districts_gdf.plot(
        column='district_name',
        cmap='Set3', # Using a distinct map for districts
        edgecolor='black',
        linewidth=1.5,
        ax=axes[2]
    )
    # Add labels for districts
    for idx, row in districts_gdf.iterrows():
        centroid = row.geometry.centroid
        axes[2].text(centroid.x, centroid.y, row['district_name'], 
                     fontsize=20, ha='center', weight='bold',
                     bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'))
    
    axes[2].set_title('C. Macro-scale: 5 Districts', fontsize=26, pad=20, weight='bold')
    axes[2].axis('off')
    
    plt.tight_layout()
    output_path = '/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_spatial_scales.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved 3-scale spatial map to {output_path}")

if __name__ == "__main__":
    plot_3_scales()
