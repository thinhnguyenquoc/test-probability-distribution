# Kết quả so sánh Facebook Mobility với Dữ liệu tính toán nội bộ

Chúng ta phân dải khoảng cách ra thành 4 nhóm để đối chiếu theo thước đo của FB:
- **(0,1)**: Không di chuyển xa / quanh quẩn dưới 1km.
- **[1, 10)**: Di chuyển từ 1km đến dưới 10km.
- **[10, 100)**: Di chuyển từ 10km đến dưới 100km.
- **100+**: Di chuyển liên vùng từ 100km trở lên.

### Độ đo Trọng tâm: Tuyệt đối (MAE), Trung bình bình phương (MRS/RMSE) và Mức khớp (CPC)
- SGP.1_1: MAE = **0.1086** | MRS (RMSE) = **0.1318** | Khớp CPC = **78.29%**
- SGP.2_1: MAE = **0.0845** | MRS (RMSE) = **0.0996** | Khớp CPC = **83.11%**
- SGP.3_1: MAE = **0.0821** | MRS (RMSE) = **0.1050** | Khớp CPC = **83.58%**
- SGP.4_1: MAE = **0.0793** | MRS (RMSE) = **0.0970** | Khớp CPC = **84.15%**
- SGP.5_1: MAE = **0.0736** | MRS (RMSE) = **0.0901** | Khớp CPC = **85.28%**

👉 **Kết luận sơ bộ**: Hai tệp dữ liệu có đồng nhất hay không được thể hiện thông qua MAE. Sai số (MAE) lý tưởng nếu gần 0. Điểm khác biệt rõ rệt nhất thường xuất hiện ở hạng mục đi về khoảng cách `[10, 100)` hay trong nội khu `0`. Nếu các cột P_fb và P_gt trong ảnh chênh lệch lớn thì quy mô mô hình GT hiện định giá khoảng cách liên vùng không sát với FB.