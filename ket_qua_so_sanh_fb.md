# Kết quả so sánh Facebook Mobility với Dữ liệu tính toán nội bộ

Chúng ta phân dải khoảng cách ra thành 4 nhóm để đối chiếu theo thước đo của FB:
- **(0,1)**: Không di chuyển xa / quanh quẩn dưới 1km.
- **(1, 10)**: Di chuyển từ 1km đến dưới 10km.
- **[10, 100)**: Di chuyển từ 10km đến dưới 100km.
- **100+**: Di chuyển liên vùng từ 100km trở lên.

### Độ đo Sai số trung bình tuyệt đối (MAE)
- SGP.1_1: **0.1086**
- SGP.2_1: **0.0845**
- SGP.3_1: **0.0821**
- SGP.4_1: **0.0793**
- SGP.5_1: **0.0736**

👉 **Kết luận sơ bộ**: Hai tệp dữ liệu có đồng nhất hay không được thể hiện thông qua MAE. Sai số (MAE) lý tưởng nếu gần 0. Điểm khác biệt rõ rệt nhất thường xuất hiện ở hạng mục đi về khoảng cách `[10, 100)` hay trong nội khu `0`. Nếu các cột P_fb và P_gt trong ảnh chênh lệch lớn thì quy mô mô hình GT hiện định giá khoảng cách liên vùng không sát với FB.