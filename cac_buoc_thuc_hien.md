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

## Bước 2: Thử nghiệm đa mô hình Không gian tại Tổng diện (Macro-scale)
- **Mã nguồn áp dụng:** `compare_dist.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Tập hợp các hàm phân phối để đối chiếu độ bao phủ: Truncated Lévy Flight (TLF), Exponential (Mũ), Lognormal, Gamma, và Shifted Power-Law.
  2. So sánh các mô hình bằng hệ số R2, AIC, BIC, KS-Test, Likelihood Ratio
  3. Kết luận mô hình phù hợp nhất với dữ liệu của các zone
---

## Bước 3: Validation chéo cùng Big-Data của Facebook Mobility
- **Mã nguồn áp dụng:** `compare_fb_gt.py`
- **Tập kết quả:** `fb_vs_gt_merged.csv` và ảnh trích xuất
- **Mô tả thao tác:**
  1. Gán nhãn các phân khu nhỏ `ORIGIN_SUBZONE` sang Quận rộng `district_id` thông qua ánh xạ đối chiếu.
  2. Chuẩn hoá nhóm cự ly của thuật toán nội bộ sang format Facebook (chuỗi `" (0, 1) "` km tránh bị lệch cột pandas do dấu phẩy, `[1, 10)`, `[10, 100)` và `100+` km).
  3. Cấp quận sát nhập bảng tính xác suất nội bộ ($P_{gt}$) và xuất ra đối chiếu dọc với tỷ lệ ping từ trạm Facebook ($P_{fb}$).
  4. Hai kết quả bám sát nhau ở mốc MAE, MRS

---

## Bước 4: Tổng hợp Văn bản Báo cáo Học thuật (Drafting Scientific Paper)
- **Văn bản đầu ra:** `draft_scientific_paper.md`
- **Mô tả thao tác:**
  Tổng hòa cấu trúc hệ lập luận (Multi-scale modeling). Đưa ra thông điệp kết luận: **Lognormal Distribution vĩ đại cho Vi Mô** & **Shifted Power-Law tối ưu hóa cho Vĩ Mô** thay vì chỉ cắm ghép TLF lạc mốt. Xây dựng dàn bài khoa học (Abstract, Methodology, Discussion, Cross-validation) củng cố vững nền để nghiên cứu sau này ráp mã thành công Gravity Models tại Đảo Quốc.
