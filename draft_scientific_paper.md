---
title: "Nghiên cứu Tính tương thích của Mô hình Di chuyển Không gian Đa Tỷ lệ Khảo sát tại Đảo quốc Singapore"
author: "Báo cáo Nghiên cứu Kỹ thuật"
date: "Tháng 4, 2026"
---

# Nghiên cứu Tính tương thích của Mô hình Di chuyển Không gian Đa Tỷ lệ: Khảo sát tại Đảo quốc Singapore

## 1. Tóm tắt (Abstract)
Hiểu rõ các hình thái dịch chuyển của con người thông qua các hàm phân phối xác suất là một phần quan trọng của công tác quy hoạch giao thông và kinh tế đô thị. Bài viết này trình bày kết quả phân tích hệ thống phân phối khoảng cách lưu lượng chuyến đi (OD) trên phạm vi giới hạn về không gian và có mật độ dân số cao như Singapore. Thay vì áp dụng một hàm thống nhất, nghiên cứu tiến hành khảo sát sự tương thích của 5 mô hình toán học cơ sở ở hai tỷ lệ: Cấp vi mô (Subzone) và Cấp vĩ mô (District). Dựa trên các tiêu chuẩn kiểm định phân phối như Akaike/Bayesian Information Criterion (AIC/BIC), Kolmogorov-Smirnov Test (KS-Test), và chỉ số Wasserstein Distance (đối chiếu với dữ liệu Facebook Mobility), kết quả cho thấy những hạn chế của mô hình Truncated Lévy Flight truyền thống ở quy mô phân tích này, đồng thời xác nhận tính hiệu quả của Shifted Power-Law cho quy hoạch cự ly liên quận và sự phù hợp của phân phối Lognormal cho cự ly ngắn ở cấp cơ sở.

---

## 2. Giới thiệu và Mục tiêu nghiên cứu (Introduction)
Trong nhiều thập kỷ qua, mô hình Truncated Lévy Flight (TLF) với đặc tính hàm cơ sở mô tả các bước nhảy dài ngắt quãng đã được sử dụng như một mô hình tiêu chuẩn để phát triển Gravity Model đối với các khu vực địa lý có diện tích rộng (như Hoa Kỳ hoặc Châu Âu). 
Tuy nhiên, tại môi trường đô thị nén (Micro Super-city) bao bọc bởi địa hình hẹp như Singapore, việc áp dụng nguyên mẫu này bộc lộ các vấn đề cần đánh giá lại:
1. Liệu có tồn tại một phân phối duy nhất phù hợp với mọi quy mô chức năng của đô thị?
2. Sự cần thiết của tham số cắt cụt hàm suy giảm đuôi ($\kappa$) trong mô hình TLF tại không gian giới hạn diện tích như thế nào?
Nghiên cứu này được thực hiện nhằm mục đích lượng hóa và trả lời cho các vấn đề trên.

---

## 3. Khung phân tích và Phương pháp Kỹ thuật (Methodology)

### 3.1. Dữ liệu Cơ sở (Ground Truth Data) và Phương pháp Thống kê
Nghiên cứu sử dụng tập dữ liệu lượng truy vết di chuyển cá nhân (Ground Truth Data) giữa các phân khu hành chính. Nhằm mục đích loại bỏ các dao động ngẫu nhiên và nhiễu sóng chu kỳ trong ngày hoặc do thời tiết, lưu lượng chuyến đi (Trip Counts) được tổng hợp và tính tổng theo cơ sở tuần (Weekly Aggregated Statistics). Phương pháp gộp mẫu này cho phép ổn định hóa cấu trúc di chuyển thống kê và phản ánh hình thái lưu thông vĩ mô cốt lõi.

Tổng thể dữ liệu bao gồm điểm đếm chuyến đi từ 303 Subzones trải khắp 5 Quận trung tâm (Districts). Hệ tọa độ không gian được quy hoạch và đồng bộ hóa về tiêu chuẩn EPSG:3414 nhằm đảm bảo tính toán định lượng chính xác tham số Khoảng cách Euclid (bề mặt phẳng).

### 3.2. Thuật toán Tối ưu hóa Tham số (Model Parameter Fitting)
Sử dụng phương pháp tối ưu hóa phi tuyến tính *Levenberg-Marquardt*, nghiên cứu tiến hành quá trình nội suy đường cong (Curve fitting) để thiết lập và đánh giá mức độ tương thích đối chiếu giữa 5 mô hình phân phối chuẩn:
- *Lognormal*
- *Gamma*
- *Exponential*
- *Shifted Power-Law (SPL)*
- *Truncated Lévy Flight (TLF)*

Các thước đo định lượng bao gồm: Hệ số xác định $R^2$, Kiểm định Kolmogorov-Smirnov (KS-Test), Khoảng cách dịch chuyển Wasserstein (EMD), và Tiêu chuẩn thông tin Bayes (BIC) hỗ trợ phân loại mức độ tin cậy đồng thời phạt các mô hình sử dụng quá nhiều biến số dư thừa.

---

## 4. Phân tích Kết quả (Results & Evaluation)

### 4.1. Khảo sát Mô hình Phân phối tại Cấp Vi mô - Zone (Micro-scale)
Trong thử nghiệm 5 mô hình phân phối trên các vùng Subzone, kết quả ghi nhận sự phân tán về mức độ tương thích như sau:
![So sánh các phân bổ](zone_distribution_metrics.png)

***Đánh giá Tổng quan 5 Mô hình trên Hệ chuẩn BIC (Dựa trên Hình 1):***
Biểu đồ phân mảnh minh họa tỷ lệ các mô hình tối ưu thông qua tiêu chuẩn khắt khe BIC. Nghiên cứu ghi nhận sự tương đương giá trị giữa **Shifted Power-Law (28.1%)** và **Lognormal (28.1%)** với cùng 85 phân khu (zones) đáp ứng tiêu chuẩn. Ngược lại, mô hình phức hóa **Truncated Lévy Flight (TLF)** ghi nhận tỷ lệ tương thích thấp nhất (3.3%). Thực tiễn thuật toán BIC áp dụng khung hình phạt cho các hàm chứa nhiều tham số cấu thành ($k=4$) mà không đạt được sự thay đổi tích cực đáng kể đối với tổng thể phương sai. Điều này phản ánh tính không cần thiết của việc vận đồ tham số cắt cụt $\kappa$ thuộc tính TLF trên không gian ngắn tại các cụm dân cư.

Để kiểm định mức độ bao trùm cấu trúc phân phối, đối sánh tỷ số KS-Test tiếp tục được thực hiện:
![So sánh Trực tiếp SPL và Lognormal](zone_distribution_metrics_best.png)

***Nhận xét:*** 
Phân phối Lognormal thể hiện năng lực giải thích tỷ lệ phương sai $R^2$ ở ngưỡng cao (`0.82`), thích ứng với sự tập trung đỉnh lưu lượng đi bộ trong bán kính 1-2km ở cấp độ vi mô. Tuy nhiên, đánh giá chỉ số kháng chênh lệch cấu trúc ngẫu nhiên (KS-Test) khẳng định Shifted Power-Law cung cấp mức độ ổn định dài hạn ưu việt hơn tính chung toàn thể hình thái nón phân phối.

### 4.2. Khảo sát Mô hình Phân phối tại Cấp Cụm Quận - District (Macro-scale)
Khi tiến hành gộp dữ liệu không gian từ 303 Subzones lên cấp 5 Quận trung tâm, cấu trúc dữ liệu OD chuyển dịch hiển thị đặc tính phân phối đuôi dài (Heavy-tail), và tính phi tuyến nội đô tại tâm cụm dần được cân bằng bởi dòng di chuyển vĩ mô.

Sự chuyển dịch quy mô dẫn tới thay đổi trong mức tương thích của Lognormal do sự thiếu hụt đặc tính đỉnh trung tâm. Đồng thời, kết quả **Kiểm định tỷ số hợp lý (Likelihood Ratio Test)** đã quy định rằng sự xuất hiện của biến số hãm đuôi theo hàm mũ ($\kappa$ - Exponential Cutoff) của Truncated Lévy Flight tại dải trên 8km không cấu thành sự cải thiện mô hình có ý nghĩa thống kê. Phân phối **Shifted Power-Law** thể hiện độ ưu việt cao qua việc tối giản các tham số dư thừa, duy trì năng lực biểu diễn thông số hiệu quả.

![Đồ thị District Coverage](district_distribution_metrics.png)
![Đồ thị Lognormal vs SPL Cấp Quận](district_distribution_metrics_best.png)

***Nhận xét:*** 
Ứng dụng tương đồng ở cả 5 Cụm Quận, mô hình SPL ghi nhận khoảng cách phi tham số KS-Test thấp và ổn định, chứng tỏ ưu thế về khả năng bao trùm thực nghiệm so với các mô hình theo chuẩn Bayesian Information Criterion.

### 4.3. Xác thực Dữ liệu qua Thông tin Mạng Viễn thông (Facebook Mobility Validation)
Để đánh giá tác động thực tiễn ứng dụng đường cong phân bổ, nghiên cứu thực hiện quy trình mô phỏng ngược xác suất phân phối kỳ vọng SPL (P_pl) và đối chiếu phân tích sai số với lượng dữ liệu Mobility độc lập (được ghi nhận bởi sóng lưu lượng trạm gốc di động Facebook).

Dữ liệu được tổ chức theo các khoảng tham chiếu: `<1km, 1-10km, 10-100km`. Khoảng cách lượng hóa EMD (Wasserstein Distance) giới hạn trong khoảng rất thấp: **0.05 đến 0.11**. Chỉ số tin cậy RMSE và MAE nằm ở mức độ bám sát nhất định.

![Sự bắt sóng giữa SPL và Facebook Mobility](fb_vs_pl_best.png)

***Nhận xét:*** 
Biểu đồ tương quan (P_fb, P_gt và mô phỏng P_pl) thể hiện tính thống nhất cao giữa ba trường dữ liệu. Cấu trúc mô phỏng khối lượng lưu chuyển liên vùng tuyến từ 1 đến 10km của SPL duy trì mức độ định tuyến tiệm cận cao với số đo lượng truyền thông từ nguồn Facebook Mobility.

### 4.4. Đánh giá tính Chặt chẽ của Tham số Định hình Không gian (Uncertainty Analysis)
Nhằm kiểm chứng tính ổn định của đường cong giới hạn Shifted Power-Law và loại trừ khả năng vượt khớp cục bộ (overfitting), cơ chế lấy mẫu giả lập tái tổ hợp tương ứng **(Multinomial Resampling Bootstrap)** chạy trên 200 vòng lặp độc lập đã được thiết lập ứng dụng quy trình tại 5 Quận thực nghiệm. Sự phân tích độ nhạy được giới hạn trọng tâm ở tham số $\beta$ - biến đại diện diễn tả lực ma sát kháng cự không gian.

![Biểu đồ Boxplot Phân tán Bootstrap](spl_parameter_uncertainty.png)

***Nhận xét:*** 
Khảo sát Khoảng tin cậy (95% Confidence Interval) đối với tham số $\beta$ cho thấy các giá trị hội tụ tiệm cận tuyến tính chặt chẽ. Đồ thị Boxplot xác nhận hệ số mức phân tán biến thiên thấp. Không ghi nhận các dị số ngoại lai cực đoan làm biến đổi cấu trúc hạ tầng thống kê, qua đó đảm bảo tính khả tín về tham số mà phân phối SPL cung cấp.

---

## 5. Kết luận khoa học (Conclusion & Discussion)
Nghiên cứu củng cố góc nhìn định lượng trong việc áp dụng mô hình phân phối đối với biến động lưu lượng tại môi trường không gian hạn chế (diện tích thu hẹp, quy mô dân cư nén) tại Singapore. Từ các mô thức vận hành tính toán chuyên sâu cho tới đối chiếu độ xác thực thực tiễn, có thể rút ra:

1. **Hiệu suất mô hình đa biến bị phân rã:** Cơ sở sử dụng mô hình có tham số hàm ngắt cụt đuôi như Truncated Lévy Flight bộc lộ nhiều điểm hạn chế, chịu hình phạt thông tin mạnh theo độ dư thừa tham số khi áp dụng vào các Super Micro-cities. 
2. **Sự tương thích của mô hình Shifted Power-Law (SPL):** Nhờ cơ chế hoạt động lũy thừa đơn giản hóa tham số ngắt định quy (exponential break $\kappa$), phân phối SPL đã bảo chứng tính hiệu quả, tối thiểu hóa độ lệch dữ liệu lý thuyết theo mô hình (EMD, KS-Test) và xác nhận mức tối ưu toàn diện tại tỷ lệ quản lý không gian Vĩ mô (Districts). 
3. **Phân phối Lognormal tại cấp độ Micro:** Tuy SPL có tính tổng quát cao, việc mô phỏng hiện tượng di chuyển nội tại tích tụ đỉnh trong vòng bán kính ngắn (<2km) cấp phường (Subzones) vẫn cho phép ứng dụng hệ mô hình Lognormal dựa trên đặc tính cung cấp vùng thể tích đếm dồn $R^2$ ưu việt. 

![Đường cong Phân phối SPL Thực tế](distribution_function.png)

### 5.1. Công thức Đại diện Shifted Power-Law Thực nghiệm
Dựa trên kết quả tối ưu hóa từ thuật toán Levenberg-Marquardt và xác thực bền vững qua Bootstrapping, phương trình nền tảng toán học đặc tả lưu lượng phân phối xác suất di chuyển $P(r)$ theo khoảng cách vật lý $r$ tại cấp Quận (Macro-scale) của Singapore được xác lập như sau:

$$ P(r) = C (r + r_0)^{-\beta} $$

Trong đó, các kích thước tham số thực nghiệm (Empirical Parameters) được ghi nhận trong khoảng giới hạn tin cậy 95% (95% CI) như sau:
- **$\beta$ (Tham số kháng cự không gian - Gravity Friction):** Dao động thực nghiệm từ **$1.95 \le \beta \le 4.04$** (tùy thuộc vào mật độ kết nối khu vực không gian của từng Quận, ví dụ SGP.3 mang đặc tính $\approx 1.95$ mở rộng giao thương, SGP.5 đạt mốc $\approx 4.04$ với sức hút hướng tâm cục bộ mạnh).
- **$r_0$ (Thông số dịch chuyển khoảng cách lỗi):** Dao động thực nghiệm bảo chứng từ **$4.2 \le r_0 \le 14.1$** km (Hệ số trễ do đặc tính đô thị nén).
- **$C$ (Hệ số chuẩn hóa phân phối):** Biến thiên độc lập phục vụ mục tiêu cố định ranh giới tích phân $\int P(r)dr = 1$.

Kết quả này là biểu tượng định lượng chính thức được khuyến nghị thay thế cơ chế của TLF gốc tại quốc gia nén này.

---

## 6. Áp dụng phân phối để ước lượng thông số cho mô hình gravity
