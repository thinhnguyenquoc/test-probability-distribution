# Nhật ký Kỹ thuật: Quy trình Phân tích và Đối chiếu Mô hình Dịch chuyển Không gian Toàn Diện

Tài liệu này tổng hợp lại tuần tự toàn bộ các bước thao tác kỹ thuật, tính toán dữ liệu không gian định tính, và thiết lập mô hình từ giai đoạn thô đến mốc báo cáo hàn lâm cuối cùng. Mạch tài liệu được điều chỉnh hệ thống hóa đồng bộ với bài luân văn nghiên cứu.

---

## Bước 1: Tiền xử lý dữ liệu Ma trận chuyến đi và Chuẩn hóa Không gian
- **Mã nguồn áp dụng:** `calc_euclidean.py` (Mới)
- **Tập kết quả:** `zone_euclid_distances.csv`
- **Mô tả thao tác:**
  1. Sử dụng thư viện `geopandas` nạp tệp bản đồ số `sub_zone/data_sgp_subzone.shp`. Bãi bỏ hệ phẳng phi logic kinh/vĩ độ, tập bản đồ được ánh xạ dời về **EPSG:3414 (SVY21 - Hệ chuẩn riêng của Singapore)**.
  2. Bóc tách tọa độ trục (X, Y) bằng `mét` cho tĩnh điểm phân khu (Centroids).
  3. Hoàn tất tổ hợp chéo, xuất bản tập 104.329 cặp Khoảng cách Euclid (quy đổi km) phẳng giữa mọi Zone để làm lõi nền tảng cho mọi tính toán không gian về sau, thay thế công thức Haversine thô ban đầu.

---

## Bước 2: Thử nghiệm đa mô hình Không gian tại các Zone cấp vi mô (Micro-scale)
- **Mã nguồn áp dụng:** `compare_distribution_formular.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Tập hợp các hàm phân phối để đối chiếu độ bao phủ: Truncated Lévy Flight (TLF), Exponential (Mũ), Lognormal, Gamma, và Shifted Power-Law.
  2. Đo lường xếp hạng các mô hình bằng chỉ số R2, AIC, BIC, KS-Test, Likelihood Ratio.
  3. Lưu kết quả đánh giá số liệu diện rộng cho từng zone vào file `zone_distribution_metrics.csv`.
  4. Trích xuất thông tin luận điểm mô hình phù hợp nhất với dữ liệu lưu lượng đỉnh cục bộ ở vùng cụm nội cư dân.
  5. Xuất kết quả thống kê thành biểu đồ tròn/cột phân loại mô hình `zone_distribution_metrics.png`.
  6. Xuất đồ thị đối chiếu KS-Test giữa 2 mô hình đầu bảng (SPL và Lognormal) tại `zone_distribution_metrics_best.png`.

---

## Bước 3: Thử nghiệm đa mô hình Không gian tại các Cụm Quận (Macro-scale)
- **Mã nguồn áp dụng:** `compare_distribution_formular_district.py`
- **Tài liệu tham chiếu:** `cac_cong_thuc_phan_phoi.md`
- **Mô tả thao tác:**
  1. Tổng hợp dữ liệu định tuyến OD từ 303 cụm zones thành 5 Cụm Quận Vĩ mô (Districts).
  2. Khởi chạy song song 5 hàm phân phối cơ bản: TLF, Exponential, Lognormal, Gamma, SPL.
  3. Tính toán R2, AIC, BIC, KS-Test, Likelihood Ratio để quan sát sự suy yếu của yếu tố phân mảnh Peak và sự lên ngôi của yếu tố Đuôi dài.
  4. Ghi chép dữ liệu sai số vào file `district_distribution_metrics.csv`.
  5. Chỉ định mô hình Shifted Power-Law do lược bỏ thành công tham số ngắt đuôi vô tri dư thừa.
  6. Xuất biểu đồ bao phủ khu vực `district_distribution_metrics.png`.
  7. Xuất biểu đồ đối trọng Lognormal và SPL `district_distribution_metrics_best.png`.

---

## Bước 4: Validation chứng thực mức độ lệch giữa Shifted Power-Law và Facebook Mobility
- **Mã nguồn áp dụng:** `compare_fb_pl.py`
- **Tập kết quả:** `fb_vs_pl.csv` và ảnh trích xuất
- **Mô tả thao tác:**
  1. Quy chuẩn nhóm cự ly của thuật toán nội bộ sang format đồng bộ với Facebook (`(0, 1)`, `[1, 10)`, `[10, 100)` và `100+` km).
  2. Sử dụng tham số SPL đã nội suy thành công để sinh ra lượng Xác suất mô phỏng quan sát nghịch đảo nhân tạo.
  3. Đối chiếu khối lượng quan sát mô phỏng này với sóng Ping thực tế từ trạm Facebook Mobility qua 5 độ đo: Wasserstein Distance (EMD), MAE, RMSE, Kullback-Leibler Divergence, và Chi-squared test.
  4. Lưu số liệu khoảng cách sai số EMD siêu thấp vào tệp `fb_vs_pl.csv`.
  5. Xuất cảnh quan chỉ số bằng hình `fb_vs_pl.png`.
  6. Vẽ biểu đồ Bar 3 chiều đối chiếu phân mảnh (Facebook xanh dương vs Dữ liệu gốc xanh lá vs SPL đỏ) tại `fb_vs_pl_best.png`.

---

## Bước 5: Phân tích tính Chặt chẽ của Tham số (Uncertainty Analysis) thông qua Bootstrapping
- **Mã nguồn áp dụng:** `uncertainty_analysis.py`
- **Tập kết quả:** `spl_parameter_uncertainty.csv` và `spl_parameter_uncertainty.png`
- **Mô tả thao tác:**
  1. Hạn chế Overfitting thông qua việc mô phỏng lấy mẫu lại Đa thức (Multinomial Resampling Bootstrap) giả lập lặp 200 vòng độc lập cho mỗi điểm Quận.
  2. Thu thập ngân hàng dữ liệu các biến nội suy nội bộ và tính toán Khoảng tin cậy hội tụ 95% (95% Confidence Interval) nhắm trọng tâm vào hệ số kháng cự rơi tự do $\beta$.
  3. Sinh biểu đồ ma trận Boxplot dạng trục rải rác nhằm chứng thực độ co dãn biên độ vô cùng nhỏ gọn của hệ mô hình.

---

## Bước 6: Cố định Biểu đồ hàm phân phối Cuối cùng và Đoạt lấy Công thức Thực nghiệm
- **Mã nguồn áp dụng:** `plot_distribution_function.py`
- **Tập kết quả:** `distribution_function.png`
- **Mô tả thao tác:**
  1. Trích xuất khoảng chặn Confidence Interval từ hệ Bootstrapping để mô tả quỹ đạo $\beta$ thực nghiệm ($1.95 \le \beta \le 4.04$).
  2. Tổ chức vẽ biểu đồ đường Hàm phân phối Không gian (Space Distribution Graph) ở hệ trục tọa độ Log-Log đặc thù. 
  3. Điểm nhấn là các rải hạt scatter (Bin Data) thể hiện mật độ dữ liệu Gốc đính kèm đường kẻ liền mạch màu đỏ tương ứng cho hàm kỳ vọng của lý thuyết SPL.
  4. Sinh file ảnh `distribution_function.png` làm bằng chứng thuyết phục thị giác cao nhất lưu vết và trích dẫn cuối văn bản.

---

## Bước 7: Biên soạn Bản Báo cáo Khoa học Tổng kết (Drafting Scientific Paper)
- **Văn bản đầu ra:** `draft_scientific_paper.md`
- **Mô tả thao tác:**
  Biên soạn hệ sinh thái kết quả dưới giọng văn Hàn lâm - Học thuật khách quan (Academic Tone). Trình diễn tuần tự từng lập luận: Sự phù hợp của Lognormal tại vùng quy mô hẹp, tính linh động và chính xác của Shifted Power Law ở dải Macro. Phản biện và lật đổ sự dư thừa biến số của TLF truyền thống tại Super Micro-City như Singapore. Lồng ghép bằng chứng hình ảnh. Ấn định phương trình thực nghiệm cuối. Nền tảng này mở đường đi tới các chặng Gravity Model.
