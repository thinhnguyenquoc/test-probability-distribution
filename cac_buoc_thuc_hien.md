# Nhật ký Kỹ thuật: Quy trình Phân tích và Đối chiếu Mô hình Dịch chuyển Không gian Toàn Diện

Tài liệu này tổng hợp lại tuần tự toàn bộ các bước thao tác kỹ thuật, tính toán dữ liệu không gian định tính, và thiết lập mô hình từ giai đoạn thô đến mốc báo cáo hàn lâm cuối cùng.

---

## Bước 1: Tiền xử lý dữ liệu Ma trận chuyến đi và Chuẩn hóa Không gian
- **Mã nguồn áp dụng:** `calc_euclidean.py` (Mới)
- **Tập kết quả:** `zone_euclid_distances.csv`
- **Mô tả thao tác:**
  1. Sử dụng thư viện `geopandas` nạp tệp bản đồ số `sub_zone/data_sgp_subzone.shp`. Thay vì giữ hệ phi logic kinh/vĩ độ, tập bản đồ được ánh xạ dời về **EPSG:3414 (SVY21 - Hệ chuẩn riêng của Singapore)**.
  2. Bóc tách tọa độ trục (X, Y) bằng `mét` cho 323 tâm phân khu (Centroids).
  3. Hoàn tất tổ hợp chéo, xuất bản thành công ~104.329 cặp Khoảng cách Euclid (quy đổi km) phẳng giữa mọi Zone để làm lõi nền tảng cho mọi tính toán không gian về sau, thay thế công thức Haversine thô ban đầu.

---

## Bước 2: Thử nghiệm đa mô hình Không gian tại các zone (Micro-scale)
- **Mã nguồn áp dụng:** `compare_distribution_formular.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Tập hợp các hàm phân phối để đối chiếu độ bao phủ: Truncated Lévy Flight (TLF), Exponential (Mũ), Lognormal, Gamma, và Shifted Power-Law.
  2. So sánh các mô hình bằng hệ số R2, AIC, BIC, KS-Test, Likelihood Ratio
  3. Lưu kết quả đánh giá cho từng zone vào file `zone_distribution_metrics.csv`
  4. Kết luận mô hình phù hợp nhất với dữ liệu của các zone
  5. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình `zone_distribution_metrics.png`
  6. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình có kết quả BIC giống nhau, cần kiểm tra thêm R_2 và KS-Test để chọn mô hình phù hợp nhất `zone_distribution_metrics_best.png`
---

## Bước 3: Thử nghiệm đa mô hình Không gian tại các district (Macro-scale)
- **Mã nguồn áp dụng:** `compare_distribution_formular_district.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Gộp dữ liệu từ các zone thành các district
  2. Tập hợp các hàm phân phối để đối chiếu độ bao phủ: Truncated Lévy Flight (TLF), Exponential (Mũ), Lognormal, Gamma, và Shifted Power-Law.
  3. So sánh các mô hình bằng hệ số R2, AIC, BIC, KS-Test, Likelihood Ratio
  4. Lưu kết quả đánh giá cho từng district vào file `district_distribution_metrics.csv`
  5. Kết luận mô hình phù hợp nhất với dữ liệu của các district
  6. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình `district_distribution_metrics.png`
  7. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình có kết quả BIC giống nhau, cần kiểm tra thêm R_2 và KS-Test để chọn mô hình phù hợp nhất `district_distribution_metrics_best.png`
---

## Bước 4: kiểm tra độ sai lệch giữa phân phối Shifted Power-Law và dữ liệu Facebook Mobility
- **Mã nguồn áp dụng:** `compare_fb_pl.py`
- **Tập kết quả:** `fb_vs_pl.csv` và ảnh trích xuất
- **Mô tả thao tác:**
  1. Gán nhãn các phân khu nhỏ `ORIGIN_SUBZONE` sang Quận rộng `district_id` thông qua ánh xạ đối chiếu.
  2. Chuẩn hoá nhóm cự ly của thuật toán nội bộ sang format Facebook (chuỗi `" (0, 1) "` km tránh bị lệch cột pandas do dấu phẩy, `[1, 10)`, `[10, 100)` và `100+` km).
  3. Dùng phân phối Shifted Power-Law để sinh dữ liệu quan sát.
  4. Só sánh dữ liệu quan sát với dữ liệu Facebook Mobility theo độ đo: Wasserstein Distance (EMD), Mean Absolute Error (MAE), Root Mean Square Error (RMSE), Relative Entropy (Kullback-Leibler Divergence), và Chi-squared test.
  5. Lưu kết quả đánh giá cho từng district vào file `fb_vs_pl.csv`
  6. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình `fb_vs_pl.png`
  7. Xuất kết quả thồng kê dưới dạng biểu đồ so sánh các mô hình có kết quả BIC giống nhau, cần kiểm tra thêm R_2 và KS-Test để chọn mô hình phù hợp nhất `fb_vs_pl_best.png`
---

## Bước 5: Tổng hợp Văn bản Báo cáo Học thuật (Drafting Scientific Paper)
- **Văn bản đầu ra:** `draft_scientific_paper.md`
- **Mô tả thao tác:**
  Miêu tả các bước đã thực hiện, thêm hình biểu đồ, rút ra nhận xét có thể tìm được phân phối phù hợp với dữ liệu của các zone và district. Kết luận phân phối đuôi dài Levy flight chưa phù hợp trong các mô hình siêu độ thị nhỏ. Trường hợp Singapore mô hình LSP chiếm ưu thế thông qua gianx lược phần đuôi dài.
