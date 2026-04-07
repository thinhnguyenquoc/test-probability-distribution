import geopandas as gpd
import pandas as pd
import numpy as np
import math
from itertools import product
import warnings

warnings.filterwarnings('ignore')

print("Đang tải shapefile của các zone...")
gdf = gpd.read_file('sub_zone/data_sgp_subzone.shp')

# Mặc định shapefile đang ở EPSG:4326.
# Để tính khoảng cách Euclid chính xác trên mặt phẳng, ta cần chuyển đổi hệ toạ độ (CRS) 
# sang EPSG:3414 (hệ toạ độ chuẩn SVY21 của đảo quốc Singapore có đơn vị là mét).
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)
gdf = gdf.to_crs(epsg=3414)

print("Đang lấy toạ độ X, Y mét của trọng tâm (Centroid)...")
gdf['centroid'] = gdf.geometry.centroid
gdf['x'] = gdf.centroid.x
gdf['y'] = gdf.centroid.y

# Trích xuất dữ liệu thành tự điển
subzone_coords = gdf.set_index('SUBZONE_C')[['x', 'y']].to_dict('index')
subzones = list(subzone_coords.keys())

print(f"Tính toán ma trận khoảng cách Euclid cho mọi cặp trong số {len(subzones)} zones...")
all_pairs = list(product(subzones, subzones))

results = []
for orig, dest in all_pairs:
    x1, y1 = subzone_coords[orig]['x'], subzone_coords[orig]['y']
    x2, y2 = subzone_coords[dest]['x'], subzone_coords[dest]['y']
    
    # Khoảng cách Euclid (bằng mét)
    dist_m = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    # Quy đổi về km
    dist_km = dist_m / 1000.0
    
    results.append({
        'ORIGIN_SUBZONE': orig,
        'DESTINATION_SUBZONE': dest,
        'euclidean_distance_km': round(dist_km, 6)
    })

# Lưu dữ liệu vào file
output_file = 'zone_euclid_distances.csv'
df_dist = pd.DataFrame(results)
df_dist.to_csv(output_file, index=False)

print(f"Hoàn thành! Đã lưu thành công tổng cộng {len(df_dist)} cặp khoảng cách vào file '{output_file}'.")
