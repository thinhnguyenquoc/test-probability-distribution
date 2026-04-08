import geopandas as gpd
import matplotlib.pyplot as plt

# Set style
plt.style.use('bmh')

# Load data
subzone_path = 'sub_zone/data_sgp_subzone.shp'
district_path = 'gadm41/gadm41_SGP_1.shp'

subzones = gpd.read_file(subzone_path)
districts = gpd.read_file(district_path)

# 1. Plot Subzones
fig, ax = plt.subplots(figsize=(12, 8))
subzones.plot(ax=ax, color='#e0f2f1', edgecolor='#00695c', linewidth=0.5)
ax.set_title('Singapore Subzone Boundaries (Micro-scale)', fontsize=15, pad=20, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig('singapore_subzones.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Plot Districts
fig, ax = plt.subplots(figsize=(12, 8))
# Use a categorical color map for districts
districts.plot(ax=ax, column='NAME_1', cmap='Set3', edgecolor='#455a64', linewidth=1, legend=True, 
               legend_kwds={'title': 'District Name', 'bbox_to_anchor': (1, 1)})
ax.set_title('Singapore Planning Districts (Macro-scale)', fontsize=15, pad=20, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig('singapore_districts.png', dpi=300, bbox_inches='tight')
plt.close()

print("Maps generated: singapore_subzones.png, singapore_districts.png")
