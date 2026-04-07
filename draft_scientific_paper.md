---
title: "Đánh giá các Mô hình Phân phối Không gian Di chuyển tại Kịch bản Đô thị Mật độ cao: Nghiên cứu trường hợp tại Singapore"
author: "Báo cáo Nghiên cứu Kỹ thuật Tích hợp"
date: "Tháng 4, 2026"
---

# Đánh giá các Mô hình Phân phối Không gian Di chuyển tại Kịch bản Đô thị Mật độ cao: Nghiên cứu trường hợp tại Singapore

## 1. Tóm tắt (Abstract)
Bài viết này nghiên cứu đặc tính di chuyển của con người trong môi trường đô thị nhỏ, mật độ cực cao (đảo quốc Singapore) thông qua biểu đồ phân kỳ hành trình OD (Origin-Destination). Bằng việc sử dụng hệ trục tọa độ mét chuẩn nội địa SVY21 (EPSG:3414) để trích xuất khoảng cách Euclid mặt phẳng, nghiên cứu đã khớp dữ liệu định tính thực tế thay vì tọa độ hình trụ. Các mô hình lý thuyết kinh điển được kiểm thử bao gồm: Truncated Lévy Flight (TLF), Shifted Power-Law, Exponential, Gamma và Lognormal. Thông qua đánh giá đa tỷ lệ (Multi-scale) từ vi mô đến vĩ mô kết hợp hệ liệt kê trừng phạt thông tin khắt khe (AIC, BIC, KS-Test, Likelihood Ratio), kết quả chỉ ra đặc tính lưỡng cực: Hàm **Lognormal** biểu hiện hiệu suất vượt trội để mô tả "khoảng cách ưa thích" nội bộ hẹp, trong khi **Shifted Power-Law** hoàn hảo đáp ứng mạng lưới vĩ mô toàn đảo do sự dư thừa tham số của TLF. Kết quả đánh giá cấp Quận (Cross-validation) cùng Facebook Mobility đạt độ tương đồng CPC lên tới ~85% (MAE xấp xỉ 0.07). Cuối cùng, một mạng giả lập tự động cơ sở dựa trên Radiation Model (Mô hình bức xạ) được thiết lập, mang về điểm nền tảng hệ thống dự đoán dòng giao thông CPC 42.44%.

---

## 2. Giới thiệu (Introduction)
Phân tích mô hình dịch chuyển không gian (spatial mobility modelling) là công nghệ lõi để tối ưu hoá cơ sở định tuyến hạ tầng và quy hoạch chuỗi cung ứng. Tuy Truncated Lévy Flight (TLF) thường là mô hình trọng điểm để biểu diễn dải không gian rã mũ "đuôi cắt cực đoan" của con người ở diện tích quốc gia rộng lớn, nhưng trên lãnh thổ hải đảo hẹp (dưới 50km) như Singapore, dạng cắt này trở nên suy biến. Nghiên cứu tập trung rà soát hệ phương trình từ các khung tiêu chí cơ bản ($R^2$) tới mức độ khắc nghiệt (AIC/BIC) nhằm tìm ra một thiết lập cốt lõi chuẩn nhất, đồng thời đối thử lại với hai bộ đo kiểm viễn thông thực chứng.

---

## 3. Dữ liệu và Phương pháp luận (Methodology)

### 3.1. Dữ liệu Đầu vào và Ma trận Mạng lưới Euclid
- **Khung phân tách Không gian:** Shapefile 323 cụm tâm phân khu (Centroids) được quy chuyển hoàn toàn về không gian chiếu chuẩn **Singapore SVY21 (EPSG:3414)**, cung cấp khoảng cách Euclid mặt phẳng siêu tuyến tính thay vì Haversine bề cong trái đất.
- **Tiêu chuẩn Thiết lập Giả định Viễn thông (Facebook Mobility):** Khung xác suất di chuyển của tập số được đúc xuống các chuẩn nhận diện khoảng cách công nghệ viễn thông `[(0, 1), [1, 10), [10, 100), 100+]` (km). Cập nhật độ chặt chẽ bằng cách bổ sung thêm sai số bình phương trung bình **(MRS/RMSE)** ngoài MAE.

### 3.2. Cấu trúc Mô hình và Công cụ Đo lường
Các tham số uốn nắn thực nghiệm được khớp qua tối ưu hóa phi tuyến học *Levenberg-Marquardt* cho:
1. **Truncated Lévy Flight (TLF)**: $P(\Delta r) \sim (\Delta r + \Delta r_0)^{-\beta} \exp(-\Delta r/\kappa)$
2. **Shifted Power-Law (SPL)**: $P(\Delta r) \sim (\Delta r + \Delta r_0)^{-\beta}$
3. **Exponential**: $P(\Delta r) \sim \exp(-\Delta r/\lambda)$
4. **Gamma**: $P(\Delta r) \sim (\Delta r)^{\alpha-1} \exp(-\Delta r/\lambda)$
5. **Lognormal**: $P(\Delta r) \sim \frac{1}{\Delta r} \exp \left( - \frac{(\ln \Delta r - \mu)^2}{2\sigma^2} \right)$

Các nhóm chỉ số đo kiểm chuyên gia để loại bỏ bất thường bao gồm: Hệ số thanh lọc cấu trúc thừa Akaike/Bayesian (AIC/BIC), Hệ số KS-Test đo lỗi tích luỹ lớn nhất (D), và Phép thử Giả thuyết Tương quan (Likelihood Ratio).

---

## 4. Kết quả và Đánh giá (Results & Evaluation)

### 4.1. Sự thoái trào của Truncated Lévy Flight theo quy mô không gian
Bằng nội suy riêng biệt cho mạng tinh thể hơn 300 điểm phân khu khởi hành (Subzones gốc), kết quả phơi bày: Cấp độ vi mô kích hoạt giới hạn cắt cụt phân rã mũ (Exponential cut-off) tự nhiên ở trên **70% phân khu (216 vùng)** với trung vị ngắt kết nối tại mốc $\kappa = 8.05$ km. Con người chạm đến ranh giới biển lập tức đánh võng lượng tương tác về 0. Tuy nhiên, khi hợp nhất dữ liệu ở cấp độ Toàn Đảo Lớn (Vĩ Mô), tính cắt cụt bị xoá sổ bởi hiệu ứng đám đông ($\kappa \to \infty$). Đường cong gãy ngược về lại chuẩn Power-law thông thường.

### 4.2. Cấp Vi mô (Micro-scale) - Khung Lognormal chiếm tuyệt đại đa số
Sàng lọc quy mô cấp phố độc lập cho ra cái tên áp đảo nhất là **Lognormal**, hoàn thiện điểm số tại **69.4% diện tích phân dải** (209 zone), để Gamma xếp nhì ở mức 26.6%. Ở cự ly sống ngắn, hành vi con người xoay quanh một số điểm lõi phục vụ (chợ, trung tâm sinh hoạt) trong cự ly "ưa thích xê dịch" mốc 2-5km. Hàm Lognormal lột tả xuất sắc đỉnh sưng gù hình chóp (peak) cho sở thích này, thứ mà SPL hay Exponential dốc đứng hoàn toàn mù mờ.

### 4.3. Cấp Vĩ mô (Macro-scale) - Bằng chứng KS-Test và BIC chọn Lũy thừa Di dịch
Trên dải nhìn rộng vĩ mô (Big Data) tạo ra đường dài phân nhánh rớt lơi lả (Heavy-tail). Theo số liệu kiểm thử ngặt nghèo nhất:
- Máy giải toán cho thấy mô hình **Shifted Power-Law (SPL)** chiến thắng tuyệt đối trên đường dài với điểm **BIC** cực thấp (vượt Exponential và Gamma) và khoảng rèn ma trận **KS Test đỉnh cao (0.0386)**.
- Điểm chốt chặn: Kiểm định độ tương thích vi phân **Likelihood Ratio (LR Test)** dội vào hai mô hình cạnh tranh nhau SPL và TLF trả về mốc p-value khá cao **0.596** (> 0.05). Chứng tỏ về mặt toán lượng, việc lắp thêm tham số mũ đuôi ngắt $\kappa$ của TLF vào môi trường Singapore quy mô ngang là phung phí và yếu kém so với sự chặt chẽ tinh gọn của Power-law bậc 3 tham số. 

### 4.4. Chứng thực Giao thoa (Cross-validation) qua mạng Viễn thông Facebook
Quy nạp ma trận giao điểm (Zone) thành ma trận chùm hành chính (District), sự giống nhau giữa xác suất dự đoán $P_{gt}$ và xác suất thiết bị ping thực tế $P_{fb}$ đem lại độ thành công tuyệt hảo:
- Quận **Tây (SGP.5)**: Sai số MAE cực thấp 0.0736 | MRS (RMSE) = **0.0901** | Bắt sóng dòng chảy **CPC = 85.28%**
- Quận **Đông Bắc (SGP.4)**: MAE = 0.0793 | MRS = **0.0970** | Tỷ lệ giao tuyến **CPC = 84.15%**
- Quận **Đông (SGP.2)**: MAE = 0.0845 | MRS = **0.0996** | Tỷ lệ giao tuyến **CPC = 83.11%**
- Quận **Bắc (SGP.3)**: MAE = 0.0821 | MRS = **0.1050** | Tỷ lệ giao tuyến **CPC = 83.58%**
- Quận **Trung Tâm (SGP.1)**: MAE = 0.1086 | MRS = **0.1318** | Tỷ lệ giao tuyến **CPC = 78.29%** (Dịch chuyển nhẹ tại chùm diện tích bị phân cắt cực nhỏ dưới 1km của lõi CBD).

### 4.5. Triển khai cấu trúc Giao thông Nền qua Mô hình Bức Xạ (Radiation Proxy Model)
Với đặc thù khối lượng số lớn của 104,329 cặp khoảng cách đo tay tiêu chuẩn, báo cáo lập trình trực tiếp bộ mô phỏng quy hoạch Bức Xạ cơ bản nhằm chứng thực dòng tương tác O-D. Đối lưu khởi xướng sử dụng Trip Count như biến số giả định khối dân cư ($m_i, n_j$). Hệ mạng lập tức kích hoạt, đạt ngưỡng tương giao lượng commuters thực tế với **CPC Baseline là 42.44%**. So với mốc 30% chưa tinh chỉnh cấu hình của khu vực đô thị thì cấu hình lưới Singapore sở hữu đặc tính thu hút việc làm/dịch vụ xuất sắc nhất.

---

## 5. Kết luận (Conclusion)
Dữ kiện xác đáng này phế truất thói quen dùng Truncated Lévy Flight truyền thống cho môi trường đảo hình thái nhỏ cứng. Phân cực toán học là cần thiết để lập trình cho mô phỏng di chuyển mới: **Dùng hàm Lognormal Distribution cho máy dò tìm cấp cơ sở bán kính nội khu**, và **kiến thiết hàm Shifted Power-Law cho lập kế luân chuyển ngoại biên Big Data Toàn Cảnh**. Cùng với đó, độ tương quan đồng dạng đáng kinh ngạc (~85% CPC) với lưới ma trận định vị gốc do tập đoàn Facebook phân rã càng làm sáng tỏ mức độ phản ánh tin cậy của lưới Centroid nội suy. Kết quả của nghiên cứu đã hoàn tất nền tảng khung mã vững chãi, sẵn sàng ráp nối chuyên sâu cùng hệ biến đổi việc làm (Land Use, Jobs) của O-D Radiation Models tạo nên tính chính xác vượt bậc cho mạng lưới giao thông tương lai ở đảo quốc Sư Tử.
