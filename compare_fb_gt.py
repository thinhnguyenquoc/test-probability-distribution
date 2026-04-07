import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import os
import io

import warnings
warnings.filterwarnings('ignore')

print("Đang đọc dữ liệu...")
gdf = gpd.read_file('sub_zone/data_sgp_subzone.shp')
df = pd.read_csv('data_trip_sum.csv')
dz = pd.read_csv('district_zone.csv')
fb = pd.read_csv('fb_agg.csv')

# Ánh xạ subzone về district cho ORIGIN
map_dict = dict(zip(dz['zone_id'], dz['district_id']))
df['district_id'] = df['ORIGIN_SUBZONE'].map(map_dict)

# Tính centroid tọa độ lat/lon
gdf = gdf.to_crs(epsg=4326)
gdf['centroid'] = gdf.geometry.centroid
gdf['lon'] = gdf.centroid.x
gdf['lat'] = gdf.centroid.y
subzone_dict = gdf.set_index('SUBZONE_C')[['lat', 'lon']].to_dict('index')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

# Tính khoảng cách vector hóa
lats1 = df['ORIGIN_SUBZONE'].map(lambda x: subzone_dict[x]['lat'] if x in subzone_dict else np.nan)
lons1 = df['ORIGIN_SUBZONE'].map(lambda x: subzone_dict[x]['lon'] if x in subzone_dict else np.nan)
lats2 = df['DESTINATION_SUBZONE'].map(lambda x: subzone_dict[x]['lat'] if x in subzone_dict else np.nan)
lons2 = df['DESTINATION_SUBZONE'].map(lambda x: subzone_dict[x]['lon'] if x in subzone_dict else np.nan)

df['distance'] = haversine(lats1, lons1, lats2, lons2)
df = df.dropna(subset=['distance', 'district_id'])

# Phân loại khoảng cách theo chuẩn Facebook mới
def bin_distance(d):
    if d < 1:
        return '(0,1)'
    elif 1 <= d < 10:
        return '(1, 10)'
    elif 10 <= d < 100:
        return '[10, 100)'
    else:
        return '100+'
        
df['category'] = df['distance'].apply(bin_distance)

# Tổng hợp (Aggregation) GT của chúng ta (Ground Truth)
print("Đang tiến hành gom nhóm (Aggregation)...")
gt_agg = df.groupby(['district_id', 'category'])['COUNT'].sum().reset_index()
district_totals = gt_agg.groupby('district_id')['COUNT'].transform('sum')
gt_agg['p_gt'] = gt_agg['COUNT'] / district_totals

# Merge dữ liệu FB và Dữ liệu tính toán độc lập
comparison = pd.merge(fb[['district_id', 'category', 'p_fb']], 
                      gt_agg[['district_id', 'category', 'p_gt']], 
                      on=['district_id', 'category'], 
                      how='outer').fillna(0)

# Khớp lại order category
cat_order = ['(0,1)', '(1, 10)', '[10, 100)', '100+']
comparison['cat_order'] = comparison['category'].map({k: i for i, k in enumerate(cat_order)})
comparison = comparison.sort_values(by=['district_id', 'cat_order']).drop(columns=['cat_order'])

# Lọc bỏ index cho gọn
districts = comparison['district_id'].unique()

print("\n--- Đánh giá độ phù hợp (Sai số trung bình tuyệt đối - MAE) ---")
results_md = "# Kết quả so sánh Facebook Mobility với Dữ liệu tính toán nội bộ\n\n"
results_md += "Chúng ta phân dải khoảng cách ra thành 4 nhóm để đối chiếu theo thước đo của FB:\n"
results_md += "- **(0,1)**: Không di chuyển xa / quanh quẩn dưới 1km.\n"
results_md += "- **(1, 10)**: Di chuyển từ 1km đến dưới 10km.\n"
results_md += "- **[10, 100)**: Di chuyển từ 10km đến dưới 100km.\n"
results_md += "- **100+**: Di chuyển liên vùng từ 100km trở lên.\n\n"

results_md += "### Độ đo Sai số trung bình tuyệt đối (MAE)\n"
for d in districts:
    dist_data = comparison[comparison['district_id'] == d]
    mae = np.mean(np.abs(dist_data['p_fb'] - dist_data['p_gt']))
    msg = f"- {d}: **{mae:.4f}**"
    print(msg)
    results_md += msg + "\n"

# Plotting bar charts
fig, axes = plt.subplots(3, 2, figsize=(15, 12))
axes = axes.flatten()

for i, d in enumerate(districts):
    ax = axes[i]
    dist_data = comparison[comparison['district_id'] == d]
    
    x = np.arange(len(cat_order))
    width = 0.35
    
    # Xếp lại cột theo đúng order đã định
    fb_vals = []
    gt_vals = []
    for cat in cat_order:
        row = dist_data[dist_data['category'] == cat]
        if not row.empty:
            fb_vals.append(row['p_fb'].values[0])
            gt_vals.append(row['p_gt'].values[0])
        else:
            fb_vals.append(0)
            gt_vals.append(0)
            
    ax.bar(x - width/2, fb_vals, width, label='Facebook (P_fb)', color='blue', alpha=0.7)
    ax.bar(x + width/2, gt_vals, width, label='Tính Nội Bộ (P_gt)', color='green', alpha=0.7)
    
    ax.set_title(f"Quận (District): {d}")
    ax.set_xticks(x)
    ax.set_xticklabels(cat_order)
    ax.set_ylabel("Xác suất (Probability)")
    
    if i == 0:
        ax.legend()
        
    ax.grid(axis='y', ls='--', alpha=0.5)

# Tắt plot thừa
for j in range(len(districts), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig("fb_vs_gt_comparison.png", dpi=300)
print("\nĐã lưu biểu đồ vào fb_vs_gt_comparison.png")

comparison.to_csv("fb_vs_gt_merged.csv", index=False)

results_md += "\n👉 **Kết luận sơ bộ**: Hai tệp dữ liệu có đồng nhất hay không được thể hiện thông qua MAE. Sai số (MAE) lý tưởng nếu gần 0. Điểm khác biệt rõ rệt nhất thường xuất hiện ở hạng mục đi về khoảng cách `[10, 100)` hay trong nội khu `0`. Nếu các cột P_fb và P_gt trong ảnh chênh lệch lớn thì quy mô mô hình GT hiện định giá khoảng cách liên vùng không sát với FB."

with open("ket_qua_so_sanh_fb.md", "w", encoding="utf-8") as f:
    f.write(results_md)

print("Đã xuất text summary vào ket_qua_so_sanh_fb.md")
