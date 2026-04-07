# Nhật ký Kỹ thuật: Quy trình Phân tích và Đối chiếu Mô hình Dịch chuyển Không gian

Tài liệu này tổng hợp lại tuần tự toàn bộ các bước thao tác kỹ thuật và mã nguồn chúng ta đã gỡ rối, phân tích dữ liệu và thiết lập mô hình tính từ đầu quy trình đến thời điểm hiện tại.

---

## Bước 1: Tiền xử lý dữ liệu và Khảo nghiệm mô hình Truncated Lévy Flight
- **Mã nguồn áp dụng:** `process_mobility.py`
- **Mô tả thao tác:**
  1. Sử dụng thư viện `geopandas` nạp tệp bản đồ số `sub_zone/data_sgp_subzone.shp`, sau đó chuyển đổi hình chiếu địa lý về **EPSG:4326** để tính toán vị trí trọng tâm (Centroid Lat/Lon) cho từng phân khu (Zone).
  2. Map dữ liệu toạ độ vào ma trận gốc `data_trip_sum.csv`, tính toán khoảng cách cự ly di chuyển cho từng cặp OD (ORIGIN-DESTINATION) bằng **công thức Haversine**.
  3. Chia tần suất xuất hiện chuyến đi (Count) trên mỗi quãng khoảng cách vào các bins để tính xác suất phân phối mức độ (Probability density - $P(\Delta r)$).
  4. Ứng dụng hàm hồi quy phi tuyến `scipy.optimize.curve_fit` nhằm tìm hệ số cho phương trình **Truncated Lévy Flight**.
  5. Phát hiện ra tham số giới hạn rãn $\kappa$ rơi vào vô cực, chỉ định rằng tại quy mô Singapore (đường kính rất nhỏ < 50km), hiện tượng luỹ thừa suy rụng cuối đuôi đồ thị (exponential cutoff) không xuất hiện.

---

## Bước 2: Thử nghiệm đa mô hình Không gian tại Tổng diện
- **Mã nguồn áp dụng:** `compare_dist.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Tích hợp bổ sung các hàm phân phối khác nhằm thay thế khoảng trống về tính hiệu quả của Lévy Flight, bao gồm: **Exponential (Mũ)**, **Lognormal**, **Gamma**, và **Shifted Power-Law**.
  2. Tạo bộ đánh giá custom $R^2$ (Hệ số tương quan).
  3. Kết quả sơ bộ toàn tuyến đường giao thông thu về: Exponential và Lognormal hoạt động rất hiệu quả ở cấp vi mô.

---

## Bước 3: Nội suy Phân phối riêng lẻ trên Mạng lưới Vi mô
- **Mã nguồn áp dụng:** `zone_distributions.py`
- **Tập kết quả:** `zone_distribution_results.csv`
- **Mô tả thao tác:**
  1. Phân luồng dữ liệu (Group data) bằng thuật toán nhóm độc lập từng phân khu khởi hành (`ORIGIN_SUBZONE`).
  2. Tinh gọn nhiễu: Loại bỏ các khu vực tĩnh, ít dân cư có dưới 500 chuyến phát sinh.
  3. Cho máy chạy vòng lặp Fitting đo lường lại $R^2$ của 4 mô hình đại diện trên tổng toàn đảo (> 300 phân khu tồn tại).
  4. Lập báo cáo đếm tần suất mô hình chiến thắng: Khẳng định thuyết Lognormal chiếm lĩnh tuyệt đối nội thị với mức phù hợp tối đa cho 69.4% diện tích khu vực. Gamma về nhì giúp phác hoạ "khoảng cách giao lưu ưa thích" làm vùng đệm.

---

## Bước 4: Validation chéo cùng Facebook Mobility API
- **Mã nguồn áp dụng:** `compare_fb_gt.py`
- **Dữ liệu mốc:** `district_zone.csv` và `fb_agg.csv`
- **Mô tả thao tác:**
  1. Gán nhãn các phân khu nhỏ `ORIGIN_SUBZONE` sang Quận rộng `district_id` dựa trên ánh xạ đối chiếu.
  2. Quy nạp khoảng cách phân mảnh nội bộ vào tiêu chuẩn bảng Facebook, gồm 4 cụm: `< 1km` quy thành nhóm `(0, 1)`, dải `[1, 10)`, dải `[10, 100)` và `100+`. (Có fix cú pháp csv từ `0` sang `(0,1)` bằng tool xử lý dòng).
  3. Gom lại xác suất ($P_{gt}$) tính theo tần suất tại cấp District, sát nhập bảng dọc đối chiếu với tỷ lệ ping vệ tinh từ Facebook ($P_{fb}$).
  4. Đo kiểm tra độ chặt chẽ của biểu đồ thống kê hai nguồn bằng mốc lỗi **Sai số Trung bình Tuyệt đối (MAE - Mean Absolute Error)**. 
  5. Hai kết quả bâu lấy biểu đồ tại mốc MAE cực kỳ nhỏ (< 11%). Khẳng định cấu trúc sử dụng quy hoạch Centroid của nền tảng đã bám đuổi tỷ lệ tín hiệu phân bổ dân số tự nhiên của gã khổng lồ Facebook.

---

## Bước 5: Chuyển đổi thành Báo cáo Học thuật (Drafting Scientific Paper)
- **Văn bản đầu ra:** `draft_scientific_paper.md`
- **Mô tả thao tác:**
  Chèn kết cấu, biểu đồ thống kê, tóm tắt kết quả thành một bài soạn thảo chuẩn văn phong khoa học chứa trọn các phần tử: Abstract, Methodology, Discussion, Cross-validation và Conclusion. Sẵn sàng cho việc công bố lý thuyết và tích hợp Gravity Models.
