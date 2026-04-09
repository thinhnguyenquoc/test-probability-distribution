import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def generate_maps():
    # Load subzones
    gdf = gpd.read_file('/Users/nguyenquocthinh/Documents/test-probability-distribution/sub_zone/data_sgp_subzone.shp')
    
    # Load the 40 regions mapping for names and districts
    regions_df = pd.read_csv('/Users/nguyenquocthinh/Documents/test-probability-distribution/singapore_40_regions.csv')
    merged = gdf.merge(regions_df, left_on='SUBZONE_C', right_on='zone_id')

    # 1. District Map
    districts_gdf = merged.dissolve(by='district_name')
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    districts_gdf.plot(ax=ax1, cmap='Set3', edgecolor='black', linewidth=1)
    ax1.set_title('Hierarchy: 5 Planning Districts', fontsize=14)
    ax1.axis('off')
    plt.savefig('singapore_districts_map.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. 40 Groups Map
    groups_gdf = merged.dissolve(by='group_name').reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    groups_gdf.plot(ax=ax2, column='group_name', cmap='tab20', edgecolor='white', linewidth=0.5)
    ax2.set_title('Hierarchy: 40 Regions (Intermediate scale)', fontsize=14)
    ax2.axis('off')
    plt.savefig('singapore_40_groups_map.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Subzone Map
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax3, color='lightgrey', edgecolor='grey', linewidth=0.3)
    ax3.set_title('Hierarchy: 303 Subzones (Micro scale)', fontsize=14)
    ax3.axis('off')
    plt.savefig('singapore_subzones_map.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Success: Generated district, 40_groups, and subzones maps.")

if __name__ == "__main__":
    generate_maps()
