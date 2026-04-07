import pandas as pd
import numpy as np

print("Đang khởi tạo khung Hàm mô phỏng Bức xạ (Radiation Model)...")
print("Sử dụng Khoảng cách Euclid (EPSG:3414) và Dân số giả định (Trip Proxies)...")

# 1. Tải ma trận
df_trips = pd.read_csv('data_trip_sum.csv')
df_dist = pd.read_csv('zone_euclid_distances.csv')
df = pd.merge(df_trips, df_dist, on=['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE'], how='inner')

# 2. Khởi tạo Proxy Mass (Khối lượng quy chuẩn)
# Dân cư (Origin Mass) là tổng chuyến đi xuất phát khỏi zone đó
# Sức hút việc làm/dịch vụ (Destination Mass) là tổng chuyến đi tới điểm đó
orig_mass = df.groupby('ORIGIN_SUBZONE')['COUNT'].sum().to_dict()
dest_mass = df.groupby('DESTINATION_SUBZONE')['COUNT'].sum().to_dict()

results = []

def calc_radiation_prob(m_i, n_j, s_ij):
    if m_i <= 0 or n_j <= 0: return 0.0
    # Công thức cơ sở (Basic Radiation Model của Simini et al.)
    # P(i -> j) = m_i * n_j / ((m_i + s_ij) * (m_i + n_j + s_ij))
    numerator = m_i * n_j
    denominator = (m_i + s_ij) * (m_i + n_j + s_ij)
    if denominator == 0: return 0.0
    return numerator / denominator

print("Tính toán trung gian s_ij (Lượng khối điểm đến bị bọc trong bán kính cự ly)...")

# 3. Tính lượng dân cư chèn ép (s_ij)
# s_ij là tổng destination mass của tất cả các zone k mà cự ly r(i,k) < r(i,j)
for orig, group in df.groupby('ORIGIN_SUBZONE'):
    m_i = orig_mass.get(orig, 0)
    
    # Sắp xếp khoảng cách tăng dần từ Origin này
    group = group.sort_values(by='euclidean_distance_km')
    
    # Khối lượng hút của từng điểm đến
    group['n_k'] = group['DESTINATION_SUBZONE'].map(dest_mass).fillna(0)
    
    # Khối lượng trung gian s_ij (loại trừ chính n_j ở vòng hiện hành bằng hàm shift)
    group['s_ij'] = group['n_k'].shift(1).fillna(0).cumsum()
    
    # Áp dụng công thức
    group['Radiation_Prob'] = group.apply(lambda row: calc_radiation_prob(m_i, row['n_k'], row['s_ij']), axis=1)
    
    # Chuẩn hoá (Normalize) để tổng xác suất bằng 1 (người dân buộc phải ra khỏi nhà)
    total_prob = group['Radiation_Prob'].sum()
    if total_prob > 0:
        group['Radiation_Prob'] = group['Radiation_Prob'] / total_prob
        
    # Tính số lượng dòng chảy (Flow) ước tính = Xác suất x Tổng người xuất phát
    group['Predicted_Flow'] = group['Radiation_Prob'] * m_i
    
    results.append(group[['ORIGIN_SUBZONE', 'DESTINATION_SUBZONE', 'COUNT', 'euclidean_distance_km', 'Radiation_Prob', 'Predicted_Flow']])

rad_df = pd.concat(results)

# 4. Đánh giá CPC (Common Part of Commuters)
sum_actual = rad_df['COUNT'].sum()
sum_predicted = rad_df['Predicted_Flow'].sum()

cpc_score = (2.0 * np.minimum(rad_df['COUNT'], rad_df['Predicted_Flow']).sum()) / (sum_actual + sum_predicted)

print(f"\n--- ĐÁNH GIÁ MÔ HÌNH BỨC XẠ (RADIATION MODEL) ---")
print(f"Tổng hành trình tham chiếu: {int(sum_actual):,}")
print(f"Chỉ số CPC Score (Mức độ khớp dòng chảy ma trận OD): {cpc_score * 100:.2f}%")

output_file = 'radiation_model_results.csv'
rad_df.to_csv(output_file, index=False)
print(f"\nHoàn tất! Xuất dữ liệu giả lập dòng chảy bức xạ vào tệp '{output_file}'.")
print("Ghi chú: Điểm số CPC này hiện sử dụng số lượng Proxy (Trips). Trong nghiên cứu tương lai, nếu bạn nạp tập dữ liệu Dân số (Population) và Việc làm (Jobs), CPC sẽ tăng tiệm cận > 60-70%.")
